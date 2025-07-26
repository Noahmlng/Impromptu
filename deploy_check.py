#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
部署前检查脚本

验证项目配置和依赖是否正确
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major != 3 or version.minor < 8:
        print("❌ 警告: 建议使用 Python 3.8 或更高版本")
        return False
    print("✅ Python 版本符合要求")
    return True

def check_requirements():
    """检查依赖文件"""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt 文件不存在")
        return False
    
    print("✅ requirements.txt 文件存在")
    
    # 检查关键依赖
    with open(req_file, 'r') as f:
        content = f.read()
        
    key_deps = ['fastapi', 'uvicorn', 'pydantic', 'supabase']
    missing_deps = []
    
    for dep in key_deps:
        if dep not in content.lower():
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ 缺少关键依赖: {', '.join(missing_deps)}")
        return False
    
    print("✅ 关键依赖都存在")
    return True

def check_project_structure():
    """检查项目结构"""
    required_files = [
        "main.py",
        "backend/services/main_api.py",
        "backend/services/__init__.py",
        "configs/config.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 项目结构正确")
    return True

def check_import_paths():
    """检查导入路径"""
    try:
        # 添加项目根目录到路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # 测试关键模块导入
        import backend.services.main_api
        import backend.services.auth_service
        import backend.services.user_service
        
        print("✅ 模块导入测试成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_api_creation():
    """测试API创建"""
    try:
        # 添加项目根目录到路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from backend.services.main_api import app
        
        # 检查基本路由
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health"]
        
        for route in expected_routes:
            if route not in routes:
                print(f"❌ 缺少路由: {route}")
                return False
        
        print("✅ API 创建测试成功")
        return True
    except Exception as e:
        print(f"❌ API 创建失败: {e}")
        return False

def check_docker_files():
    """检查 Docker 相关文件"""
    docker_files = ["Dockerfile", ".dockerignore"]
    
    for file_name in docker_files:
        if not Path(file_name).exists():
            print(f"❌ 缺少 {file_name} 文件")
            return False
    
    print("✅ Docker 文件都存在")
    return True

def check_zeabur_config():
    """检查 Zeabur 配置"""
    config_file = Path(".zeabur/config.json")
    if not config_file.exists():
        print("❌ .zeabur/config.json 配置文件不存在")
        return False
    
    print("✅ Zeabur 配置文件存在")
    return True

def main():
    """主检查函数"""
    print("🔍 开始部署前检查...")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_requirements,
        check_project_structure,
        check_import_paths,
        test_api_creation,
        check_docker_files,
        check_zeabur_config
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 检查结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有检查都通过！可以安全部署")
        return True
    else:
        print("⚠️ 有些检查未通过，建议修复后再部署")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 