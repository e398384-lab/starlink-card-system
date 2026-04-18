"""
StarLink Card System - Main Application
FastAPI + PostgreSQL + Redis + Microsoft Teams Bot
Render.com 完全相容版本
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

# 導入模型
from app.models.base import Base, get_db_engine, create_tables, Merchant, Card, CardStatus
from app.api.v1 import admin, merchant, client

# 導入服務
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
 app.state.redis_client.ltrim("system:notifications", 0, 99) # Keep last 100
 except Exception as e:
 print(f"Failed to store notification: {e}")

# Make notify_manager available globally
import app.models.base

# === Render.com 啟動修復 ===
# 檢查必要環境變量
def check_env():
 """檢查並確認環境變量"""
 required = ["DATABASE_URL"]
 optional = ["REDIS_URL"]
 
 print("=" * 60)
 print("🔍 環境變量檢查")
 print("=" * 60)
 
 missing = []
 for env in required:
 if not os.getenv(env):
 missing.append(env)
 
 if missing:
 print(f"❌ 缺少必要變量: {missing}")
 return False
 
 if not os.getenv("PORT"):
 print("⚠️ PORT 未設置，使用默認值 10000")
 os.environ["PORT"] = "10000"
 
 print(f"✅ DATABASE_URL: {os.getenv('DATABASE_URL')[:30]}...")
 print(f"✅ REDIS_URL: {'已設置' if os.getenv('REDIS_URL') else '未設置'}")
 print(f"✅ PORT: {os.getenv('PORT')}")
 print("=" * 60)
 return True

# CORS 中間件
app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

# Include routers
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(merchant.router, prefix="/api/v1/merchant", tags=["merchant"])
app.include_router(client.router, prefix="/api/v1/client", tags=["client"])

# Health check endpoint
@app.get("/health")
def health_check():
 """Basic health check endpoint for Render.com"""
 db_status = "disconnected"
 redis_status = "disconnected"
 
 # Check database connection
 try:
 engine = get_db_engine()
 with engine.connect() as conn:
 conn.execute("SELECT 1")
 db_status = "connected"
 except Exception as e:
 print(f"Database health check failed: {e}")
 
 # Check Redis connection
 try:
 redis_url = os.getenv("REDIS_URL")
 if redis_url:
 redis_client = redis.from_url(redis_url)
 redis_client.ping()
 redis_status = "connected"
 else:
 redis_status = "not configured"
 except Exception as e:
 print(f"Redis health check failed: {e}")
 
 return {
 "status": "healthy" if db_status == "connected" else "unhealthy",
 "database": db_status,
 "redis": redis_status,
 "timestamp": datetime.now().isoformat()
 }

# Initialize tables endpoint
@app.post("/api/v1/admin/init-db")
def initialize_database():
 """Initialize database tables"""
 try:
 create_tables()
 return {"message": "Database tables created successfully", "status": "success"}
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

# Update global notify_manager function
app.models.base.notify_manager = notify_manager

@app.on_event("startup")
async def startup_event():
 """
 Render.com 啟動事件
 添加重試機制，確保在 Render 環境中穩定啟動
 """
 print("=" * 60)
 print("🚀 StarLink Card System - Starting up")
 print("=" * 60)
 
 # 檢查環境變量
 env_ok = check_env()
 if not env_ok:
 print("❌ Critical environment variables missing")
 raise RuntimeError("Cannot start without required environment variables")
 
 # 初始化 Redis（帶重試）
 max_retries = 3
 redis_connected = False
 
 for i in range(max_retries):
 try:
 print(f"📡 Connecting to Redis (attempt {i+1}/{max_retries})...")
 app.state.redis_client = redis.from_url(os.getenv("REDIS_URL"))
 app.state.redis_client.ping()
 redis_connected = True
 print("✅ Redis connected successfully")
 break
 except Exception as e:
 print(f"⚠ Redis connection failed (attempt {i+1}): {e}")
 if i < max_retries - 1:
 import asyncio
 await asyncio.sleep(2)
 
 if not redis_connected:
 print("⚠ Running without Redis - notifications disabled")
 app.state.redis_client = None
 
 # 初始化數據庫表（帶重試）
 db_initialized = False
 for i in range(max_retries):
 try:
 print(f"📊 Initializing database (attempt {i+1}/{max_retries})...")
 create_tables()
 db_initialized = True
 print("✅ Database tables created successfully")
 break
 except Exception as e:
 print(f"⚠ Database initialization failed (attempt {i+1}): {e}")
 if i < max_retries - 1:
 import asyncio
 await asyncio.sleep(2)
 
 if not db_initialized:
 print("⚠ Database initialization incomplete - app may have limited functionality")
 
 print("🎉 Startup completed successfully")
 print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
 """Shutdown event"""
 print("🛑 Shutting down StarLink Card System")

# Run the app
def run_app():
 """Run the FastAPI application - Render.com compatible"""
 port = int(os.getenv("PORT", "10000"))
 host = os.getenv("HOST", "0.0.0.0")
 
 print("=" * 60)
 print("🚀 Starting StarLink Card Platform")
 print("=" * 60)
 print(f"📡 Host: {host}")
 print(f"📡 Port: {port}")
 print(f"📡 URL: http://{host}:{port}")
 print("=" * 60)
 
 uvicorn.run(
 app,
 host=host,
 port=port,
 log_level="info",
 access_log=True
 )

if __name__ == "__main__":
 run_app()
