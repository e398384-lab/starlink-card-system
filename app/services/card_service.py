from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.base import Merchant, StarLinkCard, FinancialTransaction, CardStateEnum, TransactionTypeEnum
import uuid
from datetime import datetime, timedelta

class CardService:
    def __init__(self, db: Session):
        self.db = db
    
    def issue_card(self, issued_by_merchant_id: str, face_value: float, valid_days: int = 365) -> StarLinkCard:
        """A商家發行星鏈卡"""
        # Validate merchant exists and is type A
        merchant = self.db.query(Merchant).filter(Merchant.id == issued_by_merchant_id).first()
        if not merchant:
            raise HTTPException(status_code=404, detail="Issuing merchant not found")
        if merchant.type != 'A':
            raise HTTPException(status_code=400, detail="Only A-type merchants can issue cards")
        
        # Generate unique card number
        card_number = f"SL{uuid.uuid4().hex[:12].upper()}"
        
        # Calculate expiry date
        expires_at = datetime.utcnow() + timedelta(days=valid_days)
        
        card = StarLinkCard(
            card_number=card_number,
            face_value=face_value,
            issued_by_merchant_id=issued_by_merchant_id,
            state=CardStateEnum.ISSUED,
            expires_at=expires_at
        )
        
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def allocate_card(self, card_id: str, allocated_to_merchant_id: str) -> StarLinkCard:
        """將卡片分配給B商家"""
        card = self.db.query(StarLinkCard).filter(StarLinkCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        if card.state != CardStateEnum.ISSUED:
            raise HTTPException(status_code=400, detail=f"Card cannot be allocated from state {card.state}")
        
        # Validate merchant exists and is type B
        merchant = self.db.query(Merchant).filter(Merchant.id == allocated_to_merchant_id).first()
        if not merchant:
            raise HTTPException(status_code=404, detail="Allocating merchant not found")
        if merchant.type != 'B':
            raise HTTPException(status_code=400, detail="Only B-type merchants can receive allocated cards")
        
        card.allocated_to_merchant_id = allocated_to_merchant_id
        card.state = CardStateEnum.ALLOCATED
        card.allocated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def redeem_card(self, card_id: str) -> StarLinkCard:
        """B商家兌換卡片（消費者使用）"""
        card = self.db.query(StarLinkCard).filter(StarLinkCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        if card.state != CardStateEnum.ALLOCATED:
            raise HTTPException(status_code=400, detail=f"Card cannot be redeemed from state {card.state}")
        
        card.state = CardStateEnum.REDEEMED
        card.redeemed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def settle_card(self, card_id: str) -> StarLinkCard:
        """平台結算卡片（付給A和B商家98%）"""
        card = self.db.query(StarLinkCard).filter(StarLinkCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        if card.state != CardStateEnum.REDEEMED:
            raise HTTPException(status_code=400, detail=f"Card cannot be settled from state {card.state}")
        
        card.state = CardStateEnum.SETTLED
        card.settled_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def cancel_card(self, card_id: str, reason: str = None) -> StarLinkCard:
        """取消卡片（任何階段）"""
        card = self.db.query(StarLinkCard).filter(StarLinkCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        if card.state in [CardStateEnum.SETTLED, CardStateEnum.EXPIRED]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel card in state {card.state}")
        
        card.state = CardStateEnum.CANCELLED
        if reason:
            # Could store reason in a separate field or description
            pass
        
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def get_card(self, card_id: str) -> StarLinkCard:
        """取得卡片資訊"""
        card = self.db.query(StarLinkCard).filter(StarLinkCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        return card
    
    def list_cards(self, merchant_id: str = None, state: CardStateEnum = None, limit: int = 100, offset: int = 0):
        """列出卡片（可過濾）"""
        query = self.db.query(StarLinkCard)
        
        if merchant_id:
            query = query.filter(
                (StarLinkCard.issued_by_merchant_id == merchant_id) |
                (StarLinkCard.allocated_to_merchant_id == merchant_id)
            )
        
        if state:
            query = query.filter(StarLinkCard.state == state)
        
        cards = query.offset(offset).limit(limit).all()
        return cards

class FinancialService:
    def __init__(self, db: Session):
        self.db = db
    
    def record_deposit_a(self, card_id: str, amount: float, from_merchant_id: str) -> FinancialTransaction:
        """記錄A商家付2%給平台"""
        transaction = FinancialTransaction(
            card_id=card_id,
            transaction_type=TransactionTypeEnum.DEPOSIT_A,
            amount=amount,
            from_merchant_id=from_merchant_id,
            to_merchant_id=None,  # 平台收款
            description=f"A merchant deposit 2% of card value"
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def record_deposit_b(self, card_id: str, amount: float, from_merchant_id: str) -> FinancialTransaction:
        """記錄B商家付2%給平台"""
        transaction = FinancialTransaction(
            card_id=card_id,
            transaction_type=TransactionTypeEnum.DEPOSIT_B,
            amount=amount,
            from_merchant_id=from_merchant_id,
            to_merchant_id=None,  # 平台收款
            description=f"B merchant deposit 2% of card value"
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def record_balance_payable_a(self, card_id: str, amount: float, to_merchant_id: str) -> FinancialTransaction:
        """記錄平台付98%給A商家"""
        transaction = FinancialTransaction(
            card_id=card_id,
            transaction_type=TransactionTypeEnum.BALANCE_PAYABLE_A,
            amount=amount,
            from_merchant_id=None,  # 平台付款
            to_merchant_id=to_merchant_id,
            description=f"Platform pays 98% to A merchant"
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def record_balance_payable_b(self, card_id: str, amount: float, to_merchant_id: str) -> FinancialTransaction:
        """記錄平台付98%給B商家"""
        transaction = FinancialTransaction(
            card_id=card_id,
            transaction_type=TransactionTypeEnum.BALANCE_PAYABLE_B,
            amount=amount,
            from_merchant_id=None,  # 平台付款
            to_merchant_id=to_merchant_id,
            description=f"Platform pays 98% to B merchant"
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_financial_summary(self, merchant_id: str = None):
        """取得財務摘要"""
        query = self.db.query(FinancialTransaction)
        if merchant_id:
            query = query.filter(
                (FinancialTransaction.from_merchant_id == merchant_id) |
                (FinancialTransaction.to_merchant_id == merchant_id)
            )
        transactions = query.all()
        
        summary = {
            "total_deposits": sum(t.amount for t in transactions if t.transaction_type in [TransactionTypeEnum.DEPOSIT_A, TransactionTypeEnum.DEPOSIT_B]),
            "total_payouts": sum(t.amount for t in transactions if t.transaction_type in [TransactionTypeEnum.BALANCE_PAYABLE_A, TransactionTypeEnum.BALANCE_PAYABLE_B]),
            "platform_revenue": sum(t.amount for t in transactions if t.transaction_type in [TransactionTypeEnum.DEPOSIT_A, TransactionTypeEnum.DEPOSIT_B]),
            "transactions": len(transactions)
        }
        return summary