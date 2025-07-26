#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu 全栈应用

结合前端静态文件服务和后端API的完整应用
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入原有的后端API
from backend.services.main_api import app as backend_app

# 创建新的FastAPI应用
app = FastAPI(
    title="Impromptu 社交匹配系统",
    description="前端+后端完整应用",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 检查是否有构建好的前端文件
frontend_static = Path("frontend/out")
frontend_public = Path("frontend/public")

# 优先使用 Next.js 静态导出文件
if frontend_static.exists():
    # 挂载静态文件（包括 _next 目录的资源）
    app.mount("/static", StaticFiles(directory=str(frontend_static)), name="static")
    
    # 挂载 _next 静态资源
    next_static_path = frontend_static / "_next"
    if next_static_path.exists():
        app.mount("/_next", StaticFiles(directory=str(next_static_path)), name="next_static")
    
    print("✅ 使用 Next.js 导出的静态文件")
elif frontend_public.exists():
    # 备用：使用 public 目录
    app.mount("/static", StaticFiles(directory=str(frontend_public)), name="static")
    print("✅ 使用前端 public 目录")

# 将后端API挂载到 /api 路径
app.mount("/api", backend_app)

@app.get("/")
async def root():
    """前端主页"""
    # Next.js 静态导出的主页
    index_path = Path("frontend/out/index.html")
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # 如果没有找到前端文件，返回简单的欢迎页面
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Impromptu - 社交匹配系统</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                background: white;
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 500px;
                margin: 20px;
            }
            h1 {
                color: #333;
                margin-bottom: 1rem;
                font-size: 2.5rem;
            }
            p {
                color: #666;
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 2rem;
            }
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border-radius: 30px;
                text-decoration: none;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
                margin: 10px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }
            .feature {
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 10px;
                font-size: 0.9rem;
            }
            .warning {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Impromptu</h1>
            <p>AI驱动的智能社交匹配系统<br>找到最合适的伙伴，开启美好连接</p>
            
            <div class="warning">
                ⚠️ 前端应用需要构建后才能访问<br>
                请运行：<code>cd frontend && npm run build</code>
            </div>
            
            <div class="features">
                <div class="feature">🧠 AI智能匹配</div>
                <div class="feature">💖 多维度分析</div>
                <div class="feature">🔒 隐私安全</div>
                <div class="feature">⚡ 实时响应</div>
            </div>
            
            <a href="/api/docs" class="btn">📖 API 文档</a>
            <a href="/api/health" class="btn">🔍 健康检查</a>
            
            <p style="margin-top: 2rem; color: #999; font-size: 0.9rem;">
                后端API已成功部署！<br>
                前端需要先构建才能显示界面
            </p>
        </div>
    </body>
    </html>
    """)

# SPA 路由支持 - 对于 Next.js 应用的其他路由
@app.get("/{path:path}")
async def spa_router(path: str):
    """SPA 路由支持，处理前端应用的所有路由"""
    # 忽略 API 路由
    if path.startswith("api/"):
        return {"error": "API route not found"}
    
    # 检查是否是静态资源请求
    if path.startswith("_next/") or path.endswith(('.js', '.css', '.png', '.jpg', '.ico', '.svg')):
        static_file = Path("frontend/out") / path
        if static_file.exists():
            return FileResponse(str(static_file))
    
    # 对于其他路径，返回 Next.js 应用的主页（SPA 模式）
    index_path = Path("frontend/out/index.html")
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # 如果没有前端文件，返回404
    return {"error": "Page not found", "message": "前端应用需要先构建"}

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "frontend": "integrated",
        "backend": "running",
        "message": "Impromptu 全栈应用运行正常"
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 