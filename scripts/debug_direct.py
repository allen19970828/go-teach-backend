import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# ==========================================
# 👇 請把你的 Supabase 連線字串貼在這裡 (記得加上 +asyncpg)
# 格式: postgresql+asyncpg://postgres.帳號:密碼@aws-0-xxx.pooler.supabase.com:6543/postgres
# ==========================================
DB_URL = "postgresql://postgres:goteach_database@db.asolxfqtqymytwxhqbvb.supabase.co:5432/postgres" 

async def test_direct():
    print(f"🔌 準備連接到: {DB_URL[:20]}...") # 只印出前段，保護密碼
    
    if "請貼上" in DB_URL:
        print("❌ 請先修改程式碼，填入正確的 DB_URL！")
        return

    if "postgresql://" in DB_URL and "+asyncpg" not in DB_URL:
         print("⚠️ 偵測到缺少 driver，正在自動修正...")
         real_url = DB_URL.replace("postgresql://", "postgresql+asyncpg://")
    else:
         real_url = DB_URL

    # Supabase Transaction Pooler 專用設定
    connect_args = {"statement_cache_size": 0}

    try:
        engine = create_async_engine(real_url, echo=False, connect_args=connect_args)
        
        print("⏳正在發送連線請求...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"\n✅ 恭喜！連線成功！")
            print(f"🐘 資料庫版本: {version}")
            
            # 順便測試 Vector
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.commit()
                print("✅ pgvector 擴充套件確認 OK")
            except Exception as e:
                print(f"⚠️ Vector 警告: {e}")

    except Exception as e:
        print(f"\n❌ 連線失敗！錯誤原因如下：")
        print("-" * 20)
        print(e)
        print("-" * 20)
        
        # 常見錯誤診斷
        err_msg = str(e)
        if "password authentication failed" in err_msg:
            print("💡 診斷: 密碼錯誤。")
            print("   -> 請確認是「資料庫密碼」(Database Password)，而不是 Supabase 登入密碼。")
            print("   -> 如果密碼包含 @ : / ? # 等符號，必須進行 URL Encode 轉換。")
        elif "nodename nor servname provided" in err_msg or "NXDOMAIN" in err_msg:
            print("💡 診斷: 找不到主機。")
            print("   -> 請檢查連線字串中的 host (xxx.supabase.com) 是否複製完整。")
        elif "Connection refused" in err_msg or "timeout" in err_msg:
             print("💡 診斷: 連線被拒或超時。")
             print("   -> 可能是公司/學校防火牆擋住了 Port 6543/5432。")

    finally:
        if 'engine' in locals():
            await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_direct())