# 匯出所有 Schema
from app.schemas.schemas import (
    # 用戶相關
    UserRegister,
    UserLogin,
    UserResponse,
    Token,
    
    # 商家相關
    MerchantCreate,
    MerchantUpdate,
    MerchantResponse,
    
    # 星鏈卡相關
    StarLinkCardIssue,
    StarLinkCardRedeem,
    StarLinkCardResponse,
    TransactionResponse,
    TransactionCreate,
    
    # 通用
    MessageResponse,
    ErrorResponse
)

__all__ = [
    # 用戶
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "Token",
    
    # 商家
    "MerchantCreate",
    "MerchantUpdate",
    "MerchantResponse",
    
    # 星鏈卡
    "StarLinkCardIssue",
    "StarLinkCardRedeem",
    "StarLinkCardResponse",
    "TransactionResponse",
    "TransactionCreate",
    
    # 通用
    "MessageResponse",
    "ErrorResponse"
]
