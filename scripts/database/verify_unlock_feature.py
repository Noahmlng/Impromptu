#!/usr/bin/env python3
"""
验证游戏解锁功能是否正常工作
"""

import os
import sys
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            # 尝试从.env.local获取
            env_file = project_root / ".env.local"
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith(f"{var}="):
                            os.environ[var] = line.split('=', 1)[1].strip()
                            break
            
            if not os.getenv(var):
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    print("✅ 环境配置正常")
    return True

def check_database_table():
    """检查数据库表是否存在"""
    print("🔍 检查user_unlocks表...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/user_unlocks?select=count&limit=0",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ user_unlocks表存在且可访问")
            return True
        else:
            print(f"❌ 表不存在或无法访问 (状态码: {response.status_code})")
            print("📋 请按照以下步骤创建表:")
            print("1. 打开 Supabase Dashboard")
            print("2. 进入 SQL Editor")
            print("3. 复制 scripts/database/manual_setup_guide.md 中的SQL")
            print("4. 执行SQL语句")
            return False
            
    except Exception as e:
        print(f"❌ 检查表时出错: {e}")
        return False

def check_backend_api():
    """检查后端API是否正常"""
    print("🔍 检查后端API...")
    
    api_endpoints = [
        "http://localhost:5000/health",
        "http://localhost:5000/api/unlock/games/config"
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✅ API正常: {endpoint}")
            else:
                print(f"⚠️ API异常: {endpoint} (状态码: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"❌ API无法连接: {endpoint}")
            print("💡 请启动后端服务: cd backend && python -m uvicorn services.main_api:app --reload")
        except Exception as e:
            print(f"❌ API检查失败: {endpoint} - {e}")

def check_frontend_files():
    """检查前端文件是否存在"""
    print("🔍 检查前端游戏组件...")
    
    required_files = [
        "frontend/components/memory-game.tsx",
        "frontend/components/quiz-game.tsx",
        "frontend/components/puzzle-game.tsx",
        "frontend/components/reaction-game.tsx",
        "frontend/components/unlock-modal.tsx"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    return all_exist

def main():
    """主验证流程"""
    print("🚀 验证游戏解锁功能")
    print("=" * 50)
    
    checks = [
        ("环境配置", check_environment),
        ("数据库表", check_database_table),
        ("前端组件", check_frontend_files),
        ("后端API", check_backend_api)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name}检查失败: {e}")
            results[name] = False
        print()
    
    # 总结
    print("📊 检查结果总结:")
    print("=" * 30)
    for name, result in results.items():
        status = "✅ 正常" if result else "❌ 异常"
        print(f"{name}: {status}")
    
    print("\n🎯 下一步操作:")
    if not results.get("数据库表", False):
        print("1. 🔧 创建数据库表 - 参考 scripts/database/manual_setup_guide.md")
    
    if not results.get("后端API", False):
        print("2. 🚀 启动后端服务:")
        print("   cd backend && python -m uvicorn services.main_api:app --reload")
    
    print("3. 🌐 启动前端服务:")
    print("   cd frontend && npm run dev")
    
    print("4. 🎮 测试游戏解锁功能:")
    print("   - 访问匹配搜索页面")
    print("   - 查找低匹配度用户（<50%）")
    print("   - 点击解锁按钮测试游戏")

if __name__ == "__main__":
    main() 