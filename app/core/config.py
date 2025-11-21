import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 確保能讀取到 .env
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Go Teach Backend"
    API_V1_STR: str = "/api/v1"
    
    # 驗證必要變數，讀不到會報錯
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    # 👇 關鍵修正：補上這兩行 JWT 設定！
    SECRET_KEY: str = "DEV_SECRET_KEY_PLEASE_CHANGE_IN_PROD" 
    ALGORITHM: str = "HS256"
    
    # CORS 設定 (允許前端連線)
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",  # Vue 前端預設 Port
        "http://localhost:8000",
        "*" # 開發階段先全開，方便測試
    ]

    class Config:
        case_sensitive = True

settings = Settings()