from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.database import Base, engine
import asyncio

# 導入所有路由
from app.routers import auth, merchants, cards, teams

# 創建 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="星鏈卡權益系統 - 連接需要新客的商家與客戶過剩的商家，平台收取 4% 交易費",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(merchants.router, prefix="/api/v1")
app.include_router(cards.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    import traceback
    print("=" * 50)
    print("🚀 應用啟動中...")
    print(f"📍 環境：{'Debug' if settings.DEBUG else 'Production'}")
    print(f"🗄️  DATABASE_URL: {settings.DATABASE_URL[:60]}...")
    print(f"🔑 SECRET_KEY 長度：{len(settings.SECRET_KEY)}")
    
    try:
        print("🔗 嘗試連接資料庫...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ 數據庫表已創建/驗證成功")
    except Exception as e:
        print(f"❌ 數據庫連接/創建失敗: {e}")
        print("📋 錯誤堆疊:")
        print(traceback.format_exc())
        # 不要退出，嘗試繼續
    
    try:
        print("🔗 嘗試連接 Redis...")
        import aioredis
        redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        print("✅ Redis 連接成功")
        await redis_client.close()
    except Exception as e:
        print(f"❌ Redis 連接失敗: {e}")
    
    print("=" * 50)
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} 啟動完成")
    print("=" * 50)

@app.get("/")
async def root():
    """根端點"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
