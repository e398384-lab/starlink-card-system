from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Merchant
from app.schemas import UserRegister, UserLogin, UserResponse, Token, MessageResponse
from app.auth import create_access_token, get_current_user
from passlib.context import CryptContext
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["認證"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用戶註冊"""
    # 檢查郵件是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 如果指定了 merchant_id，檢查商家是否存在
    merchant_id = None
    if user_data.merchant_id:
        result = await db.execute(
            select(Merchant).where(Merchant.id == user_data.merchant_id)
        )
        merchant = result.scalar_one_or_none()
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Merchant not found"
            )
        merchant_id = user_data.merchant_id
    
    # 創建新用戶
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        merchant_id=merchant_id,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # 創建訪問令牌
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=None
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(new_user.id)
    }

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用戶登入"""
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # 創建訪問令牌
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=None
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """獲取當前用戶資訊"""
    return current_user
