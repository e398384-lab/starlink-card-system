# StarLink Card System - 星鏈卡權益系統

完全免費的雲端部署星鏈卡權益平台，連接需要新客的商家與客戶過剩的商家，平台收取 4% 交易費。

## 🚀 快速開始

### 1. 環境變數設定

在專案根目錄創建 `.env` 檔案：

```env
# Database
DATABASE_URL=postgresql://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres

# Redis
REDIS_URL=rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379

# Microsoft Teams Bot
TEAMS_APP_ID=your_teams_app_id
TEAMS_APP_PASSWORD=your_teams_app_password

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 初始化數據庫

```bash
python -m app.database init
```

### 4. 啟動服務

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📁 專案結構

```
starlink-card-system/
├── app/
│   ├── main.py              # FastAPI 應用主入口
│   ├── config/
│   │   └── settings.py      # 環境變數配置
│   ├── models/              # SQLAlchemy 數據模型
│   ├── routers/             # API 路由
│   ├── schemas/             # Pydantic 數據驗證
│   └── services/            # 業務邏輯服務
├── tests/                   # 測試檔案
├── templates/               # HTML 模板
├── requirements.txt         # Python 依賴
├── .env                     # 環境變數
└── README.md
```

## 🔧 核心功能

### 商家管理
- A 類商家註冊（需要新客）
- B 類商家註冊（客戶過剩）
- 商家認證與審核
- 商家資料管理

### 星鏈卡交易系統
- 星鏈卡發行與兌換
- 4% 交易費自動計算
- 交易記錄追蹤
- 餘額管理

### Microsoft Teams Bot
- 商家消息互動
- 交易通知
- 定時狀態報告
- 命令執行

### 用戶權限
- JWT 身份驗證
- 角色權限控制
- 安全訪問

## 🌐 部署到 Render

### 1. 推送到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/starlink-card-system.git
git push -u origin main
```

### 2. 在 Render 創建服務

1. 訪問 https://dashboard.render.com/
2. 點擊 "New +" → "Web Service"
3. 連接你的 GitHub 倉庫
4. 配置：
   - **Name:** starlink-card-system
   - **Environment:** Python 3.11
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free

5. 添加環境變數（從 `.env` 複製）

### 3. 自動部署

每次推送到 main 分支，Render 會自動重新部署。

## 📊 API 端點

### 商家管理
- `POST /api/v1/merchants/register` - 註冊商家
- `GET /api/v1/merchants/me` - 獲取當前商家資訊
- `PUT /api/v1/merchants/me` - 更新商家資訊

### 星鏈卡交易
- `POST /api/v1/cards/issue` - 發行星鏈卡
- `POST /api/v1/cards/redeem` - 兌換星鏈卡
- `GET /api/v1/cards/history` - 交易歷史

### 用戶認證
- `POST /api/v1/auth/login` - 登入
- `POST /api/v1/auth/register` - 註冊用戶
- `GET /api/v1/auth/me` - 獲取當前用戶

## 🔐 安全說明

1. **不要將 `.env` 檔案提交到 Git**
2. **Render 環境變數必須在 Dashboard 設置**
3. **定期更新 SECRET_KEY**
4. **使用強密碼**

## 📞 支援

如有問題，請查看：
- FastAPI 文檔：https://fastapi.tiangolo.com/
- Supabase 文檔：https://supabase.com/docs
- Upstash 文檔：https://upstash.com/docs
- Microsoft Teams Bot 文檔：https://learn.microsoft.com/teams/bot-framework

## 📄 授權

MIT License
