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
    # 創建數據庫表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ 數據庫表已創建")
    print(f"✓ {settings.APP_NAME} v{settings.APP_VERSION} 已啟動")

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
