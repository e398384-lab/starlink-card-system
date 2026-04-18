# 🚀 星鏈卡系統 - 部署清單

## ✅ 部署前檢查清單

### 1. 環境變數準備
- [ ] `DATABASE_URL` - Supabase PostgreSQL 連接字串（已提供）
- [ ] `REDIS_URL` - Upstash Redis 連接字串（已提供）
- [ ] `SECRET_KEY` - 需要生成隨機字串
- [ ] `TEAMS_APP_ID` - Microsoft Teams Bot ID（可選）
- [ ] `TEAMS_APP_PASSWORD` - Microsoft Teams Bot 密碼（可選）

**生成 SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. GitHub 倉庫
- [ ] 創建 GitHub 帳號（如果還沒有）
- [ ] 初始化 Git: `git init`
- [ ] 提交程式碼: `git add . && git commit -m "Initial commit"`
- [ ] 創建遠端倉庫
- [ ] 推送程式碼: `git push -u origin main`

### 3. Render 服務
- [ ] 註冊 Render 帳號（如果還沒有）
- [ ] 創建新的 Web Service
- [ ] 連接 GitHub 倉庫
- [ ] 配置 Build Command: `pip install -r requirements.txt`
- [ ] 配置 Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] 選擇免費方案（Free）
- [ ] 添加環境變數
- [ ] 創建服務

### 4. 驗證部署
- [ ] 等待部署完成（2-5 分鐘）
- [ ] 訪問健康檢查: `https://your-url.onrender.com/health`
- [ ] 訪問 API 文檔: `https://your-url.onrender.com/docs`
- [ ] 測試用戶註冊
- [ ] 測試商家註冊
- [ ] 測試星鏈卡發行
- [ ] 測試星鏈卡兌換

---

## 📋 部署步驟（快速參考）

### 步驟 1: 準備環境變數

```bash
# 生成 SECRET_KEY
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
echo "你的 SECRET_KEY: $SECRET_KEY"
```

### 步驟 2: 推送到 GitHub

```bash
cd starlink-card-system

# 初始化 Git（如果還沒初始化）
git init
git add .
git commit -m "Initial commit: StarLink Card System"
git branch -M main

# 添加遠端倉庫（替換 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/starlink-card-system.git

# 推送
git push -u origin main
```

### 步驟 3: 在 Render 部署

1. 訪問 https://dashboard.render.com/
2. 點擊 "New +" → "Web Service"
3. 選擇 "Connect a repository"
4. 選擇 `starlink-card-system` 倉庫

**配置:**
- Name: `starlink-card-system`
- Region: `Oregon`
- Branch: `main`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Instance Type: `Free`

**環境變數:**
```
DATABASE_URL=postgresql://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres
REDIS_URL=rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379
SECRET_KEY=（貼上剛才生成的 SECRET_KEY）
DEBUG=false
```

5. 點擊 "Create Web Service"

### 步驟 4: 測試

部署完成後，你的 URL 會是：
```
https://starlink-card-system-xxxx.onrender.com
```

測試健康檢查：
```bash
curl https://starlink-card-system-xxxx.onrender.com/health
```

訪問 API 文檔：
```
https://starlink-card-system-xxxx.onrender.com/docs
```

---

## 🎯 首次使用指南

### 1. 註冊用戶

在 Swagger UI (`/docs`) 中：
1. 找到 `POST /api/v1/auth/register`
2. 點擊 "Try it out"
3. 輸入：
   ```json
   {
     "email": "test@example.com",
     "password": "testpassword123"
   }
   ```
4. 點擊 "Execute"
5. 複製返回的 `access_token`

### 2. 註冊商家

1. 找到 `POST /api/v1/merchants/register`
2. 點擊 "Authorize"，輸入 `Bearer YOUR_TOKEN`
3. 點擊 "Try it out"
4. 輸入：
   ```json
   {
     "name": "測試商家 A",
     "email": "merchant-a@example.com",
     "phone": "0912345678",
     "merchant_type": "type_a",
     "address": "台北市",
     "description": "需要新客的商家"
   }
   ```
5. 點擊 "Execute"
6. 複製返回的商家 `id`

### 3. 發行星鏈卡

1. 找到 `POST /api/v1/cards/issue`
2. 點擊 "Try it out"
3. 輸入：
   ```json
   {
     "merchant_id": "商家 ID",
     "value": 1000
   }
   ```
4. 點擊 "Execute"
5. 複製返回的 `card_number`（例如：SLK-XXXXXXXXXXXXXXXX）

### 4. 兌換星鏈卡

1. 註冊另一個 B 類商家
2. 找到 `POST /api/v1/cards/redeem`
3. 輸入：
   ```json
   {
     "card_number": "SLK-XXXXXXXXXXXXXXXX",
     "amount": 500,
     "merchant_id": "B 類商家 ID"
   }
   ```
4. 點擊 "Execute"

---

## 📊 系統功能檢查

- [ ] 用戶註冊/登入
- [ ] A 類商家註冊
- [ ] B 類商家註冊
- [ ] 發行星鏈卡
- [ ] 兌換星鏈卡
- [ ] 交易記錄查詢
- [ ] 系統狀態查詢
- [ ] 4% 交易費計算
- [ ] 商家餘額管理
- [ ] 卡片餘額管理

---

## 🔍 監控與維護

### 查看日誌
- Render Dashboard → 選擇服務 → Logs

### 重啟服務
- Render Dashboard → 選擇服務 → More → Restart

### 更新程式碼
```bash
git add .
git commit -m "Update description"
git push
```
Render 會自動重新部署。

### 修改環境變數
- Render Dashboard → 選擇服務 → Environment
- 修改後點擊 "Save Changes"
- 服務會自動重新部署

---

## 🆘 故障排除

### 問題：部署失敗
**解決：**
1. 檢查 Build Command 是否正確
2. 查看 Render 日誌錯誤訊息
3. 確認 `requirements.txt` 存在

### 問題：數據庫連接失敗
**解決：**
1. 檢查 `DATABASE_URL` 是否正確
2. 確認 Supabase 數據庫可訪問
3. 檢查 PostgreSQL 連接字串格式

### 問題：無法訪問 API
**解決：**
1. 確認服務正在運行
2. 檢查 URL 是否正確
3. 驗證環境變數是否設置

### 問題：Token 無效
**解決：**
1. 確認 Token 格式正確（Bearer token）
2. 檢查 Token 是否過期
3. 重新登入獲取新 Token

---

## 📞 支援資源

- **API 文檔:** `https://your-url.onrender.com/docs`
- **Render 文檔:** https://render.com/docs
- **FastAPI 文檔:** https://fastapi.tiangolo.com/
- **Supabase 文檔:** https://supabase.com/docs
- **Upstash 文檔:** https://upstash.com/docs

---

## ✅ 部署完成確認

- [ ] 服務運行正常
- [ ] 健康檢查通過
- [ ] API 文檔可訪問
- [ ] 用戶註冊成功
- [ ] 商家註冊成功
- [ ] 星鏈卡發行成功
- [ ] 星鏈卡兌換成功
- [ ] 交易費計算正確
- [ ] 日誌正常

**恭喜！部署完成！** 🎉

---

**版本:** 1.0.0  
**日期:** 2026-04-18
