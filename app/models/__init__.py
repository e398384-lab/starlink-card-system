"""資料庫模型"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # A_ISSUER or B_DISTRIBUTOR
    phone = Column(String(20), unique=True, nullable=False)
    address = Column(String(500))
    balance = Column(Numeric(10, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employees = relationship("Employee", back_populates="merchant")
    cards = relationship("Card", back_populates="issuer")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="employees")

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    serial_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(20), default="CREATED", nullable=False, index=True)
    issuer_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    distributor_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=True)
    current_owner_line_id = Column(String(255), nullable=True, index=True)
    face_value = Column(Numeric(10, 2), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(String(1000))
    image_url = Column(String(500))
    expiry_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    redeemed_at = Column(DateTime, nullable=True)
    
    issuer = relationship("Merchant", foreign_keys=[issuer_id], back_populates="cards")
    logs = relationship("CardHistoryLog", back_populates="card")

class CardHistoryLog(Base):
    __tablename__ = "card_history_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"))
    action = Column(String(50), nullable=False)  # ISSUE, ALLOCATE, CLAIM, TRANSFER_INIT, TRANSFER_ACCEPT, REDEEM
    from_owner_id = Column(String(255))  # LINE ID or Merchant ID
    to_owner_id = Column(String(255))   # LINE ID or Merchant ID
    operator_id = Column(String(255))   # Employee ID or System ID
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    card = relationship("Card", back_populates="logs")

class FinancialLedger(Base):
    __tablename__ = "financial_ledgers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    ledger_type = Column(String(50), nullable=False)  # DEPOSIT_PAYABLE, BALANCE_PAYABLE
    amount = Column(Numeric(10, 2), nullable=False)
    related_card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"))
    is_settled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
