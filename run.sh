#!/bin/bash
# Run script for StarLink Card System

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please run: cp .env.example .env"
    echo "Then edit .env with your credentials"
    exit 1
fi

# Load environment variables (if using local PostgreSQL and Redis)
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

# Check PostgreSQL and Redis if running locally with docker-compose
if command -v docker-compose &> /dev/null; then
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✓ Docker services running${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker services not running. Starting...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✓ Docker services started${NC}"
        sleep 5  # Wait for services to be ready
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Virtual environment not found. Running Python directly...${NC}"
fi

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ DATABASE_URL not set in .env file${NC}"
    echo "Please add DATABASE_URL to .env file"
    echo "Example for local PostgreSQL:"
    echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/starlink"
    exit 1
fi

echo "Deploying the binding between the web server and the environment"
# Build service
python -m py_compile app/main.py || echo "Compilation attempt failed, but continuing..."

# Initialize database
echo "Initializing database..."
python -c "
import sys
sys.path.insert(0, '.')
from app.models.base import create_tables
try:
    create_tables()
    print('✅ Database initialized')
except Exception as e:
    print(f'Database init error: {e}')
    sys.exit(1)
"

# Determine listen port
PORT=${PORT:-10000}
HOST=${HOST:-0.0.0.0}

echo "Starting FastAPI server..."
echo "========================"
echo "Server: $HOST:$PORT"
echo "API Docs: http://localhost:$PORT/docs"
echo "Health: http://localhost:$PORT/health"
echo "========================"
echo ""
echo "🚀 Starting uvicorn..."

# Start the application
exec uvicorn app.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --reload \
    --log-level "info"