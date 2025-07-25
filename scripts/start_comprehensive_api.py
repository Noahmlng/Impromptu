#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合匹配系统API服务器启动脚本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def check_dependencies():
    """检查必要的依赖"""
    required_packages = [
        'flask',
        'flask-cors',
        'supabase',
        'pyjwt',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """检查环境配置"""
    env_file = project_root / '.env'
    env_local_file = project_root / '.env.local'
    
    # 检查环境变量文件
    if not env_file.exists() and not env_local_file.exists():
        print("⚠️  未找到环境配置文件 (.env 或 .env.local)")
        print("建议创建 .env 文件包含以下内容:")
        print("""
JWT_SECRET=your_jwt_secret_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
""")
        return False
    
    # 检查必要的环境变量
    required_env_vars = ['JWT_SECRET', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  缺少以下环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    return True

def start_server():
    """启动服务器"""
    try:
        print("🚀 启动综合匹配系统API服务器...")
        print("=" * 50)
        print("🔐 用户认证: /api/auth/*")
        print("📝 Metadata建档: /api/profile/*")
        print("🏷️  Tag建模: /api/tags/*")
        print("🔍 用户匹配: /api/match/*")
        print("📊 系统信息: /api/system/*")
        print("=" * 50)
        print("📖 API文档: docs/COMPREHENSIVE_API.md")
        print("🌐 服务器地址: http://localhost:5003")
        print("=" * 50)
        
        # 启动服务器
        api_server_path = project_root / 'src' / 'services' / 'comprehensive_api.py'
        
        if platform.system() == 'Windows':
            # Windows
            subprocess.run([sys.executable, str(api_server_path)], cwd=str(project_root))
        else:
            # Unix/Linux/macOS
            subprocess.run([sys.executable, str(api_server_path)], cwd=str(project_root))
    
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    print("🔧 检查环境...")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺少的包后重试")
        return 1
    
    # 检查环境变量
    if not check_environment():
        print("\n⚠️  环境配置检查失败，建议配置环境变量后重试")
        print("系统将使用默认配置启动...")
    
    print("✅ 环境检查完成")
    
    # 启动服务器
    start_server()
    
    return 0

if __name__ == '__main__':
    exit(main()) 