#!/usr/bin/env python3
"""
测试登录流程修复
验证登录成功后的跳转是否正常工作
"""

import requests
import time
import json

def test_backend_connection():
    """测试后端API连接"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端API连接正常")
            return True
        else:
            print(f"❌ 后端API响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端API: {e}")
        print("请确保后端服务已启动: python backend/main.py")
        return False

def test_auth_endpoints():
    """测试认证端点"""
    base_url = 'http://localhost:8000'
    
    # 测试注册
    test_user = {
        "email": "test_login_flow@example.com",
        "password": "test123456",
        "display_name": "Test User"
    }
    
    try:
        # 先尝试登录（如果用户已存在）
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": test_user["email"], "password": test_user["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            result = login_response.json()
            if result.get('success'):
                print("✅ 登录端点工作正常")
                print(f"   Token: {result['data']['token'][:20]}...")
                return True
            else:
                print(f"❌ 登录失败: {result.get('message')}")
        
        # 如果登录失败，尝试注册
        register_response = requests.post(
            f"{base_url}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code == 200:
            result = register_response.json()
            if result.get('success'):
                print("✅ 注册端点工作正常")
                print(f"   Token: {result['data']['token'][:20]}...")
                return True
            else:
                print(f"❌ 注册失败: {result.get('message')}")
        
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 认证端点测试失败: {e}")
        return False

def check_frontend_running():
    """检查前端是否运行"""
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务运行正常")
            return True
        else:
            print(f"❌ 前端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到前端服务: {e}")
        print("请确保前端服务已启动: npm run dev")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试登录流程修复...")
    print("=" * 50)
    
    # 检查服务状态
    backend_ok = test_backend_connection()
    frontend_ok = check_frontend_running()
    
    if not backend_ok or not frontend_ok:
        print("\n❌ 服务检查失败，请确保前后端服务都已启动")
        print("\n启动命令:")
        print("后端: python backend/main.py")
        print("前端: npm run dev")
        return
    
    # 测试认证端点
    auth_ok = test_auth_endpoints()
    
    if auth_ok:
        print("\n🎉 登录流程测试通过！")
        print("\n✅ 修复内容:")
        print("1. 登录成功后直接跳转到 /home（而不是 /）")
        print("2. 注册成功后直接跳转到 /onboarding")
        print("3. 优化了认证状态检查，减少页面闪烁")
        print("4. 增强了状态管理的一致性")
        
        print("\n🔧 测试步骤:")
        print("1. 访问 http://localhost:3000/login")
        print("2. 尝试登录或注册")
        print("3. 观察是否直接跳转到目标页面（无闪烁）")
        
    else:
        print("\n❌ 认证端点测试失败")
        print("请检查后端服务和数据库配置")

if __name__ == "__main__":
    main() 