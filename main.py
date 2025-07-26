#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu - 部署入口点

这是为 Zeabur 部署创建的主入口文件，同时提供前端和后端服务
"""

import os
import sys
import socket
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def check_port(port):
    """检查端口是否可用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
        return True
    except OSError:
        return False

def main():
    """启动完整的Web应用（前端+后端）"""
    print("🚀 Impromptu 社交匹配系统 - 全栈部署启动")
    print("=" * 50)
    
    # 强制使用8000端口
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"📍 服务启动地址: http://{host}:{port}")
    print(f"📖 API文档地址: http://{host}:{port}/api/docs")
    print(f"🌐 前端界面: http://{host}:{port}/")
    
    try:
        import uvicorn
        print("🚀 正在启动服务...")
        
        # 使用修改后的 main_fullstack
        uvicorn.run(
            "main_fullstack:app", 
            host=host, 
            port=port, 
            reload=False,  # 生产环境不使用热重载
            log_level="info",
            access_log=False  # 减少日志输出
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 尝试使用备用模式启动...")
        
        # 备用启动方式
        try:
            uvicorn.run(
                "backend.services.main_api:app", 
                host=host, 
                port=port, 
                reload=False,
                log_level="info",
                access_log=False
            )
        except Exception as e2:
            print(f"❌ 备用启动也失败: {e2}")
            print("\n🔍 可能的解决方案:")
            print("1. 检查是否有其他进程占用端口")
            print("2. 检查防火墙设置")
            print("3. 尝试使用不同的端口: PORT=8001 python main.py")
            sys.exit(1)

if __name__ == "__main__":
    main() 