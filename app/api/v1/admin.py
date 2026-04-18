"""
Admin API - System management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from pydantic import BaseModel

from app.models.base import get_db_engine, create_tables
from app.models.base import Merchant, Employee, Card, CardStatus, MerchantRole
from app.services.card_service import CardService
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    from sqlalchemy.orm import sessionmaker
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class MerchantCreateRequest(BaseModel):
    name: str
    phone: str
    role: str  # "A_ISSUER" or "B_DISTRIBUTOR"
    max_employees: int = 5

class MerchantResponse(BaseModel):
    id: str
    name: str
    phone: str
    role: str
    max_employees: int
    created_at: str

class CardIssueRequest(BaseModel):
    issuer_id: str
    title: str
    face_value: float
    quantity: int

class CardResponse(BaseModel):
    id: str
    serial_number: str
    title: str
    face_value: float
    status: str
    issuer_id: str
    current_holder_id: Optional[str]
    created_at: str

# API Endpoints

@router.post("/merchants", response_model=MerchantResponse)
def create_merchant(merchant: MerchantCreateRequest, db: Session = Depends(get_db)):
    """Create a new merchant (A or B class)"""
    # Check if phone already exists
    existing = db.query(Merchant).filter(Merchant.phone == merchant.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    db_merchant = Merchant(
        name=merchant.name,
        phone=merchant.phone,
        role=MerchantRole[merchant.role],
        max_employees=merchant.max_employees
    )
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    
    return {
        "id": str(db_merchant.id),
        "name": db_merchant.name,
        "phone": db_merchant.phone,
        "role": db_merchant.role.value,
        "max_employees": db_merchant.max_employees,
        "created_at": db_merchant.created_at.isoformat()
    }

@router.get("/merchants", response_model=List[MerchantResponse])
def list_merchants(db: Session = Depends(get_db)):
    """List all merchants"""
    merchants = db.query(Merchant).all()
    return [{
        "id": str(m.id),
        "name": m.name,
        "phone": m.phone,
        "role": m.role.value,
        "max_employees": m.max_employees,
        "created_at": m.created_at.isoformat()
    } for m in merchants]

@router.post("/cards/issue", response_model=dict)
def issue_cards_to_merchant(request: CardIssueRequest, db: Session = Depends(get_db)):
    """Issue cards to A-class merchant"""
    try:
        card_service = CardService(db)
        cards = card_service.issue_cards(
            issuer_id=uuid.UUID(request.issuer_id),
            title=request.title,
            face_value=request.face_value,
            quantity=request.quantity
        )
        
        # Record financial transaction (2% deposit)
        financial_service = FinancialService(db)
        merchant = db.query(Merchant).filter_by(id=uuid.UUID(request.issuer_id)).first()
        
        for card in cards:
            financial_service.record_deposit(card, merchant, TransactionType.DEPOSIT_A)
        
        return {
            "success": True,
            "cards_issued": len(cards),
            "cards": [{
                "id": str(card.id),
                "serial_number": card.serial_number,
                "title": card.title,
                "face_value": card.face_value,
                "status": card.status.value
            } for card in cards],
            "total_face_value": request.face_value * request.quantity,
            "total_deposit_collected": request.face_value * request.quantity * 0.04  # 4% (2% from each side, but only 2% at issuance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchants/{merchant_id}/inventory")
def get_merchant_inventory(merchant_id: str, db: Session = Depends(get_db)):
    """View merchant's card inventory by status"""
    merchant_uuid = uuid.UUID(merchant_id)
    
    # Cards issued by this merchant
    issued = db.query(Card).filter(Card.issuer_id == merchant_uuid).all()
    
    # Cards currently held by this merchant
    held = db.query(Card).filter(Card.current_holder_id == merchant_uuid).all()
    
    # Group by status
    status_counts = {}
    for card in held:
        status = card.status.value
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    return {
        "merchant_id": merchant_id,
        "total_issued": len(issued),
        "total_held": len(held),
        "by_status": status_counts
    }

@router.get("/system/financial-summary")
def get_system_financial_summary(db: Session = Depends(get_db)):
    """Get system-wide financial summary"""
    financial_service = FinancialService(db)
    revenue = financial_service.calculate_platform_revenue()
    
    return {
        "total_platform_revenue": revenue["total_revenue"],
        "platform_holdings": revenue["platform_holdings"],
        "redeemed_cards": revenue["redeemed_cards"]
    }

@router.post("/init-db")
def initialize_database():
    """Initialize database tables"""
    try:
        create_tables()
        return {"success": True, "message": "Database tables created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: str

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }