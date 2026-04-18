# 🚀 星鏈卡 V3.0 - 手動部署指南

## 方法一：自動重新部署（推薦）

### 步驟 1: 登入 Render
1. 訪問 https://dashboard.render.com
2. 點擊 "Sign in with GitHub"
3. 使用您的 GitHub 帳號登入（e398384-lab）

### 步驟 2: 選擇服務
1. 在 Dashboard 中找到 `starlink-api-sks0` 服務
2. 點擊進入服務詳情頁

### 步驟 3: 切換分支
1. 點擊 "Settings" 標籤
2. 找到 "Source" 部分
3. 將 Branch 從 `main` 改為 `render-compatible`
4. 點擊 "Save Changes"

### 步驟 4: 等待部署
- Render 會自動重新部署（約 2-3 分鐘）
- 部署完成後，訪問 https://starlink-api-sks0.onrender.com/docs 查看新 API

---

## 方法二：本地測試（立即試用）

### 步驟 1: 安裝依賴
```bash
cd /Users/alanlin/starlink-v3/starlink-v3
pip install -r requirements.txt
```

### 步驟 2: 設置環境變數
```bash
export DATABASE_URL="postgresql://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres"
export REDIS_URL="rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379"
export SECRET_KEY="starlink-secret-key-2026"
```

### 步驟 3: 啟動服務
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 步驟 4: 訪問 API 文檔
打開瀏覽器訪問: http://localhost:8000/docs

---

## 📋 API 測試清單

### 1. 創建 A 商家（發行商）
```bash
curl -X POST "http://localhost:8000/api/v1/admin/merchants" \
  -H "Content-Type: application/json" \
  -d '{"name":"統一咖啡","role":"ISSUER_A","phone":"0912345678"}'
```

### 2. 創建 B 商家（分銷商）
```bash
curl -X POST "http://localhost:8000/api/v1/admin/merchants" \
  -H "Content-Type: application/json" \
  -d '{"name":"星巴克","role":"DISTRIBUTOR_B","phone":"0987654321"}'
```

### 3. 發行卡片
```bash
curl -X POST "http://localhost:8000/api/v1/admin/cards/issue" \
  -H "Content-Type: application/json" \
  -d '{"issuer_id":"<A 商家 ID>","face_value":100,"expiry_days":30,"quantity":10}'
```

### 4. 分配卡片給 B 商家
```bash
curl -X POST "http://localhost:8000/api/v1/admin/cards/allocate" \
  -H "Content-Type: application/json" \
  -d '{"card_ids":["<卡片 ID1>","<卡片 ID2>"],"distributor_id":"<B 商家 ID>"}'
```

### 5. 客戶領取卡片
```bash
curl -X POST "http://localhost:8000/api/v1/client/claim" \
  -H "Content-Type: application/json" \
  -d '{"card_id":"<卡片 ID>","line_id":"mock_line_user123"}'
```

### 6. 卡片轉讓
```bash
curl -X POST "http://localhost:8000/api/v1/client/cards/transfer" \
  -H "Content-Type: application/json" \
  -d '{"card_id":"<卡片 ID>","from_line_id":"mock_line_user123","target_line_id":"mock_line_user456"}'
```

### 7. 權益核銷
```bash
curl -X POST "http://localhost:8000/api/v1/client/cards/redeem" \
  -H "Content-Type: application/json" \
  -d '{"card_id":"<卡片 ID>","merchant_id":"<A 商家 ID>"}'
```

---

## 📊 系統特點

### V3.0 改進
- ✅ **極簡架構**: 只保留核心功能（發卡、分發、核銷、財務）
- ✅ **完全免費**: Supabase + Upstash + Render
- ✅ **自動部署**: GitHub Webhook 觸發
- ✅ **模擬模式**: 無需 LINE 即可完整測試
- ✅ **財務自動化**: 押金/尾款自動計算

### 核心流程
1. **A 商家** 發行卡片（付 2% 押金）
2. **系統方** 分配給 **B 商家**（B 付 2% 押金）
3. **B 商家** 分發給客戶（B 付 98% 尾款）
4. **客戶** 去 **A 商家** 核銷（A 付 98% 尾款）
5. **平台** 自動抽取 4% 費用

---

## 🎯 下一步

### 選項 A: 完成 Render 部署（推薦）
按照「方法一」手動切換分支，讓系統在雲端運行

### 選項 B: 本地測試
按照「方法二」在本地啟動，立即測試所有功能

### 選項 C: 等待自動部署
Render 可能已經在重新部署，等待 5-10 分鐘後再測試

---

## 📞 需要幫助？

如果遇到任何問題：
1. 檢查 Render 日誌（Dashboard → Events）
2. 確認環境變數已正確設置
3. 檢查 Supabase 和 Upstash 連接

系統已完全就緒，只待您點擊「保存」即可自動部署！
