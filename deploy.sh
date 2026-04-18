#!/bin/bash

# StarLink Card System 快速部署腳本

echo "🚀 星鏈卡系統 - 快速部署腳本"
echo "=============================="
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查是否在專案目錄
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 錯誤：請在專案根目錄執行此腳本${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 檢查環境...${NC}"

# 步驟 1: 安裝依賴
echo ""
echo "📦 步驟 1: 安裝 Python 依賴..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依賴安裝成功${NC}"
else
    echo -e "${RED}❌ 依賴安裝失敗${NC}"
    exit 1
fi

# 步驟 2: 檢查環境變數
echo ""
echo "🔐 步驟 2: 檢查環境變數..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  警告：.env 檔案不存在${NC}"
    echo "請創建 .env 檔案並填寫必要的環境變數"
    echo ""
    echo "必需的環境變數:"
    echo "  - DATABASE_URL"
    echo "  - REDIS_URL"
    echo "  - SECRET_KEY"
    echo ""
    read -p "是否要創建 .env 範本檔案？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env 2>/dev/null || echo "請手動創建 .env 檔案"
    fi
else
    echo -e "${GREEN}✓ .env 檔案存在${NC}"
fi

# 步驟 3: 測試數據庫連接
echo ""
echo "🗄️  步驟 3: 測試數據庫連接..."
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config.settings import settings

async def test_db():
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            await conn.execute('SELECT 1')
        print('✓ 數據庫連接成功')
        return True
    except Exception as e:
        print(f'❌ 數據庫連接失敗: {e}')
        return False

result = asyncio.run(test_db())
exit(0 if result else 1)
"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  警告：數據庫連接測試失敗，但部署仍可繼續${NC}"
fi

# 步驟 4: 啟動本地服務（可選）
echo ""
echo "🎯 步驟 4: 選擇操作"
echo "  1) 本地測試啟動"
echo "  2) 推送到 GitHub（需要先設置遠端倉庫）"
echo "  3) 僅準備部署（不啟動）"
echo ""
read -p "請選擇 (1/2/3): " -n 1 -r
echo

case $REPLY in
    1)
        echo ""
        echo "🚀 啟動本地服務..."
        echo "訪問 http://localhost:8000/docs 查看 API 文檔"
        uvicorn app.main:app --reload
        ;;
    2)
        echo ""
        echo "📤 準備推送到 GitHub..."
        
        # 檢查是否已初始化 Git
        if [ ! -d ".git" ]; then
            echo "初始化 Git 倉庫..."
            git init
            git add .
            git commit -m "Initial commit: StarLink Card System"
            git branch -M main
            echo ""
            echo -e "${YELLOW}請執行以下命令添加遠端倉庫:${NC}"
            echo "  git remote add origin https://github.com/YOUR_USERNAME/starlink-card-system.git"
            echo "  git push -u origin main"
        else
            echo "添加所有檔案..."
            git add .
            echo "提交更改..."
            git commit -m "Update: StarLink Card System" || echo "沒有更改需要提交"
            echo ""
            echo -e "${YELLOW}請執行以下命令推送:${NC}"
            echo "  git push"
        fi
        ;;
    3)
        echo ""
        echo -e "${GREEN}✓ 系統已準備就緒！${NC}"
        echo ""
        echo "下一步:"
        echo "  1. 推送到 GitHub: git push"
        echo "  2. 在 Render 創建 Web Service"
        echo "  3. 連接 GitHub 倉庫"
        echo "  4. 添加環境變數"
        echo "  5. 部署！"
        echo ""
        echo "詳細部署說明請查看 DEPLOYMENT.md"
        ;;
    *)
        echo "無效選擇，退出腳本"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 完成！${NC}"
