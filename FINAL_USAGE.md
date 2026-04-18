# 🌟 星鏈卡權益系統 - 完整部署指南

## ✅ 已完成的工作

### 系統架構
- ✅ FastAPI 後端框架
- ✅ Supabase PostgreSQL 數據庫集成
- ✅ Upstash Redis 快取集成
- ✅ Microsoft Teams Bot 框架
- ✅ JWT 身份驗證系統
- ✅ 4% 交易費自動計算
- ✅ 商家管理系統（A/B 類）
- ✅ 星鏈卡發行與兌換
- ✅ 交易記錄追蹤
- ✅ RESTful API 設計
- ✅ Swagger API 文檔

### 專案結構
```
starlink-card-system/
├── app/
│   ├── main.py              # FastAPI 應用主入口
│   ├── auth.py              # JWT 認證
│   ├── database.py          # 數據庫配置
│   ├── config/
│   │   └── settings.py      # 環境變數
│   ├── models/              # SQLAlchemy 模型
│   ├── routers/             # API 路由
│   │   ├── auth.py          # 認證路由
│   │   ├── merchants.py     # 商家路由
│   │   ├── cards.py         # 星鏈卡路由
│   │   └── teams.py         # Teams Bot 路由
│   ├── schemas/             # Pydantic 模型
│   └── services/            # 業務邏輯
├── tests/
│   └── test_api.py          # API 測試
├── templates/               # HTML 模板
├── .env                     # 環境變數
├── .env.example             # 環境變數範本
├── .gitignore               # Git 忽略
├── requirements.txt         # Python 依賴
├── render.yaml              # Render 部署配置
├── deploy.sh                # 快速部署腳本
├── README.md                # 專案說明
├── DEPLOYMENT.md            # 部署指南
└── FINAL_USAGE.md           # 使用說明
```

---

## 🚀 快速部署（3 步驟）

### 步驟 1: 推送到 GitHub

```bash
cd starlink-card-system

# 初始化 Git
git init
git add .
git commit -m "Initial commit: StarLink Card System"
git branch -M main

# 添加遠端倉庫（替換 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/starlink-card-system.git

# 推送
git push -u origin main
```

### 步驟 2: 在 Render 部署

1. 訪問 https://dashboard.render.com/
2. 點擊 "New +" → "Web Service"
3. 連接你的 GitHub 倉庫
4. 配置：
   - **Name:** `starlink-card-system`
   - **Region:** `Oregon`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`

5. 添加環境變數：
   ```
   DATABASE_URL=postgresql://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres
   REDIS_URL=rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379
   SECRET_KEY=生成一個隨機字串（見下方）
   DEBUG=false
   ```

   **生成 SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

6. 點擊 "Create Web Service"

### 步驟 3: 驗證部署

部署完成後（約 2-5 分鐘），你會獲得一個 URL：
```
https://starlink-card-system.onrender.com
```

測試：
```bash
curl https://starlink-card-system.onrender.com/health
```

應該返回：
```json
{"status": "healthy"}
```

---

## 📖 使用說明

### 1. 查看 API 文檔

部署後訪問：
```
https://your-render-url.onrender.com/docs
```

這裡有完整的 Swagger UI，可以直接測試所有 API。

### 2. 註冊用戶

**API:** `POST /api/v1/auth/register`

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**回應:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": "uuid"
}
```

### 3. 登入

**API:** `POST /api/v1/auth/login`

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 4. 註冊商家

**API:** `POST /api/v1/merchants/register`

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/merchants/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "測試商家",
    "email": "merchant@example.com",
    "phone": "0912345678",
    "merchant_type": "type_a",
    "address": "台北市信義區",
    "description": "需要新客的商家"
  }'
```

**merchant_type:**
- `type_a`: 需要新客的商家（A 類）
- `type_b`: 客戶過剩的商家（B 類）

### 5. 發行星鏈卡

**API:** `POST /api/v1/cards/issue`

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/cards/issue \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "merchant_id": "商家 UUID",
    "value": 1000
  }'
```

**回應:**
```json
{
  "id": "card-uuid",
  "card_number": "SLK-XXXXXXXXXXXXXXXX",
  "value": 1000,
  "balance": 1000,
  "status": "active"
}
```

### 6. 兌換星鏈卡

**API:** `POST /api/v1/cards/redeem`

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/cards/redeem \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "card_number": "SLK-XXXXXXXXXXXXXXXX",
    "amount": 500,
    "merchant_id": "消費商家 UUID"
  }'
```

**交易費計算:**
- 消費金額: $500
- 交易費 (4%): $20
- 商家淨額: $480

### 7. 查詢交易歷史

**API:** `GET /api/v1/cards/history`

```bash
curl -X GET https://your-render-url.onrender.com/api/v1/cards/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. 查詢系統狀態

**API:** `GET /api/v1/teams/status`

```bash
curl -X GET https://your-render-url.onrender.com/api/v1/teams/status
```

**回應:**
```json
{
  "merchants": {
    "total": 10,
    "type_a": 5,
    "type_b": 5,
    "active": 8
  },
  "cards": {
    "total": 50,
    "active": 45,
    "total_balance": 50000
  },
  "transactions": {
    "total": 120,
    "total_commission": 4800
  },
  "users": {
    "total": 30,
    "active": 28
  }
}
```

---

## 🔧 核心功能說明

### 商家類型

**A 類商家 (type_a):**
- 需要新客的商家
- 可以發行星鏈卡吸引顧客
- 支付 4% 交易費

**B 類商家 (type_b):**
- 客戶過剩的商家
- 接受星鏈卡兌換
- 獲得 96% 的消費金額

### 星鏈卡流程

1. **發行:** A 類商家發行星鏈卡（預付金額）
2. **分配:** 卡片分配給用戶
3. **兌換:** 用戶在 B 類商家兌換使用
4. **結算:** 系統自動扣除 4% 交易費，96% 給 B 類商家

### 交易費機制

- 平台收取 **4%** 交易費
- 自動從每筆交易中扣除
- 累積到平台餘額

---

## 🔐 安全建議

1. **定期更新 SECRET_KEY**
   - 在 Render Dashboard → Environment → 修改 SECRET_KEY

2. **限制 CORS 來源**
   - 修改 `app/main.py` 中的 `allow_origins`

3. **使用強密碼**
   - 至少 8 位字元
   - 包含大小寫字母、數字、符號

4. **監控日誌**
   - 在 Render Dashboard → Logs 查看

5. **啟用 HTTPS**
   - Render 自動提供 HTTPS

---

## 📊 監控與維護

### 查看日誌

Render Dashboard → 選擇服務 → Logs

### 系統健康檢查

```bash
curl https://your-render-url.onrender.com/health
```

### API 文檔

```
https://your-render-url.onrender.com/docs
```

### 重啟服務

Render Dashboard → 選擇服務 → Restart

---

## 🆘 常見問題

### Q: 部署失敗？

**A:** 檢查以下項目：
1. `requirements.txt` 是否存在
2. Build Command 是否正確
3. 查看 Render 日誌錯誤訊息

### Q: 數據庫連接失敗？

**A:** 檢查：
1. `DATABASE_URL` 是否正確
2. Supabase 數據庫是否可訪問
3. PostgreSQL 連接字串格式

### Q: 無法訪問 API？

**A:** 檢查：
1. 服務是否正在運行
2. URL 是否正確
3. 環境變數是否設置

### Q: 如何更新程式碼？

**A:** 
```bash
git add .
git commit -m "Update description"
git push
```
Render 會自動重新部署。

---

## 📞 支援資源

- **FastAPI 文檔:** https://fastapi.tiangolo.com/
- **Supabase 文檔:** https://supabase.com/docs
- **Upstash 文檔:** https://upstash.com/docs
- **Render 文檔:** https://render.com/docs
- **Microsoft Teams Bot:** https://learn.microsoft.com/teams/bot-framework

---

## 🎉 完成！

恭喜！你現在擁有一個：
- ✅ 完全免費的雲端系統
- ✅ 自動擴展的架構
- ✅ HTTPS 安全連接
- ✅ 自動部署流程
- ✅ 4% 交易費自動計算
- ✅ 完整的商家管理
- ✅ 星鏈卡發行與兌換
- ✅ Teams Bot 集成

**開始使用你的星鏈卡系統吧！** 🚀

---

## 📝 下一步建議

1. **測試所有功能** - 使用 Swagger UI (`/docs`)
2. **創建第一個商家** - 註冊 A 類和 B 類商家
3. **發行第一張卡片** - 測試星鏈卡流程
4. **設置 Teams Bot** - 可選，用於消息通知
5. **邀請用戶** - 開始使用系統
6. **監控交易** - 查看 4% 交易費累積

---

**版本:** 1.0.0  
**最後更新:** 2026-04-18  
**技術棧:** FastAPI + PostgreSQL + Redis + Teams Bot
