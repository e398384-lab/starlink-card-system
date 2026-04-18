# StarLink Card System - 使用說明

## 🎉 部署成功！

您的 StarLink Card System 已成功部署到： **https://starlink-api-sks0.onrender.com**

## 🚀 快速開始

### 1. 等待服務完全啟動（2-3 分鐘）

訪問健康檢查：
```bash
curl https://starlink-api-sks0.onrender.com/health
```

預期響應：
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### 2. 初始化數據庫

```bash
curl -X POST https://starlink-api-sks0.onrender.com/api/v1/admin/init-db
```

### 3. 訪問 API 文檔

打開瀏覽器：
https://starlink-api-sks0.onrender.com/docs

---

## 📚 API 端點

### 管理端（系統管理）

**創建商家**
```bash
curl -X POST https://starlink-api-sks0.onrender.com/api/v1/admin/merchants \
  -H "Content-Type: application/json" \
  -d '{"name":"餐廳A","phone":"0912345678","role":"A_ISSUER"}'
```

**發行卡片**
```bash
curl -X POST https://starlink-api-sks0.onrender.com/api/v1/admin/cards/issue \
  -H "Content-Type: application/json" \
  -d '{
    "issuer_id": "MERCHANT_ID_HERE",
    "title": "100元餐券",
    "face_value": 100,
    "quantity": 10
  }'
```

**查詢商家庫存**
```bash
curl https://starlink-api-sks0.onrender.com/api/v1/admin/merchants/{merchant_id}/inventory
```

### 商家端（B類）

**接收卡片配發**
```bash
curl -X POST https://starlink-api-sks0.onrender.com/api/v1/merchant/allocate \
  -H "Content-Type: application/json" \
  -d '{
    "serial_numbers": ["SLC-20241201-ABCD"],
    "distributor_id": "B_MERCHANT_ID"
  }'
```

**發放給客戶**
```bash
curl -X POST https://starlink-api-sks0.onrender.com/api/v1/merchant/distribute \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "SLC-20241201-ABCD",
    "customer_phone": "0911111111"
  }'
```

**核銷卡片**
```bash
curl -X POST https://starlink-api-sks0.onrender.com/api/v1/merchant/redeem \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "SLC-20241201-ABCD",
    "customer_phone": "0911111111"
  }'
```

### 客戶端

**查詢客戶卡片**
```bash
curl https://starlink-api-sks0.onrender.com/api/v1/client/{phone}/cards
```

**客戶兌換**
```bash
curl -X POST https://starlink-api-sks0.onrender.com/api/v1/client/redeem \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "SLC-20241201-ABCD",
    "customer_phone": "0911111111"
  }'
```

---

## 📊 卡片生命周期

```
CREATED → ALLOCATED → CLAIMED → REDEEMED → RETURNED/EXPIRED
  ↓            ↓          ↓          ↓
  系統創建   A配給B    B發給客戶  A商家核銷
```

---

## 💰 財務模型 (2%+98%)

### 示例：100元餐券

**發行階段（A→系統）**
- A商家支付: 100 × 2% = 2元保證金

**配發階段（A→B）**
- B商家支付: 100 × 2% = 2元保證金

**平台收入**
- 總計: 4元 (4%)

**兌換階段（客戶→A）**
- A商家獲得: 100 × 98% = 98元
- B商家獲得: 98元（來自客戶）

---

## 🔧 管理面板

### Render 控制台
URL: https://dashboard.render.com/web

功能：
- ⚙️ 查看日誌
- 🔄 手動重新部署
- 💾 設置環境變量
- 📊 監控資源使用

### Supabase 控制台
URL: https://supabase.com/dashboard/projects

功能：
- 📊 查看數據庫
- 📈 監控查詢
- 🔐 管理數據庫用戶

### Upstash 控制台
URL: https://console.upstash.com/redis

功能：
- 📊 查看 Redis 命令統計
- 📈 監控使用量
- ⚙️ 管理配置

---

## 💡 常見問題

### Q: API 返回 504 Gateway Timeout？
A: Render 免費實例在啟動中，請等待 2-3 分鐘後重試。

### Q: 如何保持服務 24/7 運行？
A: 註冊 https://uptimerobot.com 並設置監控：
- URL: https://starlink-api-sks0.onrender.com/health
- 間隔: 10 分鐘

### Q: 如何更新代碼？
```bash
cd ~/starlink-card-system
git add .
git commit -m "update"
git push origin main
# Render 會自動重新部署
```

### Q: 忘記秘密密鑰？
A: 在 Render Dashboard → Settings → Environment Variables → SECRET_KEY

---

## 📱 下一步（可選）

### Microsoft Teams Bot 集成
查看: TEAMS_SETUP.md

### 批量操作腳本
查看: scripts/ 目錄

### 數據分析面板
使用 Supabase 的 SQL 編輯器創建查詢

---

## 🎉 恭喜！

你的 **StarLink Card Platform** 現在：
- ✅ 在免費雲端 24/7 運行
- ✅ 支援 4% 交易費模式
- ✅ 完整的卡片生命周期管理
- ✅ 支援 A/B 類商家
- ✅ 自動財務結算

**完全免費！**

---

**如需支援，查看：**
- DEPLOYMENT_GUIDE.md (詳細部署說明)
- TEAMS_SETUP.md (Teams Bot 集成)
- QUICK_DEPLOY.md (快速部署指南)

**想瞭解更多？告訴我你的需求！**