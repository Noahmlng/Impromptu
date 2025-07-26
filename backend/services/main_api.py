#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
社交匹配系统统一API入口
基于FastAPI框架的模块化架构
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入各服务模块路由
from backend.services.auth_service import router as auth_router
from backend.services.user_service import router as user_router
from backend.services.tag_service import router as tag_router
from backend.services.matching_service import router as matching_router
from backend.services.metadata_service import router as metadata_router
from backend.services.database_service import init_database, close_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 启动社交匹配系统API服务器")
    print("=" * 50)
    await init_database()
    yield
    # 关闭时清理
    await close_database()
    print("👋 API服务器已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="社交匹配系统API",
    description="基于FastAPI的模块化社交匹配系统，支持用户认证、档案管理、标签建模和智能匹配",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由模块
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(user_router, prefix="/api/users", tags=["用户"])
app.include_router(tag_router, prefix="/api/tags", tags=["标签"])
app.include_router(matching_router, prefix="/api/match", tags=["匹配"])
app.include_router(metadata_router, prefix="/api/metadata", tags=["元数据"])

# 根路径健康检查
@app.get("/")
async def root():
    return {"message": "社交匹配系统API正在运行", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "message": "社交匹配系统API运行正常",
        "version": "1.0.0"
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    print(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "message": "系统出现异常，请稍后重试"
        }
    )

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    ) 