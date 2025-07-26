#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
部署检查脚本 - 验证前端和后端配置
"""

import sys
from pathlib import Path

def check_frontend():
    """检查前端配置"""
    print("🔍 检查前端配置...")
    
    # 检查关键目录
    frontend_dir = Path("frontend")
    app_dir = frontend_dir / "app"
    out_dir = frontend_dir / "out"
    legacy_dir = frontend_dir / "legacy"
    
    print(f"✅ frontend/ 目录存在: {frontend_dir.exists()}")
    print(f"✅ frontend/app/ 目录存在: {app_dir.exists()}")
    print(f"📦 frontend/out/ 目录存在: {out_dir.exists()}")
    print(f"❌ frontend/legacy/ 目录存在: {legacy_dir.exists()} (应该为 False)")
    
    # 检查主要文件
    main_page = app_dir / "page.tsx"
    next_config = frontend_dir / "next.config.js"
    package_json = frontend_dir / "package.json"
    
    print(f"✅ 主页面存在: {main_page.exists()}")
    print(f"✅ Next.js 配置存在: {next_config.exists()}")
    print(f"✅ package.json 存在: {package_json.exists()}")
    
    if out_dir.exists():
        index_html = out_dir / "index.html"
        print(f"✅ 构建后的 index.html 存在: {index_html.exists()}")
    else:
        print("⚠️ 前端还未构建，请运行: cd frontend && npm run build")
    
    return legacy_dir.exists() == False

def check_backend():
    """检查后端配置"""
    print("\n🔍 检查后端配置...")
    
    main_fullstack = Path("main_fullstack.py")
    main_py = Path("main.py")
    
    print(f"✅ main_fullstack.py 存在: {main_fullstack.exists()}")
    print(f"✅ main.py 存在: {main_py.exists()}")
    
    return main_fullstack.exists() and main_py.exists()

def main():
    """主检查函数"""
    print("🚀 Impromptu 部署配置检查")
    print("=" * 40)
    
    frontend_ok = check_frontend()
    backend_ok = check_backend()
    
    print("\n📋 检查结果:")
    print(f"前端配置: {'✅ 正确' if frontend_ok else '❌ 错误'}")
    print(f"后端配置: {'✅ 正确' if backend_ok else '❌ 错误'}")
    
    if frontend_ok and backend_ok:
        print("\n🎉 所有配置正确！")
        print("💡 如果前端还未构建，请运行：")
        print("   cd frontend && npm run build")
        print("💡 然后启动应用：")
        print("   python main.py")
    else:
        print("\n⚠️ 发现配置问题，请检查上述输出")
        sys.exit(1)

if __name__ == "__main__":
    main() 