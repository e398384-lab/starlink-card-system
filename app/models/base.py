from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
import os
from sqlalchemy import Enum

# Import notification - will be created in main.py
# from app.main import notify_manager

Base = declarative_base()

# Enum types
class MerchantRole(str, Enum):
    A_ISSUER = "A_ISSUER"  # A類商家 - 發行
    B_DISTRIBUTOR = "B_DISTRIBUTOR"  # B類商家 - 發放

class CardStatus(str, Enum):
    CREATED = "CREATED"  # 系統發行完成
    ALLOCATED = "ALLOCATED"  # B類商家接收
    CLAIMED = "CLAIMED"  # 客戶認領
    TRANSFER_INIT = "TRANSFER_INIT"  # P2P轉讓發起
    TRANSFER_ACCEPTED = "TRANSFER_ACCEPTED"  # P2P轉讓完成
    REDEEMED = "REDEEMED"  # A類商家核銷
    RETURNED = "RETURNED"  # 退回
    EXPIRED = "EXPIRED"  # 過期

class TransactionType(str, Enum):
    DEPOSIT_A = "DEPOSIT_A"  # A類商家支付2%保證金
    DEPOSIT_B = "DEPOSIT_B"  # B類商家支付2%保證金
    BALANCE_PAYABLE_A = "BALANCE_PAYABLE_A"  # A類商家應收98%
    BALANCE_PAYABLE_B = "BALANCE_PAYABLE_B"  # B類商家應收98%
    SETTLED = "SETTLED"  # 已結算

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # 商家名稱
    phone = Column(String, unique=True, nullable=False)  # 聯繫電話
    role = Column(String, nullable=False, default="B_MERCHANT") # A或B類型
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 員工上限
    max_employees = Column(Integer, default=5)
    
    # JSONB存儲額外信息
    metadata = Column(JSONB, default=dict)
    
    # 關聯
    employees = relationship("Employee", back_populates="merchant")
    issued_cards = relationship("Card", foreign_keys="[Card.issuer_id]", back_populates="issuer")
    received_cards = relationship("Card", foreign_keys="[Card.current_holder_id]", back_populates="current_holder")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)  # 用作登錄帳號
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    merchant = relationship("Merchant", back_populates="employees")

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    serial_number = Column(String, unique=True, nullable=False)  # 序列號
    
    issuer_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)  # A類發行商家
    current_holder_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"))  # 當前持有者
    
    title = Column(String, nullable=False)  # 標題（如"100元餐券"）
    face_value = Column(Float, nullable=False)  # 面值
    status = Column(SQLEnum(CardStatus), default=CardStatus.CREATED)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    allocated_at = Column(DateTime)  # 配發給B的時間
    claimed_at = Column(DateTime)  # 客戶認領時間
    redeemed_at = Column(DateTime)  # 核銷時間
    transferred_at = Column(DateTime)  # 轉讓時間
    expired_at = Column(DateTime)  # 過期時間
    
    # JSONB存儲
    metadata = Column(JSONB, default=dict)
    
    # 關聯
    issuer = relationship("Merchant", foreign_keys=[issuer_id], back_populates="issued_cards")
    current_holder = relationship("Merchant", foreign_keys=[current_holder_id], back_populates="received_cards")
    logs = relationship("CardLog", back_populates="card")
    # current_detail會在CardDetail中反向關聯

class CardDetail(Base):
    __tablename__ = "card_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False, unique=True)
    customer_phone = Column(String)  # 客戶電話（認領後填寫）
    holder_employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))  # 經手員工
    transfer_token = Column(String, unique=True)  # 轉讓令牌（48小時有效期）
    transfer_expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    card = relationship("Card", back_populates="current_detail")
    holder_employee = relationship("Employee")

# Add reverse relationship
Card.current_detail = relationship("CardDetail", uselist=False, back_populates="card")

class CardLog(Base):
    __tablename__ = "card_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    
    action = Column(String, nullable=False)  # 操作描述
    from_status = Column(SQLEnum(CardStatus))
    to_status = Column(SQLEnum(CardStatus))
    
    details = Column(JSONB, default=dict)  # 詳細信息
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    card = relationship("Card", back_populates="logs")
    merchant = relationship("Merchant")
    employee = relationship("Employee")

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)
    
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="TWD")
    
    # 雙重記帳
    debit_account = Column(String)  # 借方帳戶
    credit_account = Column(String)  # 貸方帳戶
    
    description = Column(String)
    reference_id = Column(String)  # 外部參考ID
    
    is_settled = Column(Boolean, default=False)  # 是否已結算
    settled_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    card = relationship("Card")
    merchant = relationship("Merchant")

# Database setup function
def get_db_engine():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    engine = create_engine(DATABASE_URL)
    return engine

def create_tables():
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

# For notifications - will be imported in main.py
# def notify_manager(message: str, level: str = "info"):
#     """Global notification function - placeholder"""
#     print(f"[{level.upper()}] {message}")
