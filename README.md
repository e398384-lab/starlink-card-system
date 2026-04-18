# StarLink Card System V3.0
# 極簡免費版 - 完全自主部署

## 🚀 快速開始

### 1. 環境配置
系統已自動配置以下服務：
- **數據庫**: Supabase (PostgreSQL)
- **快取**: Upstash (Redis)
- **部署**: Render.com

### 2. API 端點
- **健康檢查**: `GET /health`
- **管理後台**: `GET /docs` (Swagger UI)
- **根路徑**: `GET /`

### 3. 核心流程
1. **創建商家**: `POST /api/v1/admin/merchants`
2. **發行卡片**: `POST /api/v1/admin/cards/issue`
3. **分配卡片**: `POST /api/v1/admin/cards/allocate`
4. **客戶領取**: `POST /api/v1/client/claim`
5. **卡片轉讓**: `POST /api/v1/client/cards/transfer`
6. **權益核銷**: `POST /api/v1/client/cards/redeem`

## 📊 財務模型
- **押金 (2%)**: 發行時 A 商家付，分配時 B 商家付
- **尾款 (98%)**: 客戶領取時 B 商家付，核銷時 A 商家付
- **平台抽成**: 4% (2% 從 A + 2% 從 B)

## 🔧 技術棧
- FastAPI + SQLAlchemy
- Supabase (PostgreSQL)
- Upstash (Redis)
- Render.com (免費部署)

## 📝 注意
- 當前為 **Mock 模式**，前端暫時用網頁版代替 LINE LIFF
- 未來可通過替換環境變數無縫切換到真實 LINE 模式
