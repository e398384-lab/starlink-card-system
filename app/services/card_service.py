"""
Card Service - Handles card lifecycle management
"""

from sqlalchemy.orm import Session
from app.models.base import Card, CardDetail, CardLog, Merchant, Employee, CardStatus
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict
import json

def log_card_transition(db: Session, card: Card, action: str, from_status: CardStatus, 
                       to_status: CardStatus, merchant_id: uuid.UUID = None, 
                       employee_id: uuid.UUID = None, details: dict = None):
    """Log card state transition for audit trail"""
    log = CardLog(
        card_id=card.id,
        merchant_id=merchant_id,
        employee_id=employee_id,
        action=action,
        from_status=from_status,
        to_status=to_status,
        details=details or {}
    )
    db.add(log)
    return log

class CardService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_serial_number(self) -> str:
        """Generate unique serial number"""
        prefix = "SLC"  # StarLink Card
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = str(uuid.uuid4().hex)[:8].upper()
        return f"{prefix}-{date_part}-{random_part}"
    
    def issue_cards(self, issuer_id: uuid.UUID, title: str, face_value: float, 
                   quantity: int, metadata: dict = None) -> List[Card]:
        """System issues cards to A-class merchant (創建 → ALLOCATED)"""
        cards = []
        for _ in range(quantity):
            card = Card(
                serial_number=self.generate_serial_number(),
                issuer_id=issuer_id,
                current_holder_id=issuer_id,
                title=title,
                face_value=face_value,
                status=CardStatus.CREATED,
                metadata=metadata or {}
            )
            self.db.add(card)
            cards.append(card)
            
            # Log the creation
            log_card_transition(
                self.db, card, "card_created", None, CardStatus.CREATED,
                merchant_id=issuer_id,
                details={"face_value": face_value}
            )
        
        self.db.flush()  # Get IDs for CardDetail creation
        
        # Create CardDetail records
        for card in cards:
            detail = CardDetail(card_id=card.id)
            self.db.add(detail)
        
        self.db.commit()
        return cards
    
    def allocate_to_distributor(self, card_ids: List[uuid.UUID], distributor_id: uuid.UUID, 
                               employee_id: uuid.UUID = None) -> List[Card]:
        """A-merchant allocates cards to B-merchant (創建 → ALLOCATED)"""
        cards = []
        
        for card_id in card_ids:
            card = self.db.query(Card).filter_by(id=card_id).first()
            if not card:
                continue
            
            if card.status != CardStatus.CREATED:
                raise ValueError(f"Card {card.serial_number} is not in CREATED status")
            
            old_status = card.status
            card.status = CardStatus.ALLOCATED
            card.current_holder_id = distributor_id
            card.allocated_at = datetime.utcnow()
            
            # Update card detail
            detail = self.db.query(CardDetail).filter_by(card_id=card.id).first()
            if detail:
                detail.holder_employee_id = employee_id
            
            # Log transition
            log_card_transition(
                self.db, card, "allocated_to_distributor", old_status, CardStatus.ALLOCATED,
                merchant_id=distributor_id,
                employee_id=employee_id,
                details={"from_holder": str(card.issuer_id)}
            )
            
            cards.append(card)
        
        self.db.commit()
        return cards
    
    def claim_card(self, serial_number: str, customer_phone: str) -> Optional[Card]:
        """Customer claims card from B-merchant (ALLOCATED → CLAIMED)"""
        card = self.db.query(Card).filter_by(serial_number=serial_number).first()
        if not card:
            return None
        
        if card.status != CardStatus.ALLOCATED:
            raise ValueError(f"Card {serial_number} is not available for claiming")
        
        old_status = card.status
        card.status = CardStatus.CLAIMED
        card.claimed_at = datetime.utcnow()
        
        # Update card detail with customer info
        detail = self.db.query(CardDetail).filter_by(card_id=card.id).first()
        if detail:
            detail.customer_phone = customer_phone
        
        # Log transition
        log_card_transition(
            self.db, card, "card_claimed", old_status, CardStatus.CLAIMED,
            merchant_id=card.current_holder_id,
            details={"customer_phone": customer_phone}
        )
        
        self.db.commit()
        return card
    
    def init_transfer(self, serial_number: str, from_customer_phone: str, 
                     to_customer_phone: str) -> Optional[str]:
        """Customer initiates P2P transfer (CLAIMED → TRANSFER_INIT)"""
        card = self.db.query(Card).filter_by(serial_number=serial_number).first()
        if not card:
            return None
        
        if card.status != CardStatus.CLAIMED:
            raise ValueError(f"Card {serial_number} is not in CLAIMED status")
        
        detail = self.db.query(CardDetail).filter_by(card_id=card.id).first()
        if not detail or detail.customer_phone != from_customer_phone:
            raise ValueError("Not authorized to transfer this card")
        
        old_status = card.status
        card.status = CardStatus.TRANSFER_INIT
        
        # Generate transfer token
        transfer_token = str(uuid.uuid4().hex)[:12].upper()
        detail.transfer_token = transfer_token
        detail.transfer_expires_at = datetime.utcnow() + timedelta(hours=48)
        
        # Log transition
        log_card_transition(
            self.db, card, "transfer_initiated", old_status, CardStatus.TRANSFER_INIT,
            details={"from_phone": from_customer_phone, "to_phone": to_customer_phone}
        )
        
        self.db.commit()
        return transfer_token
    
    def accept_transfer(self, transfer_token: str, to_customer_phone: str) -> Optional[Card]:
        """Recipient accepts P2P transfer (TRANSFER_INIT → TRANSFER_ACCEPTED)"""
        detail = self.db.query(CardDetail).filter_by(transfer_token=transfer_token).first()
        if not detail:
            return None
        
        card = self.db.query(Card).filter_by(id=detail.card_id).first()
        if not card or card.status != CardStatus.TRANSFER_INIT:
            raise ValueError("Invalid transfer")
        
        if detail.transfer_expires_at and detail.transfer_expires_at < datetime.utcnow():
            # Transfer expired, revert status
            old_status = card.status
            card.status = CardStatus.CLAIMED
            detail.transfer_token = None
            detail.transfer_expires_at = None
            
            log_card_transition(
                self.db, card, "transfer_expired", old_status, CardStatus.CLAIMED
            )
            self.db.commit()
            raise ValueError("Transfer has expired")
        
        old_status = card.status
        card.status = CardStatus.TRANSFER_ACCEPTED
        detail.customer_phone = to_customer_phone
        detail.transfer_token = None
        detail.transfer_expires_at = None
        
        log_card_transition(
            self.db, card, "transfer_accepted", old_status, CardStatus.TRANSFER_ACCEPTED,
            details={"new_owner_phone": to_customer_phone}
        )
        
        # After transfer completes, return to CLAIMED status for redemption
        card.status = CardStatus.CLAIMED
        log_card_transition(
            self.db, card, "transfer_completed", CardStatus.TRANSFER_ACCEPTED, CardStatus.CLAIMED
        )
        
        self.db.commit()
        return card
    
    def redeem_card(self, serial_number: str, redeemer_phone: str, 
                   employee_id: uuid.UUID = None) -> Optional[Card]:
        """A-merchant redeems card (CLAIMED → REDEEMED)"""
        card = self.db.query(Card).filter_by(serial_number=serial_number).first()
        if not card:
            return None
        
        if card.status not in [CardStatus.CLAIMED, CardStatus.TRANSFER_ACCEPTED]:
            raise ValueError(f"Card {serial_number} cannot be redeemed in current status")
        
        detail = self.db.query(CardDetail).filter_by(card_id=card.id).first()
        if detail and detail.customer_phone != redeemer_phone:
            raise ValueError("Invalid redeemer")
        
        old_status = card.status
        card.status = CardStatus.REDEEMED
        card.redeemed_at = datetime.utcnow()
        
        if detail:
            detail.holder_employee_id = employee_id
        
        log_card_transition(
            self.db, card, "card_redeemed", old_status, CardStatus.REDEEMED,
            merchant_id=card.issuer_id,
            employee_id=employee_id,
            details={"redeemer_phone": redeemer_phone}
        )
        
        self.db.commit()
        return card