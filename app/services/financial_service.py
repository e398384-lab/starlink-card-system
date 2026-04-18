"""
Financial Service - Handles all financial transactions and double-entry accounting
"""

from sqlalchemy.orm import Session
from app.models.base import FinancialTransaction, TransactionType, Card, Merchant
from app.services.card_service import log_card_transition
import uuid
from datetime import datetime
from typing import Optional, List

class FinancialService:
    def __init__(self, db: Session):
        self.db = db
    
    def record_deposit(self, card: Card, merchant: Merchant, transaction_type: TransactionType) -> FinancialTransaction:
        """
        Record 2% deposit when card moves between merchants
        """
        amount = card.face_value * 0.02  # 2% of face value
        
        tx = FinancialTransaction(
            card_id=card.id,
            merchant_id=merchant.id,
            transaction_type=transaction_type,
            amount=amount,
            currency="TWD",
            debit_account="CASH",  # Merchant pays (cash decreases)
            credit_account="DEPOSIT_LIABILITY",  # Platform holds deposit (liability)
            description=f"2% deposit for card {card.serial_number}",
            is_settled=True,  # Deposits are settled immediately
            settled_at=datetime.utcnow()
        )
        self.db.add(tx)
        
        # Notify platform of deposit received
        # notify_manager(f"Deposit received: {amount} TWD from {merchant.name}", "financial")
        
        self.db.commit()
        return tx
    
    def record_balance_payable(self, card: Card, merchant: Merchant, transaction_type: TransactionType) -> FinancialTransaction:
        """
        Record 98% balance as payable to merchant
        - When customer claims from B: B's 98% becomes payable
        - When customer redeems at A: A's 98% becomes payable
        """
        amount = card.face_value * 0.98  # 98% of face value
        
        tx = FinancialTransaction(
            card_id=card.id,
            merchant_id=merchant.id,
            transaction_type=transaction_type,
            amount=amount,
            currency="TWD",
            debit_account="BALANCE_PAYABLE",  # Platform owes money (liability)
            credit_account="ACCOUNTS_PAYABLE",  # Money owed to merchant
            description=f"98% balance payable for card {card.serial_number}",
            is_settled=False,  # Not settled yet
        )
        self.db.add(tx)
        self.db.commit()
        return tx
    
    def settle_transaction(self, transaction_id: uuid.UUID) -> Optional[FinancialTransaction]:
        """
        Mark transaction as settled (platform pays merchant)
        """
        tx = self.db.query(FinancialTransaction).filter_by(id=transaction_id).first()
        if not tx:
            return None
        
        tx.is_settled = True
        tx.settled_at = datetime.utcnow()
        
        # Log the settlement
        log_card_transition(
            self.db, tx.card, "transaction_settled", None, None,
            merchant_id=tx.merchant_id,
            details={
                "transaction_id": str(tx.id),
                "amount": tx.amount,
                "type": tx.transaction_type.value
            }
        )
        
        self.db.commit()
        return tx
    
    def get_merchant_balance(self, merchant_id: uuid.UUID) -> dict:
        """
        Get merchant's financial summary
        """
        deposits = self.db.query(FinancialTransaction).filter_by(
            merchant_id=merchant_id,
            transaction_type=TransactionType.DEPOSIT_A
        ).all()
        
        balance_payable = self.db.query(FinancialTransaction).filter_by(
            merchant_id=merchant_id,
            transaction_type__in=[TransactionType.BALANCE_PAYABLE_A, TransactionType.BALANCE_PAYABLE_B],
            is_settled=False
        ).all()
        
        total_deposits = sum(tx.amount for tx in deposits)
        total_balance_due = sum(tx.amount for tx in balance_payable)
        
        return {
            "merchant_id": str(merchant_id),
            "total_deposits": total_deposits,
            "total_balance_due": total_balance_due,
            "net_position": total_balance_due - total_deposits,
            "unpaid_transactions": len(balance_payable)
        }
    
    def calculate_platform_revenue(self) -> dict:
        """
        Calculate platform revenue (4% per card is collected upfront)
        """
        all_cards = self.db.query(Card).filter_by(status=CardStatus.REDEEMED).all()
        
        total_revenue = 0
        platform_holdings = 0
        
        for card in all_cards:
            deposit_tx = self.db.query(FinancialTransaction).filter_by(
                card_id=card.id,
                transaction_type__in=[TransactionType.DEPOSIT_A, TransactionType.DEPOSIT_B]
            ).all()
            
            # Each card should generate 4% total (2% from each side)
            card_revenue = sum(tx.amount for tx in deposit_tx)  # This should be 4% of face value
            total_revenue += card_revenue
            
            # Add to platform holdings
            platform_holdings += sum(tx.amount for tx in deposit_tx if not tx.is_settled)
        
        return {
            "total_revenue": total_revenue,
            "platform_holdings": platform_holdings,
            "redeemed_cards": len(all_cards),
            "average_revenue_per_card": total_revenue / len(all_cards) if all_cards else 0
        }
    
    def process_full_lifecycle(self, card: Card, issuer: Merchant, distributor: Merchant) -> dict:
        """
        Process complete financial flow for a card
        1. Record deposit from issuer (2%)
        2. Record deposit from distributor (2%) 
        3. Record balance payable to distributor (98%) - when claimed
        4. Record balance payable to issuer (98%) - when redeemed
        """
        transactions = []
        
        # 1. Issuer pays 2% deposit when issuing
        if card.status in [CardStatus.CREATED, CardStatus.ALLOCATED]:
            tx1 = self.record_deposit(card, issuer, TransactionType.DEPOSIT_A)
            transactions.append(tx1)
        
        # 2. Distributor pays 2% deposit when receiving
        if card.status == CardStatus.ALLOCATED:
            tx2 = self.record_deposit(card, distributor, TransactionType.DEPOSIT_B)
            transactions.append(tx2)
        
        # 3. When customer claims from distributor
        if card.status == CardStatus.CLAIMED and card.claimed_at:
            tx3 = self.record_balance_payable(card, distributor, TransactionType.BALANCE_PAYABLE_B)
            transactions.append(tx3)
            
            # Platform takes 2% fee (from distributor's side)
            # This is implicit - the deposit already collected
        
        # 4. When customer redeems at issuer
        if card.status == CardStatus.REDEEMED and card.redeemed_at:
            tx4 = self.record_balance_payable(card, issuer, TransactionType.BALANCE_PAYABLE_A)
            transactions.append(tx4)
            
            # Platform takes another 2% fee (from issuer's side)
            # This is implicit - the deposit already collected
            
            # Platform now has 4% total and pays out 96% to merchants
        
        # 5. Settle transactions
        for tx in transactions:
            self.settle_transaction(tx.id)
        
        return {
            "transactions_created": len(transactions),
            "platform_fee_collected": sum(tx.amount for tx in transactions[:2]),  # First two are deposits (4% total)
            "balances_owed": sum(tx.amount for tx in transactions[2:]) if len(transactions) > 2 else 0
        }