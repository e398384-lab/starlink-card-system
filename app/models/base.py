# StarLink Card System - 完全相容 Render.com 的版本
# 改進: SSL 連接、連接池、錯誤恢復、日誌記錄

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.pool import NullPool, QueuePool
import uuid
from datetime import datetime
import os
import logging
import time
from typing import Optional

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Database setup functions for Render.com
class DatabaseManager:
    """
    專為 Render.com 優化的資料庫管理器
    - SSL/TLS 連接
    - 連接池管理
    - 自動重連
    - 詳細日誌
    """
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._init_engine()
    
    def _init_engine(self):
        """初始化資料庫引擎，支援 Render 環境"""
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            raise ValueError("❌ DATABASE_URL environment variable is required")
        
        logger.info(f"📊 Initiating database connection...")
        logger.info(f"🔗 URL: {DATABASE_URL.split('@')[1].split('/')[0]}  ")
        
        # Render.com PostgreSQL 需要特殊配置
        # 1. SSL 連接必須啟用
        # 2. 連接池大小限制（免費層）
        # 3. 連接回收防止閒置超時
        
        # 檢查是否需要 SSL
        is_ssl = DATABASE_URL.startswith("postgresql://")
        
        if is_ssl:
            # Render.com 提供的 URL 需要 SSL
            connect_args = {
                "sslmode": "require",  # Render PostgreSQL 要求 SSL
                "connect_timeout": 10,  # 10秒連接超時
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
        else:
            connect_args = {}
        
        # 連接池配置 - 針對 Render 免費層優化
        pool_config = {
            "poolclass": QueuePool,
            "pool_size": 5,        # 最大連接數
            "max_overflow": 10,    # 超出 pool_size 的最大連接
            "pool_pre_ping": True, # 連接前檢查
            "pool_recycle": 3600,  # 1小時回收連接（防止閒置超時）
            "pool_timeout": 30,    # 獲取連接的超時時間
        }
        
        try:
            self.engine = create_engine(
                DATABASE_URL,
                **pool_config,
                connect_args=connect_args,
                echo=False,  # 設為 True 可看到所有 SQL 語句
            )
            
            # 測試連接
            self._test_connection()
            
            # 配置 Session
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("✅ Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def _test_connection(self):
        """測試資料庫連接"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
                logger.info("✅ Database connection test passed")
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            raise
    
    def create_tables(self):
        """自動創建/更新表結構"""
        try:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ All database tables created/updated successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """刪除所有表（測試用）"""
        try:
            logger.warning("Dropping all tables...")
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("✅ All tables dropped!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to drop tables: {e}")
            raise
    
    def get_session(self):
        """獲取新的資料庫會話"""
        return scoped_session(self.SessionLocal)
    
    def cleanup(self):
        """清理連接資源"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections disposed")

# 全局 DatabaseManager 實例
db_manager = DatabaseManager()

# For notifications - will be imported in main.py
# def notify_manager(message: str, level: str = "info"):
#     """Global notification function - placeholder"""
#     print(f"[{level.upper()}] {message}")
# 設計使用便利工廠
get_engine = db_manager.engine
create_tables = db_manager.create_tables
drop_tables = db_manager.drop_tables
get_session = db_manager.get_session

if __name__ == "__main__":
    # 用於開發時直接運行
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        db_manager.create_tables()
    elif len(sys.argv) > 1 and sys.argv[1] == "drop":
        confirm = input("⚠  這將刪除所有數據！確認嗎？(yes/no): ")
        if confirm.lower() == "yes":
            db_manager.drop_tables()
    else:
        print("用法: python base.py create  # 創建表")
        print("     python base.py drop     # 刪除表（危險！）")
