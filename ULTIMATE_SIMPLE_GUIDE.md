# StarLink Card System - 極簡部署指南

## 只需要做這 4 步（5分鐘）

---

### 第一步：註冊 3 個免費服務

#### 1. Supabase（數據庫）
- 訪問: https://supabase.com
- 點擊 "Start your project" → 用 GitHub 登錄
- 創建新項目:
  - **Name**: `starlink-system`
  - **Database Password**: 設置密碼（記住！）
  - **Region**: Singapore
  - 等待2分鐘
- 進 Project Settings → Database → Connection string → **URI**
- 複製 DATABASE_URL

#### 2. Upstash（Redis）
- 訪問: https://upstash.com
- 點擊 "Sign up" → 用 GitHub 登錄
- 創建資料庫:
  - **Name**: `starlink-redis`
  - **Region**: Singapore
  - **Type**: Free Tier
  - 等待1分鐘
- 點擊資料庫 → Details → **REST API URL**
- 複製 REDIS_URL

#### 3. Render.com（主機）
- 訪問: https://render.com
- Sign in → 用 GitHub 登錄
- Dashboard → New → Web Service
- 連接 GitHub → 選 starlink-card-system 倉庫

---

### 第二步：配置環境變量

在 Render 配置中設置:

```
Name: starlink-api
Region: Singapore
Branch: main
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000
Plan: Free

Environment Variables:
  DATABASE_URL = postgresql://postgres:密碼@... (貼上)
  REDIS_URL = rediss://:密碼@... (貼上)
  SECRET_KEY = (生成隨機密鑰)
  PORT = 10000
```

生成 SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 第三步：部署

點擊 "Create Web Service" → 等待 5 分鐘

完成後你會得到網址:
```
https://starlink-xxxx.onrender.com
```

---

### 第四步：測試

訪問: **https://your-app.onrender.com/health**

應該看到:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

## 🎯 完成！你得到了什麼

### API 端點
- 主機: `https://starlink-xxxx.onrender.com`
- 文檔: `/docs`
- 健康檢查: `/health`

### 使用範例

```bash
# 1. 創建商家
curl -X POST https://starlink-xxxx.onrender.com/api/v1/admin/merchants \
  -H "Content-Type: application/json" \
  -d '{"name":"餐廳A","phone":"0912345678","role":"A_ISSUER"}'

# 2. 發行卡片
curl -X POST https://starlink-xxxx.onrender.com/api/v1/admin/cards/issue \
  -H "Content-Type: application/json" \
  -d '{
    "issuer_id": "MERCHANT_ID",
    "title": "100元餐券",
    "face_value": 100,
    "quantity": 10
  }'

# 3. 檢查狀態
curl https://starlink-xxxx.onrender.com/health
```

---

## 📱 管理你的平台

### 查看日誌
- Render Dashboard → Logs

### 重啟服務
- Render Dashboard → Manual Deploy

### 更新代碼
1. 本地修改代碼
2. git add . && git commit -m "update"
3. git push origin main
4. Render 自動重新部署

---

## 📝 系統說明

### 商業模式
- A 類商家（需要新客）→ 發行卡片
- B 類商家（客戶過剩）→ 配發卡片
- 客戶 → 認領卡片
- 平台收取 4% 交易費（每邊 2%）

### 卡片流程
```
CREATED → ALLOCATED → CLAIMED → REDEEMED → RETURNED/EXPIRED
```

### 2%+98% 模型
- 發行時：支付 2% 保證金
- 兌換時：支付 98% 尾款
- 平台淨收入：4%

---

## 💡 常見問題

**Q: 服務會一直運行嗎？**
A: Render 免費版 15 分鐘無活動會休眠。設置 UptimeRobot 每 10 分鐘 ping 一次即可 24/7 運行。

**Q: 如何擴展？**
A: 免費額度用完後，可以升級到付費版：
- Supabase: $25/月
- Upstash: $10/月
- Render: $25/月

**Q: 忘記環境變量怎麼辦？**
A: Render Dashboard → Settings → Environment Variables

---

## 🍎 **總結 - Mac 用戶專屬**

**你不需要安裝任何東西！**

要做的 = 4 步 × 5 分鐘 = 20 分鐘:
1. ✅ 註冊 3 個網站（都用 GitHub 登錄）
2. ✅ 複製 2 個 URL（DATABASE_URL, REDIS_URL）
3. ✅ 在 Render 填表單（貼上 URL）
4. ✅ 點 Deploy → 等待 5 分鐘

**完成！**
---

**現在請完成這 4 步，我會等著你！** 🚀