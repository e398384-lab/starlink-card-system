from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import TeamsMessage
from app.schemas import TeamsMessageResponse, MessageResponse
from app.auth import get_current_user
from app.config.settings import settings
from datetime import datetime
import json

router = APIRouter(prefix="/teams", tags=["Teams Bot"])

# 簡單的 Teams Bot 模擬（實際部署時需要與 Microsoft Bot Framework 集成）
@router.post("/webhook", response_model=MessageResponse)
async def teams_webhook(
    message_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """接收 Teams Bot 消息的 Webhook"""
    # 記錄收到的消息
    teams_message = TeamsMessage(
        message_id=message_data.get("message_id", ""),
        conversation_id=message_data.get("conversation_id", ""),
        user_id=message_data.get("user_id", ""),
        content=message_data.get("content", ""),
        message_type=message_data.get("message_type", "text"),
        status="pending"
    )
    
    db.add(teams_message)
    await db.commit()
    await db.refresh(teams_message)
    
    # 處理命令
    content = message_data.get("content", "").strip()
    
    if content.startswith("/status"):
        # 返回系統狀態
        response = await generate_status_report(db)
        return {"message": response, "success": True}
    
    elif content.startswith("/help"):
        help_text = """
🌟 星鏈卡系統 - 幫助指令

可用指令:
/status - 查看系統狀態
/help - 顯示此幫助訊息
/cards - 查看我的星鏈卡
/history - 查看交易歷史
/merchant - 查看商家資訊

如需更多協助，請聯繫系統管理員。
"""
        return {"message": help_text, "success": True}
    
    elif content.startswith("/cards"):
        return {"message": "請使用 API 端點獲取您的星鏈卡資訊", "success": True}
    
    elif content.startswith("/history"):
        return {"message": "請使用 API 端點獲取交易歷史", "success": True}
    
    elif content.startswith("/merchant"):
        return {"message": "請使用 API 端點獲取商家資訊", "success": True}
    
    else:
        return {"message": f"收到訊息：{content}\n輸入 /help 查看可用指令", "success": True}

async def generate_status_report(db: AsyncSession) -> str:
    """生成系統狀態報告"""
    from app.models import Merchant, StarLinkCard, Transaction, User
    
    # 統計商家數量
    result = await db.execute(select(Merchant))
    merchants = result.scalars().all()
    type_a_count = sum(1 for m in merchants if m.merchant_type.value == "type_a")
    type_b_count = sum(1 for m in merchants if m.merchant_type.value == "type_b")
    active_count = sum(1 for m in merchants if m.status.value == "active")
    
    # 統計卡片數量
    result = await db.execute(select(StarLinkCard))
    cards = result.scalars().all()
    active_cards = sum(1 for c in cards if c.status == "active")
    total_card_value = sum(c.balance for c in cards)
    
    # 統計交易
    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()
    total_transactions = len(transactions)
    total_commission = sum(t.commission for t in transactions)
    
    # 統計用戶
    result = await db.execute(select(User))
    users = result.scalars().all()
    active_users = sum(1 for u in users if u.is_active)
    
    report = f"""
📊 星鏈卡系統狀態報告

🏪 商家統計:
  • 總數: {len(merchants)}
  • A 類 (需要新客): {type_a_count}
  • B 類 (客戶過剩): {type_b_count}
  • 已啟用: {active_count}

💳 星鏈卡統計:
  • 總數: {len(cards)}
  • 活躍卡片: {active_cards}
  • 總餘額: ${total_card_value:.2f}

💰 交易統計:
  • 總交易數: {total_transactions}
  • 平台收益 (4% 佣金): ${total_commission:.2f}

👥 用戶統計:
  • 總用戶數: {len(users)}
  • 活躍用戶: {active_users}

報告時間: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
    return report

@router.get("/status", response_model=dict)
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """獲取系統狀態（JSON 格式）"""
    from app.models import Merchant, StarLinkCard, Transaction, User
    
    result = await db.execute(select(Merchant))
    merchants = result.scalars().all()
    
    result = await db.execute(select(StarLinkCard))
    cards = result.scalars().all()
    
    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return {
        "merchants": {
            "total": len(merchants),
            "type_a": sum(1 for m in merchants if m.merchant_type.value == "type_a"),
            "type_b": sum(1 for m in merchants if m.merchant_type.value == "type_b"),
            "active": sum(1 for m in merchants if m.status.value == "active")
        },
        "cards": {
            "total": len(cards),
            "active": sum(1 for c in cards if c.status == "active"),
            "total_balance": sum(c.balance for c in cards)
        },
        "transactions": {
            "total": len(transactions),
            "total_commission": sum(t.commission for t in transactions)
        },
        "users": {
            "total": len(users),
            "active": sum(1 for u in users if u.is_active)
        }
    }
