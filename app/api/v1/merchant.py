"""
Merchant API - B-class merchant operations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from pydantic import BaseModel

from app.models.base import Card, Merchant, CardStatus, MerchantRole
from app.services.card_service import CardService
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/merchant", tags=["merchant"])

def get_db():
    from sqlalchemy.orm import sessionmaker
    from app.models.base import get_db_engine
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class AllocateCardRequest(BaseModel):
    serial_numbers: List[str]
    distributor_id: str
    employee_id: str = None

class DistributeCardRequest(BaseModel):
    serial_number: str
    customer_phone: str

class RedeemCardRequest(BaseModel):
    serial_number: str
    customer_phone: str
    employee_id: str = None

class InventoryResponse(BaseModel):
    total: int
    by_status: dict

# API Endpoints

@router.post("/allocate")
def receive_card_allocation(request: AllocateCardRequest, db: Session = Depends(get_db)):
    """B-merchant receives card allocation from A-issuer"""
    try:
        # Verify distributor exists and is B class
        distributor = db.query(Merchant).filter_by(id=uuid.UUID(request.distributor_id)).first()
        if not distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        
        if distributor.role != MerchantRole.B_DISTRIBUTOR:
            raise HTTPException(status_code=400, detail="Merchant is not a B-class distributor")
        
        card_service = CardService(db)
        
        # Find cards by serial numbers
        cards = db.query(Card).filter(Card.serial_number.in_(request.serial_numbers)).all()
        if len(cards) != len(request.serial_numbers):
            raise HTTPException(status_code=400, detail="One or more cards not found")
        
        # Allocate cards
        employee_uuid = uuid.UUID(request.employee_id) if request.employee_id else None
        allocated_cards = card_service.allocate_to_distributor(
            card_ids=[c.id for c in cards],
            distributor_id=distributor.id,
            employee_id=employee_uuid
        )
        
        # Record 2% deposits from distributor
        financial_service = FinancialService(db)
        for card in allocated_cards:
            if card.status == CardStatus.ALLOCATED:
                financial_service.record_deposit(card, distributor, TransactionType.DEPOSIT_B)
        
        return {
            "success": True,
            "allocated": len(allocated_cards),
            "cards": [{
                "serial_number": card.serial_number,
                "title": card.title,
                "face_value": card.face_value
            } for card in allocated_cards]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distribute")
def distribute_card_to_customer(request: DistributeCardRequest, db: Session = Depends(get_db)):
    """B-merchant distributes card to customer"""
    try:
        card_service = CardService(db)
        financial_service = FinancialService(db)
        
        claimed_card = card_service.claim_card(
            serial_number=request.serial_number,
            customer_phone=request.customer_phone
        )
        
        if not claimed_card:
            raise HTTPException(status_code=404, detail="Card not found or already claimed")
        
        # This is the trigger for recording B's 98% balance payable
        # The financial transaction was already recorded in claim_card process
        
        return {
            "success": True,
            "card": {
                "serial_number": claimed_card.serial_number,
                "title": claimed_card.title,
                "face_value": claimed_card.face_value,
                "status": claimed_card.status.value
            },
            "transfer_token": None,  # This is for direct distribution, no token needed
            "customer_phone": request.customer_phone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cards/{serial_number}/transfer/init")
def initiate_transfer(serial_number: str, from_phone: str, to_phone: str, db: Session = Depends(get_db)):
    """Initiate P2P transfer from one customer to another"""
    try:
        card_service = CardService(db)
        
        transfer_token = card_service.init_transfer(
            serial_number=serial_number,
            from_customer_phone=from_phone,
            to_customer_phone=to_phone
        )
        
        if not transfer_token:
            raise HTTPException(status_code=404, detail="Card not found or not in claimable status")
        
        return {
            "success": True,
            "transfer_token": transfer_token,
            "expires_in": "48 hours",
            "from_phone": from_phone,
            "to_phone": to_phone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cards/transfer/accept")
def accept_transfer(transfer_token: str, to_phone: str, db: Session = Depends(get_db)):
    """Accept incoming P2P transfer"""
    try:
        card_service = CardService(db)
        
        transferred_card = card_service.accept_transfer(
            transfer_token=transfer_token,
            to_customer_phone=to_phone
        )
        
        if not transferred_card:
            raise HTTPException(status_code=404, detail="Invalid or expired transfer token")
        
        return {
            "success": True,
            "card": {
                "serial_number": transferred_card.serial_number,
                "title": transferred_card.title,
                "face_value": transferred_card.face_value
            },
            "new_owner_phone": to_phone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{merchant_id}/inventory")
def get_merchant_inventory(merchant_id: str, db: Session = Depends(get_db)):
    """Get merchant's card inventory"""
    merchant_uuid = uuid.UUID(merchant_id)
    
    # Cards currently held by this merchant
    held_cards = db.query(Card).filter(Card.current_holder_id == merchant_uuid).all()
    
    # Group by status
    by_status = {}
    for card in held_cards:
        status = card.status.value
        if status not in by_status:
            by_status[status] = []
        by_status[status].append({
            "serial_number": card.serial_number,
            "title": card.title,
            "face_value": card.face_value
        })
    
    total = len(held_cards)
    pending_count = len(by_status.get("CREATED", []))
    allocated_count = len(by_status.get("ALLOCATED", []))
    claimed_count = len(by_status.get("CLAIMED", []))
    redeemed_count = len(by_status.get("REDEEMED", []))
    
    return {
        "merchant_id": merchant_id,
        "total_cards": total,
        "by_status": {status: len(cards) for status, cards in by_status.items()},
        "details": by_status
    }

@router.get("/cards/{serial_number}/status")
def check_card_status(serial_number: str, db: Session = Depends(get_db)):
    """Check card status"""
    card = db.query(Card).filter(Card.serial_number == serial_number).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return {
        "serial_number": card.serial_number,
        "title": card.title,
        "face_value": card.face_value,
        "status": card.status.value,
        "issuer": card.issuer.name if card.issuer else None,
        "current_holder": card.current_holder.name if card.current_holder else None,
        "created_at": card.created_at.isoformat() if card.created_at else None,
        "allocated_at": card.allocated_at.isoformat() if card.allocated_at else None,
        "claimed_at": card.claimed_at.isoformat() if card.claimed_at else None,
        "redeemed_at": card.redeemed_at.isoformat() if card.redeemed_at else None
    }