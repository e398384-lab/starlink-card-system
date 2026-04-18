#!/bin/bash
# StarLink Card System - macOS 超簡單安裝腳本
# 只需要貼上這個檔案內容到終端機

set -e

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🍎 Mac專用：StarLink Card System 超簡單安裝"
echo "================================================"
echo ""

# 1. 檢查是否已安裝 Homebrew
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}⚠️  需要先安裝 Homebrew...${NC}"
    echo "請先訪問: https://brew.sh"
    echo "或在終端機貼上以下命令:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
else
    echo -e "${GREEN}✓ Homebrew 已安裝${NC}"
fi

# 2. 安裝 Python 3.11 (如果還沒有)
if ! command -v python3 &> /dev/null; then
    echo "安裝 Python 3.11..."
    brew install python@3.11
    echo -e "${GREEN}✓ Python 3.11 已安裝${NC}"
else
    python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    echo -e "${GREEN}✓ Python $python_version 已安裝${NC}"
fi

# 3. 安裝 Docker Desktop (推薦最簡單的方式)
echo ""
echo "Docker 安裝檢查..."
if ! command -v docker &> /dev/null; then
    echo "下載 Docker Desktop for Mac..."
    echo "請訪問: https://www.docker.com/products/docker-desktop/"
    echo "下載 .dmg 檔案，拖曳到應用程式資料夾即可"
    echo ""
    echo "或是用 Homebrew 安裝:"
    echo "  brew install --cask docker"
    
    read -p "是否自動安裝 Docker？ (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "安裝 Docker Desktop..."
        brew install --cask docker
        echo ""
        echo -e "${YELLOW}⚠️  安裝完成後，請手動打開 Docker Desktop 應用程式${NC}"
        echo "Docker Desktop 完全啟動後，再按 Enter 繼續..."
        read
    else
        echo "請先安裝 Docker Desktop 後再重新執行此腳本"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Docker 已安裝${NC}"
fi

# 4. 等待 Docker 啟動
echo ""
echo "檢查 Docker 是否正在運行..."
timeout=60
elapsed=0
while ! docker info &> /dev/null; do
    if [ $elapsed -ge $timeout ]; then
        echo -e "${RED}❌ Docker 未在 60 秒內啟動${NC}"
        echo "請手動打開 Docker Desktop 應用程式，等待完全啟動後再試一次"
        exit 1
    fi
    echo -n "等待 Docker 啟動.."
    sleep 5
    elapsed=$((elapsed + 5))
done
echo -e "${GREEN}✓ Docker 已啟動${NC}"

# 5. 創建項目目錄
PROJECT_DIR="$HOME/starlink-card-system"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  項目目錄已存在: $PROJECT_DIR${NC}"
    read -p "是否覆蓋現有項目？ (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "移除現有目錄..."
        rm -rf "$PROJECT_DIR"
    else
        echo "使用現有目錄"
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 6. 創建核心文件
echo ""
echo "創建核心文件..."

# 6.1. app/main.py
cat << 'EOF' > app/main.py
from fastapi import FastAPI
from sqlalchemy.orm import Session
import os
import uvicorn

app = FastAPI(title="StarLink Card Platform")

@app.get("/")
def root():
    return {"message": "StarLink Card Platform is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# 6.2. requirements.txt
cat << 'EOF' > requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
EOF

# 6.3. docker-compose.yml (最簡單版本)
cat << 'EOF' > docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: starlink
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass redis123

volumes:
  postgres_data:
EOF

# 6.4. .env.example
cat << 'EOF' > .env.example
# For local Docker development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/starlink
REDIS_URL=redis://:redis123@localhost:6379
EOF

# 6.5. install.sh
cat << 'EOS' > install.sh
#!/bin/bash
pip install -r requirements.txt
echo "✅ 安裝完成！"
EOS
chmod +x install.sh

# 6.6. run.sh  
cat << 'EOS' > run.sh
#!/bin/bash
uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload
EOS
chmod +x run.sh

# 7. 啟動 Docker
echo ""
echo "啟動 PostgreSQL and Redis..."
docker-compose up -d

# 等待服務啟動
echo "等待資料庫啟動..."
sleep 5

# 8. 安裝 Python 依賴
echo ""
echo "安裝 Python 依賴..."
pip3 install -r requirements.txt

# 9. 複製環境變量
cp .env.example .env

# 10. 啟動應用
echo ""
echo -e "${GREEN}✅ 安裝完成！${NC}"
echo ""
echo "啟動 StarLink Card System..."
echo "API 將在 5-10 秒後可用..."
echo ""
echo "訪問以下網址："
echo "  📚 API 文件: http://localhost:10000/docs"
echo "  🏥 健康檢查: http://localhost:10000/health"
echo ""
echo "按 Ctrl+C 停止服務"
echo ""

# 啟動服務
uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload