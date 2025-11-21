from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import ai, auth, jobs, chat 
from app.socket_server import socket_app


# 初始化 FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 設定 CORS (解決跨域問題)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


#註冊 AI 路由 (加上 prefix)
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Services"])

# 👇 註冊 Auth 路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"]) # 👈 註冊 Jobs
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Services"])
# 掛載 Socket.IO 到 /socket.io 路徑
app.mount("/socket.io", socket_app)

# 健康檢查路由 (Health Check)
@app.get("/")
async def root():
    return {
        "message": "Go Teach Backend is running! 🚀",
        "docs_url": "http://localhost:8000/docs"
    }

# 測試 DB 連線是否能在 API 中運作
@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "connected"}


