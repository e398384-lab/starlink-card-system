from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from datetime import datetime
import uuid
import os

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# Enums
class CardStateEnum(str, enum.Enum):
    ISSUED = "issued" # A 商家發行
    ALLOCATED = "allocated" # 已分配給 B 商家
    REDEEMED = "redeemed" # B 商家兌換
    SETTLED = "settled" # 平台結算
    EXPIRED = "expired" # 過期
    CANCELLED = "cancelled" # 取消
    REFUNDED = "refunded" # 退款
    DISPUTED = "disputed" # 爭議

class TransactionTypeEnum(str, enum.Enum):
    DEPOSIT_A = "deposit_a" # A 商家付 2% 給平台
    DEPOSIT_B = "deposit_b" # B 商家付 2% 給平台
    BALANCE_PAYABLE_A = "balance_payable_a" # 平台付 98% 給 A 商家
    BALANCE_PAYABLE_B = "balance_payable_b" # 平台付 98% 給 B 商家

class MerchantType(str, enum.Enum):
    TYPE_A = "type_a"  # 需要新客的商家
    TYPE_B = "type_b"  # 客戶過剩的商家

class MerchantStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Tables
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # 'A' or 'B'
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(200))
    address = Column(Text)
    website = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StarLinkCard(Base):
    __tablename__ = "starlink_cards"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    card_number = Column(String(50), unique=True, nullable=False, index=True)
    face_value = Column(Numeric(10, 2), nullable=False)  # 票面金額
    issued_by_merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    allocated_to_merchant_id = Column(String, ForeignKey("merchants.id"), nullable=True)
    state = Column(SQLEnum(CardStateEnum), default=CardStateEnum.ISSUED, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    allocated_at = Column(DateTime, nullable=True)
    redeemed_at = Column(DateTime, nullable=True)
    settled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    issued_by = relationship("Merchant", foreign_keys=[issued_by_merchant_id])
    allocated_to = relationship("Merchant", foreign_keys=[allocated_to_merchant_id])

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    card_id = Column(String, ForeignKey("starlink_cards.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionTypeEnum), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    from_merchant_id = Column(String, ForeignKey("merchants.id"), nullable=True)
    to_merchant_id = Column(String, ForeignKey("merchants.id"), nullable=True)
    description = Column(Text)
    transaction_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    card = relationship("StarLinkCard")
    from_merchant = relationship("Merchant", foreign_keys=[from_merchant_id])
    to_merchant = relationship("Merchant", foreign_keys=[to_merchant_id])

# For Alembic migrations
def get_tables():
    return [Merchant.__table__, StarLinkCard.__table__, FinancialTransaction.__table__]

def get_db_engine():
    """Create SQLAlchemy engine with Render.com compatibility"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Render.com uses postgres:// but SQLAlchemy 2.0+ requires postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Add SSL mode for Supabase/Render compatibility
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"sslmode": "require"}
    )
    return engine

def create_tables(engine):
    """Create all tables"""
    Base.metadata.create_all(bind=engine)