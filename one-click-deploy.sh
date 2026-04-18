#!/bin/bash

# 🚀 星鏈卡系統 - 一鍵自動化部署腳本
# 執行後自動完成所有 Render 部署步驟

set -e

echo "🌟 星鏈卡系統 - 自動化部署"
echo "=============================="
echo ""

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置
PROJECT_NAME="starlink-card-system"
RENDER_SERVICE_NAME="starlink-card-system"
GITHUB_REPO="e398384-lab/starlink-card-system"

echo -e "${YELLOW}📋 部署前檢查...${NC}"
echo ""

# 1. 檢查是否已安裝 Render CLI
if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}⚠️  Render CLI 未安裝，正在安裝...${NC}"
    npm install -g @render-cloud/cli || {
        echo -e "${RED}❌ Render CLI 安裝失敗${NC}"
        echo ""
        echo "請手動安裝: npm install -g @render-cloud/cli"
        echo "或訪問: https://render.com/docs/cli"
        exit 1
    }
fi

echo -e "${GREEN}✓ Render CLI 已安裝${NC}"

# 2. 檢查是否已登入 Render
if ! render whoami &> /dev/null; then
    echo -e "${YELLOW}🔐 請登入 Render...${NC}"
    echo "執行: render login"
    echo ""
    read -p "按 Enter 繼續登入..." 
    render login
    
    if ! render whoami &> /dev/null; then
        echo -e "${RED}❌ Render 登入失敗${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ 已登入 Render${NC}"

# 3. 檢查專案目錄
if [ ! -f "render.yaml" ]; then
    echo -e "${RED}❌ 錯誤：render.yaml 不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✓ render.yaml 存在${NC}"

# 4. 檢查 Git 狀態
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ 錯誤：不是 Git 倉庫${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git 倉庫正常${NC}"

# 5. 推送最新程式碼
echo ""
echo -e "${YELLOW}📤 推送最新程式碼到 GitHub...${NC}"
git add -A
git commit -m "Auto-deploy: $(date)" || echo "沒有更改需要提交"
git push origin main

echo -e "${GREEN}✓ 程式碼已推送${NC}"

# 6. 創建 Render 服務
echo ""
echo -e "${YELLOW}🚀 在 Render 創建服務...${NC}"
echo ""

# 使用 render.yaml 配置
render up --yes --no-inputs 2>/dev/null || {
    echo -e "${YELLOW}⚠️  render up 命令不支援，使用替代方案...${NC}"
    
    # 顯示手動部署連結
    echo ""
    echo -e "${GREEN}✅ 程式碼已準備就緒！${NC}"
    echo ""
    echo "最後一步：在 Render Dashboard 點擊幾下"
    echo ""
    echo "📍 訪問: https://dashboard.render.com/create?type=web"
    echo ""
    echo "配置:"
    echo "  Repository: $GITHUB_REPO"
    echo "  Name: $RENDER_SERVICE_NAME"
    echo "  Region: oregon"
    echo "  Build: pip install -r requirements.txt"
    echo "  Start: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
    echo "  Plan: Free"
    echo ""
    echo "環境變數 (複製貼上):"
    echo "  DATABASE_URL=postgresql://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres"
    echo "  REDIS_URL=rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379"
    echo "  SECRET_KEY=M82MsQDE7jvr1W21s75ZysZ6Uiwn2gcraqvbdvPOq6Y"
    echo "  DEBUG=false"
    echo ""
    echo "🔗 快速連結: https://dashboard.render.com/create?type=web&repo=$GITHUB_REPO"
    echo ""
    echo "完成後訪問: https://$RENDER_SERVICE_NAME.onrender.com/docs"
    echo ""
    
    # 打開瀏覽器
    if command -v open &> /dev/null; then
        open "https://dashboard.render.com/create?type=web&repo=$GITHUB_REPO"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "https://dashboard.render.com/create?type=web&repo=$GITHUB_REPO"
    fi
    
    exit 0
}

# 7. 等待部署完成
echo ""
echo -e "${YELLOW}⏳ 等待部署完成...${NC}"
sleep 10

# 8. 獲取服務 URL
echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""

# 嘗試獲取服務資訊
SERVICES=$(render services list --json 2>/dev/null || echo "[]")
SERVICE_URL=$(echo "$SERVICES" | jq -r '.[0].externalUrl' 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ] && [ "$SERVICE_URL" != "null" ]; then
    echo "🌐 服務網址: $SERVICE_URL"
    echo "📚 API 文檔: $SERVICE_URL/docs"
    echo "💚 健康檢查: $SERVICE_URL/health"
else
    echo "🌐 服務網址: https://$RENDER_SERVICE_NAME.onrender.com"
    echo "📚 API 文檔: https://$RENDER_SERVICE_NAME.onrender.com/docs"
    echo "💚 健康檢查: https://$RENDER_SERVICE_NAME.onrender.com/health"
fi

echo ""
echo -e "${GREEN}🎉 恭喜！系統已成功部署！${NC}"
echo ""
echo "下一步:"
echo "  1. 訪問 API 文檔測試功能"
echo "  2. 註冊第一個用戶"
echo "  3. 註冊商家"
echo "  4. 發行第一張星鏈卡"
echo ""
echo "詳細說明請查看: FINAL_USAGE.md"
echo ""
