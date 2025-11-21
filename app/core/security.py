from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 設定密碼加密演算法
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 設定 JWT 參數 (開發用預設值，上線請改 .env)
# SECRET_KEY = "DEV_SECRET_KEY_PLEASE_CHANGE_IN_PROD" 
# ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token 有效期 1 天

def create_access_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # 👇 關鍵：使用 settings.SECRET_KEY 簽名
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)