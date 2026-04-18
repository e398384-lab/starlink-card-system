#!/bin/bash
# 超簡單啟動腳本 - 當你再次啟動時只需要這個

cd ~/starlink-card-system

# 檢查 Docker 是否運行
if ! docker info &> /dev/null; then
    echo "請先啟動 Docker Desktop 應用程式"
    echo "然後再執行這個腳本"
    exit 1
fi

echo "🚀 啟動 StarLink Card System..."
docker-compose up -d

sleep 3

echo "🌐 API 將在 5 秒後可用..."
echo ""
echo "訪問："
echo "  📚 API 文件: http://localhost:10000/docs"
echo "  🏥 健康檢查: http://localhost:10000/health"
echo ""
echo "保持此視窗開啟，按 Ctrl+C 停止"

uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload