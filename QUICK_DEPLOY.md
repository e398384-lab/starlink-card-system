# StarLink Card System - 一鍵部署

## 超簡單部署（5 分鐘）

只需要在終端機貼上這幾行：

```bash
cd ~/starlink-card-system
python3 deploy.py
```

腳本會自動引導你完成：
1. GitHub 設置
2. Supabase 數據庫
3. Upstash Redis
4. Render.com 部署
5. 測試和驗證

## 或者，手動快速部署

如果你不想用腳本，這是簡化的手動步驟：

### 1. 註冊這 4 個服務（都用 GitHub 登錄）

- **GitHub**: 已經有了
- **Supabase**: https://supabase.com
- **Upstash**: https://upstash.com  
- **Render**: https://render.com

### 2. 從 Supabase 複製 DATABASE_URL

### 3. 從 Upstash 複製 REDIS_URL

### 4. 在 Render 部署：

```
GitHub Repository: your-username/starlink-card-system
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000
Environment Variables:
  - DATABASE_URL=postgresql://...
  - REDIS_URL=rediss://...
  - SECRET_KEY=generate_random_key_here
```

### 5. 訪問你的 API

```
API: https://your-app.onrender.com
Docs: https://your-app.onrender.com/docs
Health: https://your-app.onrender.com/health
```

## 使用 API

### 創建商家
```bash
curl -X POST https://your-app.onrender.com/api/v1/admin/merchants   -H "Content-Type: application/json"   -d '{"name":"餐廳A","phone":"0912345678","role":"A_ISSUER"}'
```

### 發行卡片
```bash
curl -X POST https://your-app.onrender.com/api/v1/admin/cards/issue   -H "Content-Type: application/json"   -d '{
    "issuer_id": "MERCHANT_ID",
    "title": "100元餐券",
    "face_value": 100,
    "quantity": 10
  }'
```

### 檢查系統狀態
```bash
curl https://your-app.onrender.com/health
```

## 完整的 2%+98% 財務模型

- A類商家發行卡片：支付 2% 保證金
- B類商家接收卡片：支付 2% 保證金  
- 客戶兌換時：B類商家獲得 98% 尾款
- 平台收入：每張卡片 4%（雙邊各 2%）

## 支援

查看 DEPLOYMENT_GUIDE.md 獲取詳細說明
或者運行: python3 deploy.py 獲得交互式指導
