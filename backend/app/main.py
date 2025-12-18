"""
HistoriaQuest API - FastAPI 后端
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routers import (
    users_router,
    lessons_router,
    chat_router,
    figures_router,
    social_router,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 {settings.app_name} is starting...")
    yield
    # 关闭时
    print(f"👋 {settings.app_name} is shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="历史学习游戏化应用 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users_router, prefix="/api")
app.include_router(lessons_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(figures_router, prefix="/api")
app.include_router(social_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to HistoriaQuest API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
