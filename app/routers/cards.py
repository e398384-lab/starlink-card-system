from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import StarLinkCard, Transaction, Merchant
from app.schemas import (
    StarLinkCardIssue, StarLinkCardRedeem,
    StarLinkCardResponse, TransactionResponse, TransactionCreate,
    MessageResponse
)
from app.auth import get_current_user, get_current_merchant_user
from uuid import UUID
import uuid
from datetime import datetime, timedelta

router = APIRouter(prefix="/cards", tags=["星鏈卡交易"])

def generate_card_number() -> str:
    """生成唯一的星鏈卡卡號"""
    return f"SLK-{uuid.uuid4().hex[:16].upper()}"

@router.post("/issue", response_model=StarLinkCardResponse)
async def issue_card(
    card_data: StarLinkCardIssue,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_merchant_user)
):
    """發行星鏈卡"""
    # 驗證商家存在
    result = await db.execute(
        select(Merchant).where(Merchant.id == card_data.merchant_id)
    )
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    if merchant.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant is not active"
        )
    
    # 檢查商家餘額是否足夠
    if merchant.balance < card_data.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient merchant balance"
        )
    
    # 扣除商家餘額
    merchant.balance -= card_data.value
    
    # 生成卡片
    card_number = generate_card_number()
    expires_at = card_data.expires_at or (datetime.utcnow() + timedelta(days=365))
    
    new_card = StarLinkCard(
        id=str(uuid.uuid4()),
        card_number=card_number,
        merchant_id=card_data.merchant_id,
        value=card_data.value,
        balance=card_data.value,
        status="active",
        expires_at=expires_at
    )
    
    db.add(new_card)
    await db.commit()
    await db.refresh(new_card)
    
    return new_card

@router.post("/redeem", response_model=TransactionResponse)
async def redeem_card(
    redeem_data: StarLinkCardRedeem,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """兌換星鏈卡"""
    # 查找卡片
    result = await db.execute(
        select(StarLinkCard).where(StarLinkCard.card_number == redeem_data.card_number)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    if card.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card is not active"
        )
    
    if card.balance < redeem_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient card balance"
        )
    
    # 檢查過期
    if card.expires_at and card.expires_at < datetime.utcnow():
        card.status = "expired"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card has expired"
        )
    
    # 驗證消費商家
    result = await db.execute(
        select(Merchant).where(Merchant.id == redeem_data.merchant_id)
    )
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    if merchant.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant is not active"
        )
    
    # 計算交易費 (4%)
    commission = redeem_data.amount * merchant.commission_rate
    net_amount = redeem_data.amount - commission
    
    # 更新卡片餘額
    card.balance -= redeem_data.amount
    if card.balance == 0:
        card.status = "redeemed"
    
    # 更新商家餘額
    merchant.balance += net_amount
    
    # 記錄交易
    transaction = Transaction(
        id=str(uuid.uuid4()),
        card_id=card.id,
        merchant_id=redeem_data.merchant_id,
        user_id=current_user.id,
        amount=redeem_data.amount,
        commission=commission,
        net_amount=net_amount,
        transaction_type="purchase",
        status="completed",
        description="星鏈卡兌換"
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return transaction

@router.get("/my-cards", response_model=list[StarLinkCardResponse])
async def get_my_cards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取當前用戶的星鏈卡"""
    result = await db.execute(
        select(StarLinkCard).where(StarLinkCard.holder_user_id == current_user.id)
    )
    cards = result.scalars().all()
    
    return cards

@router.get("/history", response_model=list[TransactionResponse])
async def get_transaction_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取交易歷史"""
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.created_at.desc())
    )
    transactions = result.scalars().all()
    
    return transactions

@router.get("/merchant/history", response_model=list[TransactionResponse])
async def get_merchant_transaction_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_merchant_user)
):
    """獲取商家的交易歷史"""
    result = await db.execute(
        select(Transaction).where(Transaction.merchant_id == current_user.merchant_id).order_by(Transaction.created_at.desc())
    )
    transactions = result.scalars().all()
    
    return transactions

@router.get("/{card_id}", response_model=StarLinkCardResponse)
async def get_card_info(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取卡片資訊"""
    try:
        card_uuid = UUID(card_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid card ID format"
        )
    
    result = await db.execute(
        select(StarLinkCard).where(StarLinkCard.id == card_uuid)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    return card

@router.post("/assign", response_model=MessageResponse)
async def assign_card_to_user(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """將卡片分配給當前用戶"""
    try:
        card_uuid = UUID(card_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid card ID format"
        )
    
    result = await db.execute(
        select(StarLinkCard).where(StarLinkCard.id == card_uuid)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    if card.holder_user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card already assigned to a user"
        )
    
    card.holder_user_id = current_user.id
    await db.commit()
    
    return {"message": "Card successfully assigned to you", "success": True}
