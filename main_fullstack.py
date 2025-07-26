#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu 全栈应用

构建并提供Next.js前端 + 后端API的完整应用
"""

import os
import sys
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入后端API
from backend.services.main_api import app as backend_app

# 创建全栈应用
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

def build_frontend():
    """构建Next.js前端"""
    frontend_dir = Path("frontend")
    out_dir = frontend_dir / "out"
    
    print("🔨 检查前端构建状态...")
    
    # 检查是否已经构建过
    if out_dir.exists() and len(list(out_dir.glob("*"))) > 0:
        print("✅ 发现已构建的前端文件，跳过构建")
        return True
    
    if not frontend_dir.exists():
        print("❌ frontend 目录不存在")
        return False
    
    print("⚠️ 前端未构建，将在后台构建...")
    print("💡 如需立即使用，请手动运行: cd frontend && npm run build")
    
    # 不在启动时构建，让用户手动构建或后台处理
    return False

# 检查前端状态（不阻塞启动）
frontend_status = build_frontend()

# 配置静态文件服务（如果前端已构建）
frontend_out = Path("frontend/out")
if frontend_out.exists() and len(list(frontend_out.glob("*"))) > 0:
    # 挂载 _next 静态资源
    next_static = frontend_out / "_next"
    if next_static.exists():
        app.mount("/_next", StaticFiles(directory=str(next_static)), name="next_static")
    
    # 挂载其他静态资源
    app.mount("/static", StaticFiles(directory=str(frontend_out)), name="static")
    print("✅ 前端静态文件已挂载")
else:
    print("⚠️ 前端未构建，将显示构建指引页面")

# 将后端API挂载到 /api 路径
app.mount("/api", backend_app)

@app.get("/")
async def root():
    """前端主页 - 提供Next.js构建的页面"""
    frontend_index = Path("frontend/out/index.html")
    
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    
    # 如果前端未构建，返回构建指引页面
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Impromptu - 构建中</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                text-align: center;
                background: white;
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 600px;
                margin: 20px;
            }}
            h1 {{
                color: #333;
                margin-bottom: 1rem;
                font-size: 2.5rem;
            }}
            p {{
                color: #666;
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 2rem;
            }}
            .code {{
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 8px;
                font-family: 'Monaco', 'Courier New', monospace;
                color: #333;
                margin: 1rem 0;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border-radius: 30px;
                text-decoration: none;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
                margin: 10px;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Impromptu</h1>
            <p>前端应用正在准备中...</p>
            
            <p>请运行以下命令构建前端：</p>
            <div class="code">
                cd frontend<br>
                npm install<br>
                npm run build
            </div>
            
            <p>或者重新启动应用，系统会自动构建：</p>
            <div class="code">
                python main_fullstack.py
            </div>
            
            <a href="/api/docs" class="btn">📖 API 文档</a>
            <a href="/api/health" class="btn">🔍 健康检查</a>
            
            <p style="margin-top: 2rem; color: #999; font-size: 0.9rem;">
                后端API已就绪，等待前端构建完成
            </p>
        </div>
        
        <script>
            // 每5秒检查一次页面是否可用
            setTimeout(() => {{
                window.location.reload();
            }}, 5000);
        </script>
    </body>
    </html>
    """)

@app.get("/{path:path}")
async def spa_router(path: str):
    """SPA路由支持 - 处理前端应用的所有路由"""
    # 忽略API路由
    if path.startswith("api/"):
        return {"error": "API route not found"}
    
    # 检查是否是静态资源
    if path.startswith("_next/") or path.endswith(('.js', '.css', '.png', '.jpg', '.ico', '.svg', '.json')):
        static_file = Path("frontend/out") / path
        if static_file.exists():
            return FileResponse(str(static_file))
    
    # 对于其他路径，返回前端主页（SPA模式）
    frontend_index = Path("frontend/out/index.html")
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    
    # 如果前端未构建，重定向到主页
    return HTMLResponse(content='<script>window.location.href="/";</script>')

@app.get("/health")
async def health():
    """健康检查"""
    frontend_status = "ready" if Path("frontend/out/index.html").exists() else "building"
    return {
        "status": "healthy",
        "frontend": frontend_status,
        "backend": "running",
        "message": "Impromptu 全栈应用运行正常"
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 Impromptu 全栈应用启动")
    print("=" * 50)
    print(f"📍 应用地址: http://0.0.0.0:{port}")
    print(f"📖 API文档: http://0.0.0.0:{port}/api/docs")
    print(f"🔍 健康检查: http://0.0.0.0:{port}/health")
    
    frontend_ready = Path("frontend/out/index.html").exists()
    if frontend_ready:
        print("✅ 前端已构建，可直接访问")
    else:
        print("⚠️ 前端未构建，将显示构建指引")
        print("💡 构建命令: cd frontend && npm run build")
    
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=port) 