from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.base import Merchant
from app.models.base import get_db
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/merchant", tags=["merchant"])

# Pydantic models (same as admin for simplicity, could be different)
class MerchantCreate(BaseModel):
    name: str
    type: str  # Should be 'B' for merchant portal? but we keep generic
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

@router.get("/profile/{merchant_id}", response_model=MerchantResponse)
def get_merchant_profile(merchant_id: str, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

@router.put("/profile/{merchant_id}", response_model=MerchantResponse)
def update_merchant_profile(merchant_id: str, merchant: MerchantCreate, db: Session = Depends(get_db)):
    db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not db_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    for key, value in merchant.dict().items():
        setattr(db_merchant, key, value)
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

# For A merchants: issue cards
@router.post("/cards/issue")
def issue_card_from_merchant(merchant_id: str, face_value: float, valid_days: int = 365, db: Session = Depends(get_db)):
    from app.services.card_service import CardService
    card_service = CardService(db)
    card = card_service.issue_card(
        issued_by_merchant_id=merchant_id,
        face_value=face_value,
        valid_days=valid_days
    )
    return {"card_id": card.id, "card_number": card.card_number}

# For B merchants: allocate cards (they receive allocation)
@router.post("/cards/allocate")
def allocate_card_to_merchant(merchant_id: str, card_id: str, db: Session = Depends(get_db)):
    from app.services.card_service import CardService
    card_service = CardService(db)
    card = card_service.allocate_card(
        card_id=card_id,
        allocated_to_merchant_id=merchant_id
    )
    return {"status": "allocated", "card_id": card.id}

# For B merchants: redeem cards
@router.post("/cards/redeem/{card_id}")
def redeem_card(merchant_id: str, card_id: str, db: Session = Depends(get_db)):
    from app.services.card_service import CardService
    card_service = CardService(db)
    # Verify the card is allocated to this merchant
    card = card_service.get_card(card_id)
    if card.allocated_to_merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Card not allocated to this merchant")
    card = card_service.redeem_card(card_id)
    return {"status": "redeemed", "card_id": card.id}

# For B merchants: list their allocated cards
@router.get("/cards/allocated", response_model=List[dict])
def get_allocated_cards(merchant_id: str, db: Session = Depends(get_db)):
    from app.services.card_service import CardService
    card_service = CardService(db)
    cards = card_service.list_cards(merchant_id=merchant_id)
    return [
        {
            "id": c.id,
            "card_number": c.card_number,
            "face_value": c.face_value,
            "state": c.state.value,
            "issued_at": c.issued_at,
            "expires_at": c.expires_at
        }
        for c in cards
    ]