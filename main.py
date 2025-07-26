#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu - 部署入口点

这是为 Zeabur 部署创建的主入口文件，同时提供前端和后端服务
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """启动完整的Web应用（前端+后端）"""
    print("🚀 Impromptu 社交匹配系统 - 全栈部署启动")
    print("=" * 50)
    
    # 获取环境变量中的端口，默认为8000
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"📍 服务启动地址: http://{host}:{port}")
    print(f"📖 API文档地址: http://{host}:{port}/docs")
    print(f"🌐 前端界面: http://{host}:{port}/")
    
    try:
        import uvicorn
        # 使用修改后的 main_api，它包含静态文件服务
        uvicorn.run(
            "main_fullstack:app", 
            host=host, 
            port=port, 
            reload=False,  # 生产环境不使用热重载
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 尝试使用备用模式启动...")
        
        # 备用启动方式
        try:
            uvicorn.run(
                "backend.services.main_api:app", 
                host=host, 
                port=port, 
                reload=False,
                log_level="info"
            )
        except Exception as e2:
            print(f"❌ 备用启动也失败: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main() 