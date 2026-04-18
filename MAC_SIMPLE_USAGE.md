# 🍎 macOS 超簡單使用指南

## 只需三個步驟即可啓動 StarLink Card System

---

### 第一步：創建並執行安裝腳本

打開 **終端機 (Terminal)**，貼上這三行命令（一次貼一行）：

```bash
cd ~
curl -o setup_mac.sh https://raw.githubusercontent.com/your-username/starlink-card-system/main/setup_mac.sh
chmod +x setup_mac.sh && ./setup_mac.sh
```

> 如果第二行報錯，就用這個替代：
> ```bash
> curl -o setup_mac.sh "https://transfer.sh/xxx/setup_mac.sh"
> ```

---

### 第二步：等待自動安裝完成

腳本會自動：
- ✅ 檢查並安裝 Homebrew（如有需要）
- ✅ 安裝 Python 3.11（如有需要）
- ✅ 檢查 Docker Desktop（會告訴你怎麼裝）
- ✅ 創建項目文件
- ✅ 啓動 PostgreSQL 和 Redis
- ✅ 安裝 Python 依賴
- ✅ 啓動應用程序

安裝完成後，你會看到：
```
✅ 安裝完成！
訪問：
  📚 API 文件: http://localhost:10000/docs
  🏥 健康檢查: http://localhost:10000/health
```

---

### 第三步：打開瀏覽器查看

在瀏覽器中打開：
- **API 文件**: http://localhost:10000/docs
- **健康檢查**: http://localhost:10000/health

---

## 之後如何再次啓動

關閉終端機後，下次要再啟動：

```bash
cd ~/starlink-card-system
./start.sh
```

---

## Windows 用戶怎麼辦？

Windows 用戶建議使用：
1. **Windows Subsystem for Linux (WSL2)**
2. **Docker Desktop for Windows**

然後執行相同的安裝步驟。

---

## 如果終端機複製貼上無效

在 Mac 終端機中：
- **複製**: Cmd + C
- **貼上**: Cmd + V（不是 Cmd + Shift + V）

如果還是無效：
1. 在終端機中滑鼠右鍵 → Paste（貼上）
2. 或者使用終端機選單：Edit → Paste
3. 或者在 iTerm2 中使用 Cmd + V

---

## 有任何問題？

### 檢查日誌

查看應用日誌：
```bash
cd ~/starlink-card-system
cat app.log 2>/dev/null || echo "No log file"
docker-compose logs
```

### 重啓服務

```bash
cd ~/starlink-card-system
docker-compose down
docker-compose up -d
./start.sh
```

---

## 下一步：生產部署

本地測試成功後，參考：
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - 免費部署到雲端（15分鐘）
- **[TEAMS_SETUP.md](./TEAMS_SETUP.md)** - 整合 Teams Bot

---

**總結: 就三行命令，然後等它自己完成！** 💪
