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
import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入各服务模块路由
from backend.services.auth_service import router as auth_router
from backend.services.user_service import router as user_router
from backend.services.tag_service import router as tag_router
from backend.services.matching_service import router as matching_router
from backend.services.metadata_service import router as metadata_router
from backend.services.ai_service import router as ai_router
from backend.services.database_service import init_database, close_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 简化版本"""
    # 启动时验证
    print("🚀 启动社交匹配系统API服务器")
    print("=" * 50)
    
    # 简单验证数据库连接（可选）
    try:
        from backend.services.database_service import get_supabase
        client = get_supabase()
        print("✅ 数据库连接验证成功")
    except Exception as e:
        print(f"⚠️ 数据库连接验证失败: {e}")
        # 不中断启动，让服务继续运行
    
    yield
    
    # 关闭时清理（实际上Supabase客户端不需要显式清理）
    print("👋 API服务器已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="社交匹配系统API",
    description="基于FastAPI的模块化社交匹配系统，支持用户认证、档案管理、标签建模和智能匹配",
    version="1.0.0",
    lifespan=lifespan
)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "database": "skipped",  # 暂时跳过数据库检查
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# 添加一个简单的测试端点
@app.get("/test")
async def test_endpoint():
    """简单的测试端点"""
    return {"message": "API server is working", "timestamp": datetime.datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Linker 社交匹配系统API",
        "version": "0.0.1",
        "docs": "/docs",
        "health": "/health",
        "test": "/test"
    }

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
app.include_router(ai_router, prefix="/api/ai", tags=["AI服务"])

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
    import os
    port = int(os.getenv("API_PORT", 5000))
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 