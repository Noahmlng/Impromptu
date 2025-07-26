#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu - 部署入口点

这是为 Zeabur 部署创建的主入口文件
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """启动主要的API服务"""
    print("🚀 Impromptu 社交匹配系统 - 生产环境启动")
    print("=" * 50)
    
    # 获取环境变量中的端口，默认为8000
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"📍 服务启动地址: http://{host}:{port}")
    print(f"📖 API文档地址: http://{host}:{port}/docs")
    
    try:
        import uvicorn
        uvicorn.run(
            "backend.services.main_api:app", 
            host=host, 
            port=port, 
            reload=False,  # 生产环境不使用热重载
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 尝试使用简单模式启动...")
        
        # 备用启动方式
        try:
            from backend.services.api_server import app
            app.run(host=host, port=port, debug=False)
        except ImportError:
            print("❌ 所有启动方式都失败了")
            sys.exit(1)

if __name__ == "__main__":
    main() 