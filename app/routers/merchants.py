from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Merchant, MerchantType, MerchantStatus, User
from app.schemas import (
 MerchantCreate, MerchantUpdate, MerchantResponse,
 MessageResponse, UserResponse
)
from app.auth import get_current_user, get_current_merchant_user
from uuid import UUID
import uuid

router = APIRouter(prefix="/merchants", tags=["商家管理"])

@router.post("/register", response_model=MerchantResponse)
async def register_merchant(
    merchant_data: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """註冊新商家"""
    # 檢查郵件是否已存在
    result = await db.execute(
        select(Merchant).where(Merchant.email == merchant_data.email)
    )
    existing_merchant = result.scalar_one_or_none()
    
    if existing_merchant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered for a merchant"
        )
    
    # 創建新商家
    new_merchant = Merchant(
        id=str(uuid.uuid4()),
        name=merchant_data.name,
        email=merchant_data.email,
        phone=merchant_data.phone,
        merchant_type=merchant_data.merchant_type,
        status=MerchantStatus.PENDING,  # 預設待審核
        address=merchant_data.address,
        description=merchant_data.description,
        balance=0.0,
        commission_rate=0.04  # 4% 交易費
    )
    
    db.add(new_merchant)
    await db.commit()
    await db.refresh(new_merchant)
    
    return new_merchant

@router.get("/me", response_model=MerchantResponse)
async def get_current_merchant(
    current_user: User = Depends(get_current_merchant_user),
    db: AsyncSession = Depends(get_db)
):
    """獲取當前商家資訊"""
    result = await db.execute(
        select(Merchant).where(Merchant.id == current_user.merchant_id)
    )
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    return merchant

@router.put("/me", response_model=MerchantResponse)
async def update_current_merchant(
    merchant_data: MerchantUpdate,
    current_user: User = Depends(get_current_merchant_user),
    db: AsyncSession = Depends(get_db)
):
    """更新當前商家資訊"""
    result = await db.execute(
        select(Merchant).where(Merchant.id == current_user.merchant_id)
    )
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    # 更新欄位
    update_data = merchant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(merchant, field, value)
    
    await db.commit()
    await db.refresh(merchant)
    
    return merchant

@router.get("/list", response_model=list[MerchantResponse])
async def list_merchants(
    merchant_type: MerchantType = None,
    status: MerchantStatus = MerchantStatus.ACTIVE,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出所有商家（可篩選類型）"""
    query = select(Merchant).where(Merchant.status == status)
    
    if merchant_type:
        query = query.where(Merchant.merchant_type == merchant_type)
    
    result = await db.execute(query)
    merchants = result.scalars().all()
    
    return merchants

@router.get("/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取特定商家資訊"""
    try:
        merchant_uuid = UUID(merchant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid merchant ID format"
        )
    
    result = await db.execute(
        select(Merchant).where(Merchant.id == merchant_uuid)
    )
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    if merchant.status != MerchantStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant is not active"
        )
    
    return merchant

@router.post("/{merchant_id}/link", response_model=MessageResponse)
async def link_merchant_to_user(
    merchant_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """將商家連結到當前用戶"""
    try:
        merchant_uuid = UUID(merchant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid merchant ID format"
        )
    
    result = await db.execute(
        select(Merchant).where(Merchant.id == merchant_uuid)
    )
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    if merchant.status != MerchantStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant is not active"
        )
    
    current_user.merchant_id = merchant_uuid
    await db.commit()
    
    return {"message": "Successfully linked to merchant", "success": True}
