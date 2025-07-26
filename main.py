#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu - 部署入口点

提供完整的前后端服务
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """启动完整的前后端服务"""
    print("🚀 Impromptu 全栈应用启动")
    print("=" * 50)
    
    # 获取环境变量中的端口，默认为8000
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"📍 应用地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/api/docs")
    print(f"🔍 健康检查: http://{host}:{port}/health")
    print("💡 前端页面将自动构建并提供服务")
    
    try:
        import uvicorn
        # 使用全栈应用
        uvicorn.run(
            "main_fullstack:app", 
            host=host, 
            port=port, 
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 请确保已安装所有依赖：pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main() 