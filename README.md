# ⭐ StarLink Card Platform

**連接需要新客戶的商家與客戶過剩的商家，平台收取4%交易費**

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Microsoft Teams](https://img.shields.io/badge/Microsoft%20Teams-Bot-purple)
![Deployment](https://img.shields.io/badge/Deployment-Render.com-brightgreen)

**完全免費的雲端部署 | 24小時運行 | Microsoft Teams 遠程控制**

---

## 系統概述

### 商業模式

```
A類商家 (需要新客) ←→ 平台收取4% ←→ B類商家 (客戶過剩)
     ↑                                  ↑
     │                                  │
     └─────── 客戶認領與兌換 ───────────┘
```

**費用模型：2% + 98%**

- **發行階段**: A類商家支付2%保證金
- **配發階段**: B類商家支付2%保證金  
- **認領階段**: B類商家應收98%尾款
- **兌換階段**: A類商家應收98%尾款
- **平台收入**: 每張卡收取4%（兩邊各2%）

### 卡片生命周期 (8個狀態)

```
系統發行 → A配發給B → 客戶認領 → (P2P轉讓) → A商家核銷 → (退回/過期)

CREATED → ALLOCATED → CLAIMED → (TRANSFER → TRANSFER_ACCEPTED) → REDEEMED → (RETURNED | EXPIRED)
```

---

## 核心功能

### 1. 商家管理
- ✅ 註冊A類商家（發行方）
- ✅ 註冊B類商家（發放方）  
- ✅ 員工子帳號管理
- ✅ 額度限制設置

### 2. 卡片管理
- ✅ 批量發行卡片（A→系統）
- ✅ 卡片配發（A→B）
- ✅ 客戶認領（B→客戶）
- ✅ P2P轉讓（客戶→客戶，48小時有效）
- ✅ 商家兌換（客戶→A）
- ✅ 實時狀態追蹤

### 3. 財務系統
- ✅ 2%+98%自動計算
- ✅ 雙重記帳（借貸平衡）
- ✅ 保證金自動收取
- ✅ 尾款應收管理
- ✅ 平台收入統計
- ✅ 結算記錄

### 4. Microsoft Teams Bot
- ✅ 遠程系統監控
- ✅ `/status` - 系統健康狀態
- ✅ `/cards` - 卡片統計
- ✅ `/exec <cmd>` - 執行命令
- ✅ `/help` - 幫助信息

---

## 技術棧

| 組件 | 技術 | 說明 |
|------|------|------|
| **後端框架** | FastAPI | 高性能異步框架，自動生成API文檔 |
| **數據庫** | PostgreSQL | Supabase免費版（500MB） |
| **緩存** | Redis | Upstash免費版（10k命令/天） |
| **部署** | Render.com | 免費版（750小時/月） |
| **容器** | Docker | 本地開發環境 |
| **Bot框架** | Teams Bot Framework | Microsoft Teams集成 |
| **語言** | Python 3.8+ | 現代異步編程 |

---

## API端點

### 管理端 `/api/v1/admin/*`

```bash
# 創建商家
POST /admin/merchants
{"name": "餐廳A", "phone": "0912345678", "role": "A_ISSUER"}

# 發行卡片
POST /admin/cards/issue  
{
  "issuer_id": "uuid",
  "title": "100元餐券",
  "face_value": 100,
  "quantity": 10
}

# 商家庫存查詢
GET /admin/merchants/{id}/inventory

# 系統財務匯總
GET /admin/system/financial-summary

# 初始化數據庫
POST /admin/init-db

# 健康檢查
GET /health
```

### 商家端 `/api/v1/merchant/*`

```bash
# B商家接收配發
POST /merchant/allocate
{"serial_numbers": ["SLC-..."], "distributor_id": "uuid"}

# B商家發放給客戶
POST /merchant/distribute
{"serial_number": "SLC-...", "customer_phone": "0912345678"}

# 發起P2P轉讓
POST /merchant/cards/{serial}/transfer/init

# 接受P2P轉讓
POST /merchant/cards/transfer/accept
{"transfer_token": "ABC123", "to_phone": "0987654321"}

# A商家核銷卡片
POST /merchant/redeem
{"serial_number": "SLC-...", "customer_phone": "0912345678"}

# 查詢卡片狀態
GET /merchant/cards/{serial}/status
```

### 客戶端 `/api/v1/client/*`

```bash
# 查詢客戶持有的卡片
GET /client/{phone}/cards

# 客戶兌換卡片
POST /client/redeem
{"serial_number": "SLC-...", "customer_phone": "0912345678"}

# 發起轉讓（客戶端）
POST /client/transfer/init

# 接受轉讓（客戶端）
POST /client/transfer/accept

# 驗證卡片有效性
GET /client/cards/{serial}/verify
```

---

## 快速開始（本地）

### 1. 安裝

```bash
cd ~/starlink-card-system
./install.sh
```

### 2. 配置環境變量

```bash
cp .env.example .env
# 編輯 .env 文件，填寫數據庫連接字符串
```

### 3. 啟動服務

```bash
# 使用 Docker（推薦）
docker-compose up -d

# 啟動應用
./run.sh
```

### 4. 訪問API文檔

打開瀏覽器：
- API文檔: http://localhost:10000/docs
- 健康檢查: http://localhost:10000/health

---

## 快速開始（生產 - 免費部署）

### 完整部署流程（約15-20分鐘）

**1. 創建雲服務**
- ✅ Supabase (PostgreSQL) - 免費500MB
- ✅ Upstash (Redis) - 免費10k命令/天  
- ✅ Render.com - 免費750小時/月
- ✅ GitHub賬戶

**2. 部署步驟**

詳細步驟見 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

```bash
# 檢查清單
☑️ Supabase 數據庫創建 + 複製 DATABASE_URL
☑️ Upstash Redis創建 + 複製 REDIS_URL
☑️ Render.com 部署 + 配置環境變量
☑️ 初始化數據庫: POST /admin/init-db
☑️ 測試API: GET /health
☑️ 配置UptimeRobot保持喚醒（可選）
☑️ Teams Bot集成（可選）
```

**完全免費，無需信用卡（除Azure Bot驗證）**

---

## Microsoft Teams Bot

### 可用命令

在Teams中與Bot對話：

```
/status          - 系統健康狀態
/cards           - 卡片統計
/exec <command>  - 執行命令（ls, ps, docker, df等）
/help            - 顯示幫助
```

### 設置指南

詳見 [TEAMS_SETUP.md](./TEAMS_SETUP.md)

**快速步驟：**
1. Azure Bot註冊（免費F0層）
2. 獲取 APP_ID 和 APP_PASSWORD
3. 配置 Render 環境變量
4. 設置 Webhook: `/api/bot/messages`
5. 創建 Teams 應用程序包
6. 安裝到 Teams

---

## 測試流程

### 完整生命周期測試

```bash
# 1. 創建A類商家（餐廳）
POST /admin/merchants {"name": "餐廳A", "phone": "0911111111", "role": "A_ISSUER"}
# 記錄返回的 merchant_id

# 2. 創建B類商家（咖啡店）
POST /admin/merchants {"name": "咖啡店B", "phone": "0922222222", "role": "B_DISTRIBUTOR"}
# 記錄返回的 merchant_id

# 3. A商家發行卡片（10張100元餐券）
POST /admin/cards/issue
{
  "issuer_id": "a_merchant_uuid",
  "title": "100元餐券",
  "face_value": 100,
  "quantity": 10
}
# 記錄返回的 serial_numbers

# 4. B商家接收配發（全部10張）
POST /merchant/allocate
{
  "serial_numbers": ["SLC-...", ...],
  "distributor_id": "b_merchant_uuid"
}

# 5. B商家發放給客戶
POST /merchant/distribute
{
  "serial_number": "SLC-...",
  "customer_phone": "0933333333"
}

# 6. 客戶查詢持有的卡片
GET /client/0933333333/cards

# 7. 客戶到A商家店鋪兌換
POST /client/redeem
{
  "serial_number": "SLC-...",
  "customer_phone": "0933333333"
}

# 8. 查詢平台收入
GET /admin/system/financial-summary
# 應該顯示：總收入4%（10張x100元x4% = 40元）
```

---

## 財務計算示例

**場景**: A餐廳發行100張100元餐券，全部配發給B咖啡店，最終全部兌換

```
發行總額: 100張 × 100元 = 10,000元面額

A餐廳支付: 10,000 × 2% = 200元（保證金）
B咖啡店支付: 10,000 × 2% = 200元（保證金）
─────────────────────────────────────────
平台收取: 400元（總收入4%）

兌換時支付:
A餐廳應收: 10,000 × 98% = 9,800元（但已經支付200元，實收9,600元）
B咖啡店應收: 10,000 × 98% = 9,800元（但已經支付200元，實收9,600元）
──────────────────────────────────────────────────────────────
實際現金流:
  平台淨收入: 400元（保留的4%）
  A餐廳淨收入: 9,600元  
  B咖啡店淨收入: 9,600元
```

**結果**: 平台每張卡賺4元，100張卡 = 400元

---

## 數據庫結構

```sql
merchants           # 商家（A/B類型）
├─ id (UUID)
├─ name
├─ phone
├─ role (A_ISSUER / B_DISTRIBUTOR)
└─ max_employees

employees           # 員工子帳號
├─ id (UUID)
├─ merchant_id
├─ name
├─ phone
└─ is_active

cards               # 卡片主數據
├─ id (UUID)
├─ serial_number
├─ issuer_id (A商家)
├─ current_holder_id
├─ title
├─ face_value
├─ status (8個狀態)
├─ created_at
├─ allocated_at
├─ claimed_at
├─ redeemed_at
└─ transferred_at

card_details        # 卡片詳細信息
├─ id (UUID)
├─ card_id
├─ customer_phone
├─ holder_employee_id
├─ transfer_token
└─ transfer_expires_at

card_logs           # 審計日誌
├─ id (UUID)
├─ card_id
├─ merchant_id
├─ employee_id
├─ action
├─ from_status
├─ to_status
├─ details (JSONB)
└─ created_at

financial_transactions  # 財務交易
├─ id (UUID)
├─ card_id
├─ merchant_id
├─ transaction_type
├─ amount
├─ currency
├─ debit_account
├─ credit_account
├─ description
├─ is_settled
├─ settled_at
└─ created_at
```

---

## 文檔索引

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - 完整部署指南（免費雲端）
- **[TEAMS_SETUP.md](./TEAMS_SETUP.md)** - Teams Bot設置詳細步驟
- **API文檔** - 訪問 `/docs` 查看自動生成的Swagger文檔

---

## 免費額度限制

| 服務 | 免費額度 | 說明 |
|------|----------|------|
| **Supabase** | 500MB存儲 | 約可存儲1萬張卡片數據 |
| **Upstash** | 10k命令/天 | 平均每張卡1次操作，日限1萬張 |
| **Render** | 750小時/月 | 約25天24小時連續運行 |
| **Azure Bot** | 1萬條消息/月 | 每日300+條指令 |

**升級建議**: 當達到80%額度時開始考慮升級

---

## 性能優化

- **數據庫連接池**: 最多20個並發連接
- **Redis緩存**: 減少數據庫查詢
- **狀態機原子性**: 單一數據庫事務保證一致性
- **並發控制**: Redis分佈式鎖 + 數據庫行級鎖

---

## 未來擴展

- [ ] QR碼生成與掃描
- [ ] 定時任務（過期、退回）
- [ ] 短信驗證
- [ ] 商家Web儀表板
- [ ] 客戶移動錢包
- [ ] 統計報表
- [ ] 區塊鏈集成（可選）

---

## 支援

遇到問題？

1. 檢查 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 的故障排除章節
2. 查看 Render 日誌
3. 測試本地環境: `./run.sh`
4. 提交 Issue 到 GitHub

---

## 授權

MIT License - 可商業使用

---

**🎉 StarLink Card Platform 已經準備就緒！**

**下一步**: 查看 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 開始免費部署！