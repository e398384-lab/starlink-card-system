# 🚀 立即部署指南 - 星鏈卡系統

## ✅ 已完成的工作

1. ✅ 程式碼已推送到 GitHub: `https://github.com/e398384-lab/starlink-card-system`
2. ✅ 所有環境配置完成
3. ✅ 數據庫和 Redis 已連接
4. ✅ 系統架構完整

## 🎯 現在只需 3 分鐘完成部署

### 步驟 1: 打開 Render (10 秒)

訪問: **https://dashboard.render.com/**

如果沒有帳號，免費註冊（只需要 Google 帳號或 GitHub 帳號）

### 步驟 2: 創建 Web Service (2 分鐘)

1. 點擊 **"New +"** → **"Web Service"**

2. 選擇 **"Connect a repository"**
   - 找到並選擇: `e398384-lab/starlink-card-system`

3. **填寫配置:**

   ```
   Name: starlink-card-system
   Region: Oregon (或離你最近的)
   Branch: main
   Root Directory: (留空)
   Runtime: Python
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free (免費!)
   ```

4. **添加環境變數** (點擊 "Advanced" → "Add Environment Variable"):

   複製貼上以下內容:

   ```
   DATABASE_URL=postgresql://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres
   ```

   ```
   REDIS_URL=rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379
   ```

   ```
   SECRET_KEY=M82MsQDE7jvr1W21s75ZysZ6Uiwn2gcraqvbdvPOq6Y
   ```

   ```
   DEBUG=false
   ```

   ```
   APP_NAME=StarLink Card System
   ```

5. 點擊 **"Create Web Service"**

### 步驟 3: 等待部署 (1-3 分鐘)

- Render 會自動:
  - 安裝所有依賴
  - 創建數據庫表
  - 啟動服務
  - 配置 HTTPS

- 你可以看到實時日誌滾動

### 步驟 4: 完成！(10 秒)

部署完成後，你會看到:
```
https://starlink-card-system-xxxx.onrender.com
```

**立即測試:**

1. **健康檢查:**
   ```
   https://starlink-card-system-xxxx.onrender.com/health
   ```
   應該返回: `{"status": "healthy"}`

2. **API 文檔:**
   ```
   https://starlink-card-system-xxxx.onrender.com/docs
   ```
   完整的 Swagger UI，可以直接測試所有功能

---

## 📱 快速開始使用

### 1. 註冊第一個用戶

在 `/docs` 頁面:
1. 找到 `POST /api/v1/auth/register`
2. 點擊 "Try it out"
3. 輸入:
   ```json
   {
     "email": "admin@example.com",
     "password": "admin123456"
   }
   ```
4. 點擊 "Execute"
5. 複製 `access_token`

### 2. 註冊 A 類商家 (需要新客)

1. 點擊 "Authorize"，輸入 `Bearer YOUR_TOKEN`
2. 找到 `POST /api/v1/merchants/register`
3. 輸入:
   ```json
   {
     "name": "我的第一家店",
     "email": "shop-a@example.com",
     "phone": "0912345678",
     "merchant_type": "type_a",
     "address": "台北市信義區",
     "description": "需要新客的商家"
   }
   ```
4. 點擊 "Execute"
5. 複製返回的 `id` (商家 ID)

### 3. 發行的第一張星鏈卡

1. 找到 `POST /api/v1/cards/issue`
2. 輸入:
   ```json
   {
     "merchant_id": "剛才複製的商家 ID",
     "value": 1000
   }
   ```
3. 點擊 "Execute"
4. 複製 `card_number` (例如: `SLK-XXXXXXXXXXXXXXXX`)

### 4. 查看系統狀態

找到 `GET /api/v1/teams/status`
點擊 "Execute"

你會看到:
- 商家統計
- 卡片統計
- 交易統計
- 平台收益 (4% 佣金)

---

## 🎉 系統功能清單

✅ **完全免費**
- Render 免費層 (750 小時/月)
- Supabase PostgreSQL (免費層)
- Upstash Redis (免費層)

✅ **自動擴展**
- 根據流量自動調整
- 無需管理伺服器

✅ **安全連接**
- HTTPS 自動配置
- JWT 身份驗證
- 密碼加密儲存

✅ **核心功能**
- A/B 類商家管理
- 星鏈卡發行與兌換
- 4% 交易費自動計算
- 交易記錄追蹤
- 餘額管理
- Teams Bot 集成 (可選)

✅ **完整 API**
- Swagger UI 文檔
- 可直接測試
- RESTful 設計

---

## 📊 系統架構

```
用戶 → Render (FastAPI) → Supabase (數據庫)
                ↓
            Upstash Redis (快取)
                ↓
         Microsoft Teams Bot (通知)
```

**交易流程:**
1. A 類商家發行星鏈卡 (預付 $1000)
2. 用戶在 B 類商家消費 $500
3. 系統自動扣除 4% ($20) 作為平台費
4. B 類商家獲得 $480
5. 交易記錄永久保存

---

## 🔧 後續維護

### 更新程式碼
```bash
git add .
git commit -m "更新說明"
git push
```
Render 會自動重新部署 (約 1 分鐘)

### 查看日誌
Render Dashboard → 選擇服務 → Logs

### 修改環境變數
Render Dashboard → 選擇服務 → Environment
修改後自動重新部署

---

## 🆘 常見問題

**Q: 部署失敗？**
A: 檢查 Render 日誌，通常是環境變數問題

**Q: 無法訪問 API？**
A: 確認服務狀態是 "Live"，檢查 URL 是否正確

**Q: 如何重置？**
A: 在 Render Dashboard 刪除服務，重新創建即可

---

## 🎯 下一步

1. ✅ 完成上述部署步驟
2. ✅ 測試所有 API 功能
3. ✅ 註冊真實商家
4. ✅ 發行第一張卡片
5. ✅ 邀請用戶使用
6. ✅ 監控交易和收益

---

**部署連結:**
- GitHub: https://github.com/e398384-lab/starlink-card-system
- Render: https://dashboard.render.com/

**準備好了嗎？點擊這裡開始部署:**
👉 https://dashboard.render.com/create?type=web

選擇 "Connect a repository" 然後選擇 `e398384-lab/starlink-card-system`

---

**版本:** 1.0.0  
**部署時間:** 約 3 分鐘  
**成本:** $0 (完全免費)

🚀 **立即開始，3 分鐘後你的系統就上線了！**
