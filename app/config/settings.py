from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:!@Ar20417b1@db.srpuwkcieefgslryedkb.supabase.co:5432/postgres"
    
    # Redis
    REDIS_URL: str = "rediss://default:gQAAAAAAAYvKAAIocDEwNDU1YWNlNTBkZGI0MTgyYWVhYjIyMGE5NWY1ZmNjMnAxMTAxMzIy@welcome-fowl-101322.upstash.io:6379"
    
    # Microsoft Teams Bot
    TEAMS_APP_ID: Optional[str] = None
    TEAMS_APP_PASSWORD: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Application
    APP_NAME: str = "StarLink Card System"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
