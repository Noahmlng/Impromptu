#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu 后端主入口

统一的后端服务入口，整合所有API功能
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def start_comprehensive_api(port=8000):
    """启动完整的API服务（包含认证、匹配等完整功能）"""
    print(f"🚀 启动完整API服务 - 端口 {port}")
    import uvicorn
    uvicorn.run(
        "backend.services.main_api:app", 
        host='0.0.0.0', 
        port=port, 
        reload=True,
        log_level="info"
    )

def start_simple_api(port=5000):
    """启动简单的API服务（基础匹配和训练功能）"""
    print(f"🔧 启动简单API服务 - 端口 {port}")
    try:
        from backend.services.api_server import app
        app.run(host='0.0.0.0', port=port, debug=True)
    except ImportError:
        print("⚠️ api_server模块不存在，使用main_api替代")
        import uvicorn
        uvicorn.run(
            "backend.services.main_api:app", 
            host='0.0.0.0', 
            port=port, 
            reload=True,
            log_level="info"
        )

def main():
    parser = argparse.ArgumentParser(description='Impromptu 后端服务')
    parser.add_argument('mode', choices=['comprehensive', 'simple', 'both'], 
                       default='comprehensive',
                       help='API服务模式: comprehensive(完整功能), simple(基础功能), both(同时启动)')
    parser.add_argument('--port', type=int, default=8000, 
                       help='主要API服务端口 (comprehensive模式)')
    parser.add_argument('--simple-port', type=int, default=5000,
                       help='简单API服务端口 (simple模式或both模式)')
    
    args = parser.parse_args()
    
    print("🎯 Impromptu 后端服务启动器")
    print("=" * 40)
    
    if args.mode == 'comprehensive':
        start_comprehensive_api(args.port)
    elif args.mode == 'simple':
        start_simple_api(args.simple_port)
    elif args.mode == 'both':
        print("🔄 同时启动两个API服务...")
        # 这里可以实现并行启动两个服务
        print(f"📍 完整API: http://localhost:{args.port}")
        print(f"📍 简单API: http://localhost:{args.simple_port}")
        print("💡 推荐使用: python backend/main.py comprehensive")
        start_comprehensive_api(args.port)

if __name__ == "__main__":
    main() 