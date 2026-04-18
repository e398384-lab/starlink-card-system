from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import os
from dotenv import load_dotenv
from app.models.base import get_db_engine, create_tables

load_dotenv()

app = FastAPI(title="StarLink Card System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_url = os.getenv("REDIS_URL")
if redis_url:
    redis_client = redis.from_url(redis_url, decode_responses=True)
else:
    redis_client = None

# Include API routers
from app.api.v1 import admin, merchant
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(merchant.router, prefix="/api/v1/merchant", tags=["merchant"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        engine = get_db_engine()
        create_tables(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

@app.get("/")
async def root():
    return {"message": "StarLink Card System is running"}

@app.get("/health")
async def health_check():
    # Check database connection
    db_status = "disconnected"
    try:
        engine = get_db_engine()
        # Try to connect
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy", 
        "redis": redis_client is not None,
        "database": db_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))