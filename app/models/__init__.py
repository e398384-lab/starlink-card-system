# 匯出所有模型
from app.models.base import (
    Base,
    User,
    Merchant,
    StarLinkCard,
    FinancialTransaction as Transaction,
    CardStateEnum,
    TransactionTypeEnum,
    MerchantType,
    MerchantStatus
)

# TeamsMessage 暫時不使用，如果未來需要可以添加
# class TeamsMessage(Base):
#     __tablename__ = "teams_messages"
#     ...

__all__ = [
    "Base",
    "User",
    "Merchant", 
    "StarLinkCard",
    "Transaction",
    "CardStateEnum",
    "TransactionTypeEnum",
    "MerchantType",
    "MerchantStatus"
]
