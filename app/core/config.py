"""FastAPI 設定"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LINE 相關
    LINE_CHANNEL_ACCESS_TOKEN: Optional[str] = None
    LINE_CHANNEL_SECRET: Optional[str] = None
    LIFF_ID: Optional[str] = None
    
    # 資料庫
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/starlink"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # 應用設定
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 卡片設定
    TRANSFER_TIMEOUT_HOURS: int = 48
    
    class Config:
        env_file = ".env"

settings = Settings()
