import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# 1. 強制定位 .env 檔案 (腳本所在目錄 -> 上一層 -> .env)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# 2. 載入環境變數
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"📂 已讀取環境變數檔: {ENV_PATH}")
else:
    print(f"❌ 找不到檔案: {ENV_PATH}")
    print("請確認檔名是否為 '.env' (不要有 .txt 副檔名)")
    sys.exit(1)

def get_fixed_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("❌ 錯誤: .env 檔案中找不到 'DATABASE_URL' 設定")
        print("請確認內容格式為: DATABASE_URL=\"postgresql+asyncpg://...\"")
        sys.exit(1)
    
    # 自動補正 driver
    if url.startswith("postgresql://"):
        print("🔧 自動修正連線字串: 加上 +asyncpg")
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    
    return url

async def test_connection():
    url = get_fixed_url()
    print(f"🔌 正在嘗試連接資料庫...")

    connect_args = {"statement_cache_size": 0}

    try:
        engine = create_async_engine(url, echo=False, connect_args=connect_args)

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ 連線成功！")
            print(f"🐘 資料庫版本: {version}")

            print("-" * 30)
            print("🔍 檢查 pgvector...")
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.commit()
                print("✅ pgvector 功能已就緒！")
            except Exception as e:
                print(f"⚠️ pgvector 訊息: {e}")

    except Exception as e:
        print(f"❌ 連線失敗: {e}")
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(test_connection())