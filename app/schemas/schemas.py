from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.enums import MerchantType, MerchantStatus

# ========================================
# 用戶相關 Schema
# ========================================
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    merchant_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    merchant_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

# ========================================
# 商家相關 Schema
# ========================================
class MerchantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = None
    merchant_type: MerchantType
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class MerchantResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    merchant_type: MerchantType
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    balance: float = 0.0
    commission_rate: float = 0.04
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ========================================
# 星鏈卡相關 Schema
# ========================================
class StarLinkCardIssue(BaseModel):
    merchant_id: str
    value: float = Field(..., gt=0)
    expires_days: Optional[int] = 365

class StarLinkCardRedeem(BaseModel):
    card_number: str
    amount: float = Field(..., gt=0)
    merchant_id: str

class StarLinkCardResponse(BaseModel):
    id: str
    card_number: str
    value: float
    balance: float
    state: str
    issued_by_merchant_id: str
    allocated_to_merchant_id: Optional[str] = None
    issued_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: str
    card_id: str
    transaction_type: str
    amount: float
    from_merchant_id: Optional[str] = None
    to_merchant_id: Optional[str] = None
    description: Optional[str] = None
    transaction_at: datetime
    
    class Config:
        from_attributes = True

# ========================================
# 通用 Schema
# ========================================
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    success: bool = False
