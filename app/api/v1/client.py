"""
Client API - Customer operations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from pydantic import BaseModel

from app.models.base import Card, Employee
from app.services.card_service import CardService
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/client", tags=["client"])

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
class ClientCardsResponse(BaseModel):
    total: int
    cards: List[dict]

class TransferInitiateRequest(BaseModel):
    serial_number: str
    from_phone: str
    to_phone: str

class TransferAcceptRequest(BaseModel):
    transfer_token: str
    to_phone: str

# API Endpoints

@router.get("/{phone}/cards", response_model=ClientCardsResponse)
def get_client_cards(phone: str, db: Session = Depends(get_db)):
    """Get all cards owned by customer phone"""
    from app.models.base import CardDetail, CardStatus
    
    # Find card details where customer_phone matches
    card_details = db.query(CardDetail).filter(CardDetail.customer_phone == phone).all()
    
    cards = []
    for detail in card_details:
        card = detail.card
        if card and card.status in [CardStatus.CLAIMED, CardStatus.TRANSFER_INIT, CardStatus.TRANSFER_ACCEPTED]:
            cards.append({
                "serial_number": card.serial_number,
                "title": card.title,
                "face_value": card.face_value,
                "status": card.status.value,
                "issuer": card.issuer.name if card.issuer else None,
                "created_at": card.created_at.isoformat() if card.created_at else None,
                "claimed_at": card.claimed_at.isoformat() if card.claimed_at else None
            })
    
    return {
        "total": len(cards),
        "cards": cards
    }

@router.post("/redeem")
def redeem_card_at_merchant(serial_number: str, customer_phone: str, 
                           employee_id: str = None, db: Session = Depends(get_db)):
    """Customer redeems card at A-merchant"""
    try:
        from app.models.base import CardStatus
        
        card_service = CardService(db)
        
        # Get card
        card = db.query(Card).filter(Card.serial_number == serial_number).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Verify customer owns the card
        detail = db.query(CardDetail).filter_by(card_id=card.id).first()
        if not detail or detail.customer_phone != customer_phone:
            raise HTTPException(status_code=403, detail="Not authorized to redeem this card")
        
        # Verify card is in redeemable status
        if card.status not in [CardStatus.CLAIMED, CardStatus.TRANSFER_ACCEPTED]:
            raise HTTPException(status_code=400, detail=f"Card is {card.status.value}, cannot be redeemed")
        
        # Redeem the card
        employee_uuid = uuid.UUID(employee_id) if employee_id else None
        redeemed_card = card_service.redeem_card(
            serial_number=serial_number,
            redeemer_phone=customer_phone,
            employee_id=employee_uuid
        )
        
        if not redeemed_card:
            raise HTTPException(status_code=500, detail="Failed to redeem card")
        
        # Record A-merchant's 98% balance payable
        financial_service = FinancialService(db)
        financial_service.record_balance_payable(
            card=redeemed_card,
            merchant=card.issuer,
            transaction_type=TransactionType.BALANCE_PAYABLE_A
        )
        
        return {
            "success": True,
            "card": {
                "serial_number": redeemed_card.serial_number,
                "title": redeemed_card.title,
                "face_value": redeemed_card.face_value
            },
            "message": f"Card redeemed successfully at {card.issuer.name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer/init")
def initiate_transfer(request: TransferInitiateRequest, db: Session = Depends(get_db)):
    """Customer initiates P2P transfer"""
    try:
        card_service = CardService(db)
        
        transfer_token = card_service.init_transfer(
            serial_number=request.serial_number,
            from_customer_phone=request.from_phone,
            to_customer_phone=request.to_phone
        )
        
        if not transfer_token:
            raise HTTPException(status_code=404, detail="Card not found or not in claimable status")
        
        return {
            "success": True,
            "transfer_token": transfer_token,
            "expires_in": "48 hours",
            "message": f"Transfer initiated. Share token {transfer_token} with recipient"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer/accept")
def accept_transfer(request: TransferAcceptRequest, db: Session = Depends(get_db)):
    """ Recipient accepts incoming P2P transfer """
    try:
        card_service = CardService(db)
        
        transferred_card = card_service.accept_transfer(
            transfer_token=request.transfer_token,
            to_customer_phone=request.to_phone
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
            "message": f"Transfer completed. Card now owned by {request.to_phone}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cards/{serial_number}/verify")
def verify_card(serial_number: str, db: Session = Depends(get_db)):
    """Verify card is valid and available"""
    from app.models.base import CardStatus
    
    card = db.query(Card).filter(Card.serial_number == serial_number).first()
    
    if not card:
        return {
            "valid": False,
            "message": "Card not found"
        }
    
    if card.status == CardStatus.CREATED:
        return {
            "valid": True,
            "status": card.status.value,
            "message": "Card available for allocation to B-merchant"
        }
    elif card.status == CardStatus.ALLOCATED:
        return {
            "valid": True,
            "status": card.status.value,
            "message": "Card available for customer to claim",
            "distributor": card.current_holder.name if card.current_holder else None
        }
    elif card.status == CardStatus.CLAIMED:
        return {
            "valid": True,
            "status": card.status.value,
            "message": "Card claimed by customer, ready for redemption or transfer"
        }
    elif card.status == CardStatus.REDEEMED:
        return {
            "valid": False,
            "status": card.status.value,
            "message": "Card already redeemed",
            "redeemed_at": card.redeemed_at.isoformat() if card.redeemed_at else None
        }
    else:
        return {
            "valid": False,
            "status": card.status.value,
            "message": f"Card status: {card.status.value}"
        }