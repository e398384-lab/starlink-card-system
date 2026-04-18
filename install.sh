#!/bin/bash
# Install script for StarLink Card System

set -e

echo "🚀 Starting StarLink Card System installation..."
echo "=================================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python version $python_version is compatible"
else
    echo "❌ Python version $python_version is too old. Requires 3.8+"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists, create from template if not
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created - please edit with your credentials"
else
    echo "⚠️  .env file already exists"
fi

# Make scripts executable
echo "Setting up scripts..."
chmod +x scripts/*.sh 2>/dev/null || echo "No scripts directory found"
chmod +x run.sh

echo ""
echo "🎉 Installation complete!"
echo "="
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   - DATABASE_URL (from Supabase)"
echo "   - REDIS_URL (from Upstash or local Redis)"
echo "   - SECRET_KEY (generate random string)"
echo ""
echo "2. Start PostgreSQL and Redis (if using local):"
echo "   docker-compose up -d"
echo ""
echo "3. Initialize database:"
echo "   curl -X POST http://localhost:10000/api/v1/admin/init-db"
echo ""
echo "4. Start the application:"
echo "   ./run.sh"
echo ""
echo "5. Access the API docs:"
echo "   http://localhost:10000/docs"