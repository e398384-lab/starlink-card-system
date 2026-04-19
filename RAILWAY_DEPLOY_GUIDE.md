# 🚀 Railway 部署指南 - 星鏈卡系統

## 快速部署步驟（只需 2 分鐘）

### 步驟 1: 訪問 Railway
1. 打開瀏覽器訪問: **https://railway.app**
2. 點擊 **"Login"** 或使用 **GitHub 帳號登入**（推薦）

### 步驟 2: 創建新項目
1. 登入後，點擊 **"New Project"**
2. 選擇 **"Deploy from GitHub repo"**
3. 選擇你的倉庫: **`e398384-lab/starlink-card-system`**
   - 如果看不到，請授權 Railway 訪問你的 GitHub 帳號

### 步驟 3: 配置環境變數
在 Railway 項目頁面，點擊 **"Variables"** 標籤，添加以下變數：

| 變數名稱 | 值 |
|---------|-----|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres` |
| `REDIS_URL` | `rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379` |
| `SECRET_KEY` | `RailwaySecretKey_` + 隨機字串（例如 `RailwaySecretKey_20260419`） |
| `DEBUG` | `false` |
| `PYTHON_VERSION` | `3.11` |

**提示**: 點擊 **"Add Variable"** 按鈕，然後逐個添加。

### 步驟 4: 部署
1. 添加完變數後，點擊 **"Deploy"** 或等待自動部署
2. 等待 2-3 分鐘（首次部署需要構建）
3. 看到 **"Running"** 狀態表示成功

### 步驟 5: 獲取服務網址
1. 部署成功後，點擊 **"Settings"** 標籤
2. 找到 **"Domains"** 部分
3. 複製你的服務網址（例如: `https://starlink-card-xxxx.railway.app`）

### 步驟 6: 測試 API
訪問以下網址確認部署成功：
- **首頁**: `https://你的網址.railway.app/`
- **健康檢查**: `https://你的網址.railway.app/health`
- **API 文檔**: `https://你的網址.railway.app/docs`
- **登入端點**: `https://你的網址.railway.app/api/v1/auth/login`

---

## 常見問題

### Q: 部署失敗怎麼辦？
A: 檢查以下幾點：
1. **環境變數是否正確**（特別是 `DATABASE_URL` 必須包含 `+asyncpg`）
2. **資料庫是否可訪問**（Supabase 需要允許外部連接）
3. **查看 Railway 的 Logs**（點擊 "Logs" 標籤查看錯誤訊息）

### Q: 免費額度夠用嗎？
A: Railway 新用戶有 $5 的免費信用額，足夠運行這個項目很長時間。如果擔心費用，可以設置預算警報。

### Q: 如何更新代碼？
A: 只需在 GitHub 推送代碼到 `main` 分支，Railway 會自動重新部署。

---

## 需要幫助？
如果遇到問題，請將錯誤訊息截圖或複製給我，我會立即協助修復！

**祝你部署成功！ 🎉**
