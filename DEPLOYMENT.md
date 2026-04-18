# 星鏈卡系統部署指南

## 📋 前置準備

### 1. 已準備好的資源
- ✅ Supabase PostgreSQL 數據庫
- ✅ Upstash Redis 快取
- ✅ GitHub 帳號（需要創建 Token）

### 2. 需要創建的資源
- ⏳ Microsoft Teams Bot（可選，用於消息通知）

---

## 🚀 部署步驟

### 步驟 1: 推送到 GitHub

```bash
# 進入專案目錄
cd starlink-card-system

# 初始化 Git
git init

# 添加所有檔案
git add .

# 提交
git commit -m "Initial commit: StarLink Card System"

# 建立 main 分支
git branch -M main

# 添加 GitHub 遠端（替換 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/starlink-card-system.git

# 推送
git push -u origin main
```

### 步驟 2: 在 Render 創建服務

1. **訪問 Render Dashboard**
   - 前往 https://dashboard.render.com/
   - 登入或註冊帳號

2. **創建新的 Web Service**
   - 點擊 "New +" → "Web Service"
   - 選擇 "Connect a repository"
   - 選擇你剛推送的 `starlink-card-system` 倉庫

3. **配置服務**
   
   **基本設定:**
   - Name: `starlink-card-system`
   - Region: `Oregon` (或離你最近的區域)
   - Branch: `main`
   - Root Directory: (留空)
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: `Free`

   **環境變數 (Environment Variables):**
   
   點擊 "Advanced" → "Add Environment Variable"，添加以下變數：

   ```
   DATABASE_URL=postgresql://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres
   REDIS_URL=rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379
   SECRET_KEY=your-random-secret-key-here (生成一個隨機字串)
   DEBUG=false
   ```

   **Microsoft Teams Bot (可選):**
   ```
   TEAMS_APP_ID=your_teams_app_id
   TEAMS_APP_PASSWORD=your_teams_app_password
   ```

4. **創建服務**
   - 點擊 "Create Web Service"
   - 等待部署完成（約 2-5 分鐘）

### 步驟 3: 驗證部署

部署完成後，你會獲得一個 URL，例如：
```
https://starlink-card-system.onrender.com
```

測試健康檢查端點：
```bash
curl https://starlink-card-system.onrender.com/health
```

應該返回：
```json
{"status": "healthy"}
```

訪問 API 文檔：
```
https://starlink-card-system.onrender.com/docs
```

---

## 📝 使用說明

### 1. 註冊用戶

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. 註冊商家

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

獲取 token 後，使用 token 註冊商家：

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/merchants/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Test Merchant",
    "email": "merchant@example.com",
    "phone": "0912345678",
    "merchant_type": "type_a",
    "address": "123 Test Street",
    "description": "A merchant that needs new customers"
  }'
```

### 3. 發行星鏈卡

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/cards/issue \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "merchant_id": "MERCHANT_ID",
    "value": 1000
  }'
```

### 4. 兌換星鏈卡

```bash
curl -X POST https://your-render-url.onrender.com/api/v1/cards/redeem \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "card_number": "SLK-XXXXXXXXXXXXXXXX",
    "amount": 500,
    "merchant_id": "MERCHANT_ID"
  }'
```

---

## 🔍 API 文檔

系統提供完整的 Swagger UI 文檔：

```
https://your-render-url.onrender.com/docs
```

可以在此介面直接測試所有 API 端點。

---

## 🔐 安全建議

1. **定期更新 SECRET_KEY**
   - 在 Render Dashboard 的環境變數中修改

2. **限制 CORS 來源**
   - 修改 `app/main.py` 中的 `allow_origins`

3. **啟用 HTTPS**
   - Render 自動提供 HTTPS

4. **監控日誌**
   - 在 Render Dashboard 查看應用日誌

---

## 📊 監控與維護

### 查看日誌

在 Render Dashboard:
1. 選擇你的服務
2. 點擊 "Logs" 標籤
3. 查看實時日誌

### 系統狀態查詢

```bash
curl https://your-render-url.onrender.com/api/v1/teams/status
```

返回系統統計數據。

---

## 🆘 故障排除

### 部署失敗

1. 檢查 Build Command 是否正確
2. 確認 `requirements.txt` 存在
3. 查看 Render 日誌錯誤訊息

### 數據庫連接失敗

1. 確認 `DATABASE_URL` 正確
2. 檢查 Supabase 數據庫是否可訪問
3. 驗證 PostgreSQL 連接字串格式

### Redis 連接失敗

1. 確認 `REDIS_URL` 正確
2. 檢查 Upstash Redis 是否可訪問

---

## 📞 支援

如有問題，請：
1. 查看 Render 日誌
2. 檢查 `/docs` API 文檔
3. 確認環境變數設定正確

---

## 🎉 完成！

現在你擁有一個完全免費、雲端運行的星鏈卡權益系統！

系統特點:
- ✅ 完全免費（Render 免費層 + Supabase + Upstash）
- ✅ 自動擴展
- ✅ HTTPS 支援
- ✅ 自動部署（每次推送更新）
- ✅ 4% 交易費自動計算
- ✅ 商家管理
- ✅ 星鏈卡發行與兌換
- ✅ Teams Bot 集成（可選）

開始使用吧！
