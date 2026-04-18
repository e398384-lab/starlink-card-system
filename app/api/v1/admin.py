from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.base import Merchant, StarLinkCard, FinancialTransaction, CardStateEnum, TransactionTypeEnum
from app.services.card_service import CardService
from app.services.financial_service import FinancialService
from app.models.base import get_db
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])

# Pydantic models
class MerchantCreate(BaseModel):
    name: str
    type: str  # 'A' or 'B'
    contact_person: str = None
    phone: str = None
    email: str = None
    address: str = None
    website: str = None

class MerchantResponse(BaseModel):
    id: str
    name: str
    type: str
    contact_person: str = None
    phone: str = None
    email: str = None
    address: str = None
    website: str = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CardIssueRequest(BaseModel):
    issued_by_merchant_id: str
    face_value: float
    valid_days: int = 365

class CardResponse(BaseModel):
    id: str
    card_number: str
    face_value: float
    issued_by_merchant_id: str
    allocated_to_merchant_id: str = None
    state: str
    issued_at: datetime
    allocated_at: datetime = None
    redeemed_at: datetime = None
    settled_at: datetime = None
    expires_at: datetime = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FinancialTransactionResponse(BaseModel):
    id: str
    card_id: str
    transaction_type: str
    amount: float
    from_merchant_id: str = None
    to_merchant_id: str = None
    description: str = None
    transaction_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/merchants", response_model=MerchantResponse)
def create_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    db_merchant = Merchant(**merchant.dict())
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

@router.get("/merchants", response_model=List[MerchantResponse])
def list_merchants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    merchants = db.query(Merchant).offset(skip).limit(limit).all()
    return merchants

@router.get("/merchants/{merchant_id}", response_model=MerchantResponse)
def get_merchant(merchant_id: str, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

@router.post("/cards/issue", response_model=CardResponse)
def issue_card(request: CardIssueRequest, db: Session = Depends(get_db)):
    card_service = CardService(db)
    card = card_service.issue_card(
        issued_by_merchant_id=request.issued_by_merchant_id,
        face_value=request.face_value,
        valid_days=request.valid_days
    )
    return card

@router.get("/cards", response_model=List[CardResponse])
def list_cards(merchant_id: str = None, state: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    card_service = CardService(db)
    state_enum = CardStateEnum(state) if state else None
    cards = card_service.list_cards(merchant_id=merchant_id, state=state_enum, limit=limit, offset=skip)
    return cards

@router.get("/cards/{card_id}", response_model=CardResponse)
def get_card(card_id: str, db: Session = Depends(get_db)):
    card_service = CardService(db)
    card = card_service.get_card(card_id)
    return card

@router.get("/financial/transactions", response_model=List[FinancialTransactionResponse])
def list_financial_transactions(merchant_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    financial_service = FinancialService(db)
    # For simplicity, we'll query directly; could add method to service
    query = db.query(FinancialTransaction)
    if merchant_id:
        query = query.filter(
            (FinancialTransaction.from_merchant_id == merchant_id) |
            (FinancialTransaction.to_merchant_id == merchant_id)
        )
    transactions = query.offset(skip).limit(limit).all()
    return transactions

@router.get("/financial/summary")
def get_financial_summary(merchant_id: str = None, db: Session = Depends(get_db)):
    financial_service = FinancialService(db)
    summary = financial_service.get_financial_summary(merchant_id=merchant_id)
    return summary