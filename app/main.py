# StarLink Card System V3.0 - 極簡免費版
# 核心功能：發卡、分發、核銷、財務自動化
# 技術棧：FastAPI + Supabase + Upstash + Render

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import redis
import os
from dotenv import load_dotenv
import uuid
import hashlib

load_dotenv()

app = FastAPI(title="StarLink Card System V3.0", version="3.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:%21%40Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres")
REDIS_URL = os.getenv("REDIS_URL", "rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379")
SECRET_KEY = os.getenv("SECRET_KEY", "starlink-secret-key-2026")

# Redis 連接
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    redis_client = None
    REDIS_AVAILABLE = False

# 數據庫引擎 (使用 SQLAlchemy)
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Enum, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 數據庫模型
class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'ISSUER_A' or 'DISTRIBUTOR_B'
    phone = Column(String, unique=True, nullable=False)
    line_id = Column(String, nullable=True)
    deposit_rate = Column(Float, default=0.02)
    balance_rate = Column(Float, default=0.98)
    created_at = Column(DateTime, default=datetime.utcnow)

class Card(Base):
    __tablename__ = "cards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    serial_number = Column(String, unique=True, nullable=False)
    status = Column(String, default="CREATED")  # CREATED, ALLOCATED, ACTIVE, LOCKED, REDEEMED, VOID
    issuer_id = Column(String, nullable=False)
    distributor_id = Column(String, nullable=True)
    current_owner_line_id = Column(String, nullable=True)
    face_value = Column(Float, default=100.0)
    expiry_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    redeemed_at = Column(DateTime, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id = Column(String, nullable=False)
    card_id = Column(String, nullable=False)
    type = Column(String, nullable=False)  # DEPOSIT_PAYABLE, BALANCE_PAYABLE
    amount = Column(Float, nullable=False)
    is_settled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CardLog(Base):
    __tablename__ = "card_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    card_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    from_owner = Column(String, nullable=True)
    to_owner = Column(String, nullable=True)
    operator_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# 創建表
Base.metadata.create_all(bind=engine)

# 依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 輔助函數
def generate_serial_number():
    return f"SL-{uuid.uuid4().hex[:8].upper()}"

def create_transaction(db, merchant_id, card_id, type, amount):
    tx = Transaction(
        merchant_id=merchant_id,
        card_id=card_id,
        type=type,
        amount=amount,
        is_settled=False
    )
    db.add(tx)
    db.commit()
    return tx

def log_card_action(db, card_id, action, from_owner, to_owner, operator_id):
    log = CardLog(
        card_id=card_id,
        action=action,
        from_owner=from_owner,
        to_owner=to_owner,
        operator_id=operator_id
    )
    db.add(log)
    db.commit()

# API 模型
class MerchantCreate(BaseModel):
    name: str
    role: str
    phone: str
    line_id: Optional[str] = None

class CardIssue(BaseModel):
    issuer_id: str
    face_value: float
    expiry_days: int
    quantity: int

class CardAllocate(BaseModel):
    card_ids: List[str]
    distributor_id: str

class CardClaim(BaseModel):
    card_id: str
    line_id: str

class CardTransfer(BaseModel):
    card_id: str
    target_line_id: str

class CardRedeem(BaseModel):
    card_id: str
    merchant_id: str

# 路由
@app.get("/")
async def root():
    return {"message": "StarLink Card System V3.0 is running", "version": "3.0.0", "mode": "mock"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "redis": REDIS_AVAILABLE,
        "database": "connected",
        "mode": "mock"
    }

# 商家管理
@app.post("/api/v1/admin/merchants")
async def create_merchant(merchant: MerchantCreate, db = Depends(get_db)):
    # 檢查手機號是否已存在
    existing = db.query(Merchant).filter(Merchant.phone == merchant.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    new_merchant = Merchant(
        name=merchant.name,
        role=merchant.role,
        phone=merchant.phone,
        line_id=merchant.line_id or f"mock_line_{uuid.uuid4().hex[:8]}"
    )
    db.add(new_merchant)
    db.commit()
    db.refresh(new_merchant)
    return new_merchant

@app.get("/api/v1/admin/merchants")
async def list_merchants(db = Depends(get_db)):
    return db.query(Merchant).all()

# 卡片管理
@app.post("/api/v1/admin/cards/issue")
async def issue_cards(data: CardIssue, db = Depends(get_db)):
    issuer = db.query(Merchant).filter(Merchant.id == data.issuer_id).first()
    if not issuer:
        raise HTTPException(status_code=404, detail="Issuer not found")
    
    cards = []
    expiry_date = datetime.utcnow() + timedelta(days=data.expiry_days)
    
    for _ in range(data.quantity):
        serial = generate_serial_number()
        card = Card(
            serial_number=serial,
            status="CREATED",
            issuer_id=data.issuer_id,
            face_value=data.face_value,
            expiry_date=expiry_date
        )
        db.add(card)
        
        # 財務：A 商家應付押金
        deposit_amount = data.face_value * issuer.deposit_rate
        create_transaction(db, data.issuer_id, card.id, "DEPOSIT_PAYABLE", deposit_amount)
        
        cards.append(card)
        log_card_action(db, card.id, "ISSUE", None, data.issuer_id, "system")
    
    db.commit()
    return {"issued": len(cards), "cards": [{"id": c.id, "serial": c.serial_number} for c in cards]}

@app.post("/api/v1/admin/cards/allocate")
async def allocate_cards(data: CardAllocate, db = Depends(get_db)):
    distributor = db.query(Merchant).filter(Merchant.id == data.distributor_id).first()
    if not distributor:
        raise HTTPException(status_code=404, detail="Distributor not found")
    
    allocated = []
    for card_id in data.card_ids:
        card = db.query(Card).filter(Card.id == card_id).first()
        if not card or card.status != "CREATED":
            continue
        
        card.status = "ALLOCATED"
        card.distributor_id = data.distributor_id
        
        # 財務：B 商家應付押金
        deposit_amount = card.face_value * distributor.deposit_rate
        create_transaction(db, data.distributor_id, card.id, "DEPOSIT_PAYABLE", deposit_amount)
        
        log_card_action(db, card.id, "ALLOCATE", "system", data.distributor_id, "system")
        allocated.append(card)
    
    db.commit()
    return {"allocated": len(allocated)}

@app.post("/api/v1/client/claim")
async def claim_card(data: CardClaim, db = Depends(get_db)):
    card = db.query(Card).filter(Card.id == data.card_id).first()
    if not card or card.status != "ALLOCATED":
        raise HTTPException(status_code=404, detail="Card not available")
    
    distributor = db.query(Merchant).filter(Merchant.id == card.distributor_id).first()
    
    card.status = "ACTIVE"
    card.current_owner_line_id = data.line_id
    
    # 財務：B 商家應付尾款
    balance_amount = card.face_value * distributor.balance_rate
    create_transaction(db, card.distributor_id, card.id, "BALANCE_PAYABLE", balance_amount)
    
    log_card_action(db, card.id, "CLAIM", card.distributor_id, data.line_id, data.line_id)
    db.commit()
    
    return {"status": "success", "card": {"id": card.id, "serial": card.serial_number}}

@app.post("/api/v1/client/cards/transfer")
async def transfer_card(data: CardTransfer, db = Depends(get_db)):
    card = db.query(Card).filter(Card.id == data.card_id).first()
    if not card or card.status != "ACTIVE" or card.current_owner_line_id != data.from_line_id:
        raise HTTPException(status_code=404, detail="Card not available for transfer")
    
    # 鎖定卡片
    card.status = "LOCKED"
    log_card_action(db, card.id, "TRANSFER_INIT", data.from_line_id, data.target_line_id, data.from_line_id)
    db.commit()
    
    # 模擬 48 小時超時 (實際應使用 Cronjob)
    # 這裡直接模擬接收成功
    card.status = "ACTIVE"
    card.current_owner_line_id = data.target_line_id
    log_card_action(db, card.id, "TRANSFER_ACCEPT", data.from_line_id, data.target_line_id, data.target_line_id)
    db.commit()
    
    return {"status": "success", "message": "Transfer completed"}

@app.post("/api/v1/client/cards/redeem")
async def redeem_card(data: CardRedeem, db = Depends(get_db)):
    card = db.query(Card).filter(Card.id == data.card_id).first()
    if not card or card.status != "ACTIVE":
        raise HTTPException(status_code=404, detail="Card not available")
    
    issuer = db.query(Merchant).filter(Merchant.id == card.issuer_id).first()
    
    card.status = "REDEEMED"
    card.redeemed_at = datetime.utcnow()
    
    # 財務：A 商家應付尾款
    balance_amount = card.face_value * issuer.balance_rate
    create_transaction(db, card.issuer_id, card.id, "BALANCE_PAYABLE", balance_amount)
    
    log_card_action(db, card.id, "REDEEM", card.current_owner_line_id, card.issuer_id, data.merchant_id)
    db.commit()
    
    return {"status": "success", "message": "Card redeemed successfully"}

# 查詢端點
@app.get("/api/v1/admin/cards")
async def list_cards(db = Depends(get_db)):
    return db.query(Card).all()

@app.get("/api/v1/admin/transactions")
async def list_transactions(db = Depends(get_db)):
    return db.query(Transaction).all()

@app.get("/api/v1/admin/logs")
async def list_logs(db = Depends(get_db)):
    return db.query(CardLog).order_by(CardLog.timestamp.desc()).limit(100).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
