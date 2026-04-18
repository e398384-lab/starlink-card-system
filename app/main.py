"""
StarLink Card System - Main Application
FastAPI + PostgreSQL + Redis + Microsoft Teams Bot
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uvicorn
import redis
import json
from typing import Optional

# Import models
from app.models.base import Base, get_db_engine, create_tables, Merchant, Card, CardStatus
from app.api.v1 import admin, merchant, client

# Import services
from app.services.card_service import CardService
from app.services.financial_service import FinancialService

app = FastAPI(
    title="StarLink Card Platform API",
    description="A platform connecting merchants needing customers (A-class) with merchants having excess customers (B-class)",
    version="1.0.0"
)

# Global notification function
def notify_manager(message: str, level: str = "info"):
    """Global notification function for system events"""
    timestamp = datetime.now().isoformat()
    notification = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    print(f"[⚠️ NOTIFICATION] {json.dumps(notification)}")
    
    # Store in Redis for Teams Bot to retrieve
    try:
        if hasattr(app.state, 'redis_client') and app.state.redis_client:
            app.state.redis_client.lpush("system:notifications", json.dumps(notification))
            app.state.redis_client.ltrim("system:notifications", 0, 99)  # Keep last 100
    except Exception as e:
        print(f"Failed to store notification: {e}")

# Make notify_manager available globally
import app.models.base
app.models.base.notify_manager = notify_manager

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis setup
def setup_redis():
    """Setup Redis connection"""
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            app.state.redis_client = redis.from_url(redis_url)
            app.state.redis_client.ping()  # Test connection
            print("✅ Redis connected successfully")
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            app.state.redis_client = None
            return False
    else:
        print("⚠️  REDIS_URL not set, some features disabled")
        app.state.redis_client = None
        return False

# Include routers
app.include_router(admin.router, prefix="/api/v1")
app.include_router(merchant.router, prefix="/api/v1")
app.include_router(client.router, prefix="/api/v1")

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "StarLink Card Platform API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "api_docs": "/docs",
            "admin": "/api/v1/admin",
            "merchant": "/api/v1/merchant",
            "client": "/api/v1/client"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    redis_status = "connected" if app.state.redis_client else "disabled"
    
    return {
        "status": "healthy",
        "database": "connected",
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Teams Bot Integration (PORT 3978)
@app.post("/api/bot/messages")
async def teams_bot_webhook(request: dict):
    """
    Microsoft Teams Bot Webhook Handler
    Expects Bot Framework messages at endpoint: /api/bot/messages
    """
    try:
        # Process incoming message (simplified version)
        activity = request.get("activity", {})
        text = activity.get("text", "")
        from_id = activity.get("from", {}).get("id", "")
        
        if text.startswith("/"):
            # Bot command detected
            response = process_bot_command(text, from_id)
        else:
            response = process_bot_message(text, from_id)
            
        return {
            "type": "message",
            "text": response,
            "from": {"id": "bot", "name": "StarLink Bot"},
            "recipient": {"id": from_id},
            "replyToId": activity.get("id")
        }
    except Exception as e:
        print(f"Bot webhook error: {e}")
        return {"error": str(e)}

@app.post("/api/teams/webhook")
async def teams_webhook(request: dict):
    """
    Alternative Teams webhook endpoint for system commands
    """
    try:
        command = request.get("command", "")
        args = request.get("args", [])
        
        if command == "/status":
            return get_system_status()
        elif command == "/cards":
            return get_card_stats()
        elif command == "/exec":
            if not args:
                return {"error": "No command provided"}
            return execute_system_command(args[0])
        elif command == "/help":
            return get_help_message()
        else:
            return {"message": f"Unknown command: {command}. Type /help for available commands"}
    except Exception as e:
        return {"error": str(e)}

def process_bot_command(text: str, user_id: str) -> str:
    """Process bot command like /status, /cards, /exec"""
    parts = text.strip().split()
    command = parts[0].lower()
    
    if command == "/status":
        return get_system_status_text()
    elif command == "/cards":
        return get_card_stats_text()
    elif command == "/exec":
        if len(parts) < 2:
            return "Usage: /exec <command>"
        return execute_system_command(parts[1])
    elif command == "/help":
        return get_help_message_text()
    else:
        return f"Unknown command: {command}. Type /help for available commands"

def process_bot_message(text: str, user_id: str) -> str:
    """Process regular message (not a command)"""
    return f"Received: {text}. Type /help for available commands"

def get_system_status_text() -> str:
    """Get system status for Teams Bot"""
    try:
        from app.models.base import get_db_engine
        engine = get_db_engine()
        
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM cards").scalar()
            card_count = result
            
            result = conn.execute("SELECT COUNT(*) FROM merchants").scalar()
            merchant_count = result
            
        return (
            f"🟢 System Status:\n"
            f"• Total Cards: {card_count}\n"
            f"• Total Merchants: {merchant_count}\n"
            f"• Database: Connected\n"
            f"• Service: Running\n"
            f"• Timestamp: {datetime.now().isoformat()}\n"
        )
    except Exception as e:
        return f"❌ Database query failed: {e}"

def get_card_stats_text() -> str:
    """Get card statistics"""
    try:
        from app.models.base import get_db_engine, CardStatus
        engine = get_db_engine()
        
        with engine.connect() as conn:
            # Get status distribution
            result = conn.execute("SELECT status, COUNT(*) FROM cards GROUP BY status").fetchall()
            status_counts = {row[0]: row[1] for row in result}
            
            total = sum(status_counts.values())
            
        output = f"📊 Card Statistics (Total: {total}):\n"
        for status in CardStatus:
            count = status_counts.get(status.value, 0)
            percentage = (count / total * 100) if total > 0 else 0
            output += f"• {status.value}: {count} ({percentage:.1f}%)\n"
        
        return output
    except Exception as e:
        return f"❌ Statistics query failed: {e}"

def execute_system_command(command: str) -> str:
    """Execute system command (limited commands only)"""
    # Security: Only allow specific safe commands
    allowed_commands = ["ls", "df", "free", "ps", "top", "docker", "date", "uptime"]
    
    parts = command.strip().split()
    cmd_name = parts[0]
    
    if cmd_name not in allowed_commands:
        return f"❌ Command not allowed: {cmd_name}\n\nAllowed: {', '.join(allowed_commands)}"
    
    try:
        import subprocess
        import shlex
        
        # Security: Use timeout and limit output
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/"
        )
        
        output = result.stdout or result.stderr
        
        # Limit output length
        if len(output) > 1500:
            output = output[:1500] + "\n...(truncated)"
        
        if result.returncode == 0:
            return f"✅ Output:\n```\n{output}\n```"
        else:
            return f"❌ Command failed (code {result.returncode}):\n{output}"
    except subprocess.TimeoutExpired:
        return "❌ Command timed out (30s limit)"
    except Exception as e:
        return f"❌ Execution failed: {e}"

def get_help_message_text() -> str:
    """Get help message for Teams Bot"""
    return (
        "🤖 StarLink Bot Commands:\n\n"
        "/status - System health and statistics\n"
        "/cards - Card inventory and status distribution\n"
        "/exec <command> - Execute system command (limited set)\n"
        "/help - Show this help message\n\n"
        "Examples:\n"
        "/exec ls -la\n"
        "/exec df -h\n"
        "/exec docker ps\n"
        "/exec free -m"
    )

def get_help_message() -> dict:
    """Get help message as dict"""
    return {"message": get_help_message_text()}

def get_system_status() -> dict:
    """Get system status as dict"""
    return {
        "system": "StarLink Card Platform",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "commands": ["/status", "/cards", "/exec", "/help"]
    }

def get_card_stats() -> dict:
    """Get card statistics as dict"""
    try:
        from app.models.base import get_db_engine, CardStatus
        engine = get_db_engine()
        
        with engine.connect() as conn:
            result = conn.execute("SELECT status, COUNT(*) FROM cards GROUP BY status").fetchall()
            status_counts = {row[0]: row[1] for row in result}
            
        return {
            "stats": status_counts,
            "total": sum(status_counts.values())
        }
    except Exception as e:
        return {"error": str(e)}

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize database and Redis"""
    print("🚀 Starting StarLink Card Platform...")
    
    # Setup database
    try:
        engine = get_db_engine()
        create_tables()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
    
    # Setup Redis
    setup_redis()
    
    # Notify manager
    notify_manager("System started successfully", "info")
    print("🎉 StarLink Card Platform is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    notify_manager("System shutting down", "warning")
    print("👋 StarLink Card Platform shutdown complete")

def run_app():
    """Run the FastAPI application"""
    # Get port and host from environment, defaults for Render.com
    port = int(os.getenv("PORT", "10000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Environment variables check
    required_env = ["DATABASE_URL"]
    missing = [env for env in required_env if not os.getenv(env)]
    
    if missing:
        print(f"⚠️  Warning: Missing environment variables: {missing}")
        print("   System can start but database connection will fail")
    
    print(f"📡 Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_app()