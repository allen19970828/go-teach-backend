# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase 連線字串格式 (請在 .env 設定 DATABASE_URL)
# 格式: postgresql+asyncpg://user:password@host:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # 開發模式開啟 SQL Log，上線後關閉
    future=True
)

# 建立非同步 Session 工廠
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    """
    FastAPI Dependency: 每個 Request 取得一個 DB Session
    """
    async with AsyncSessionLocal() as session:
        yield session