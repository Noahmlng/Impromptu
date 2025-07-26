#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu - 简化启动脚本（备用）

如果 main.py 失败，可以使用这个脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def start_server():
    """启动服务器的最简单方法"""
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 启动 Impromptu API 服务 - {host}:{port}")
    
    try:
        # 最简单的启动方式
        import uvicorn
        from backend.services.main_api import app
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        # 尝试直接导入并运行
        try:
            os.system(f"cd backend/services && python main_api.py --port {port}")
        except Exception as e2:
            print(f"❌ 备用启动也失败: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    start_server() 