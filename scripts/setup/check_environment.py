#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
环境检查脚本

检查项目运行环境是否满足要求
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("   需要Python 3.8或更高版本")
        return False
    else:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True

def check_required_packages():
    """检查必需的Python包"""
    print("\n📦 检查必需的Python包...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'gensim',
        'faiss',
        'numpy',
        'sklearn',
        'jieba',
        'yaml',
        'requests',
        'supabase'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_dirs = [
        'src',
        'src/algorithms',
        'src/models',
        'src/services',
        'data',
        'data/raw',
        'data/processed',
        'data/models',
        'data/results',
        'scripts',
        'scripts/demo',
        'scripts/setup',
        'scripts/train',
        'web',
        'configs',
        'tests'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - 不存在")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️  缺少目录: {', '.join(missing_dirs)}")
        return False
    
    return True

def check_data_files():
    """检查数据文件"""
    print("\n📊 检查数据文件...")
    
    # 检查用户档案
    profiles_dir = Path("data/raw/profiles")
    if profiles_dir.exists():
        profile_files = list(profiles_dir.glob("*.json"))
        print(f"✅ 用户档案: {len(profile_files)} 个文件")
    else:
        print("❌ 用户档案目录不存在")
        return False
    
    # 检查模型文件
    models_dir = Path("data/models")
    if models_dir.exists():
        model_files = list(models_dir.glob("*.pkl")) + list(models_dir.glob("*.npy"))
        print(f"✅ 模型文件: {len(model_files)} 个文件")
    else:
        print("⚠️  模型目录不存在")
    
    return True

def check_imports():
    """检查模块导入"""
    print("\n🔧 检查模块导入...")
    
    try:
        # 添加项目根目录到路径
        project_root = Path(__file__).parent.parent.parent
        sys.path.append(str(project_root))
        
        # 测试导入
        from backend.models import CompatibilityResult, UserRequest
        print("✅ src.models 导入成功")
        
        from configs.config import ConfigManager
        print("✅ configs.config 导入成功")
        
        from backend.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
        print("✅ 核心算法模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def main():
    """主检查流程"""
    print("🔍 Impromptu 环境检查")
    print("=" * 40)
    
    checks = [
        check_python_version,
        check_required_packages,
        check_project_structure,
        check_data_files,
        check_imports
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 环境检查通过！项目可以正常运行。")
        print("\n🚀 下一步:")
        print("1. 运行演示: python scripts/demo/main.py")
        print("2. 启动API: bash scripts/setup/start_api.sh")
        print("3. 启动Web: bash scripts/setup/start_web.sh")
    else:
        print("❌ 环境检查失败，请解决上述问题后重试。")
        print("\n💡 建议:")
        print("1. 运行: bash scripts/setup/install.sh")
        print("2. 检查Python环境和依赖包")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 