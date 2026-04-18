from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import os
from dotenv import load_dotenv

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

@app.get("/")
async def root():
    return {"message": "StarLink Card System is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "redis": redis_client is not None}

# Include API routers (to be created)
# from app.api.v1 import admin, merchant, client
# app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
# app.include_router(merchant.router, prefix="/api/v1/merchant", tags=["merchant"])
# app.include_router(client.router, prefix="/api/v1/client", tags=["client"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))