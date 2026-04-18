import enum

class MerchantType(str, enum.Enum):
    """商家類型"""
    TYPE_A = "type_a"  # 需要新客的商家
    TYPE_B = "type_b"  # 客戶過剩的商家

class MerchantStatus(str, enum.Enum):
    """商家狀態"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class CardStateEnum(str, enum.Enum):
    """卡片狀態"""
    ISSUED = "issued"       # A 商家發行
    ALLOCATED = "allocated" # 已分配給 B 商家
    REDEEMED = "redeemed"   # B 商家兌換
    SETTLED = "settled"     # 平台結算
    EXPIRED = "expired"     # 過期
    CANCELLED = "cancelled" # 取消
    REFUNDED = "refunded"   # 退款
    DISPUTED = "disputed"   # 爭議

class TransactionTypeEnum(str, enum.Enum):
    """交易類型"""
    DEPOSIT_A = "deposit_a"           # A 商家付 2% 給平台
    DEPOSIT_B = "deposit_b"           # B 商家付 2% 給平台
    BALANCE_PAYABLE_A = "balance_payable_a"  # 平台付 98% 給 A 商家
    BALANCE_PAYABLE_B = "balance_payable_b"  # 平台付 98% 給 B 商家
