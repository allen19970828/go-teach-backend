# app/init_db.py
import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine

# 修正路徑以讀取 app 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import DATABASE_URL
from app.models.base import Base
# 必須匯入所有 Model，SQLAlchemy 才知道要建哪些表
from app.models.user import User, SchoolProfile, TeacherProfile
from app.models.job import Job
from app.models.lesson import LessonPlan
from app.models.application import Application
from app.models.chat import ChatRoom, Message


async def init_models():
    print("🔄 正在連接資料庫並建立資料表...")
    
    # 針對 Supabase Pooler 的設定
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"statement_cache_size": 0}
    )

    async with engine.begin() as conn:
        # 這裡會自動執行 CREATE TABLE IF NOT EXISTS
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ 資料表建立完成！")
    print("   - Users (使用者)")
    print("   - SchoolProfiles / TeacherProfiles (詳細資料)")
    print("   - Jobs (職缺 + 向量欄位)")
    print("   - LessonPlans (AI 教案)")

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(init_models())
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")