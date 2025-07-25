 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Supabase认证系统重构
验证注册、登录、获取用户信息等功能
"""

import requests
import json
import sys
import time

# API配置
API_BASE_URL = 'http://localhost:5003'
import time
TEST_EMAIL = f'test_user_{int(time.time())}@gmail.com'  # 使用真实域名避免Supabase拒绝
TEST_PASSWORD = 'test_password_123'
TEST_DISPLAY_NAME = '测试用户'

def test_register():
    """测试用户注册"""
    print("🧪 测试用户注册...")
    
    url = f"{API_BASE_URL}/api/auth/register"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "display_name": TEST_DISPLAY_NAME
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if response.status_code == 201 and result.get('success'):
            print("✅ 注册成功")
            print(f"   用户ID: {result['data']['user_id']}")
            print(f"   邮箱: {result['data']['email']}")
            print(f"   显示名: {result['data']['display_name']}")
            return result['data']
        else:
            print(f"❌ 注册失败: {result.get('error', result.get('message', '未知错误'))}")
            print(f"   HTTP状态码: {response.status_code}")
            print(f"   完整响应: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 注册请求异常: {e}")
        return None

def test_login():
    """测试用户登录"""
    print("\n🧪 测试用户登录...")
    
    url = f"{API_BASE_URL}/api/auth/login"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print("✅ 登录成功")
            print(f"   用户ID: {result['data']['user_id']}")
            print(f"   Token: {result['data']['token'][:20]}...")
            return result['data']['token']
        else:
            print(f"❌ 登录失败: {result.get('error', result.get('message', '未知错误'))}")
            print(f"   HTTP状态码: {response.status_code}")
            print(f"   完整响应: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return None

def test_get_current_user(token):
    """测试获取当前用户信息"""
    print("\n🧪 测试获取用户信息...")
    
    url = f"{API_BASE_URL}/api/auth/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print("✅ 获取用户信息成功")
            print(f"   用户ID: {result['data']['user_id']}")
            print(f"   邮箱: {result['data']['email']}")
            print(f"   显示名: {result['data']['display_name']}")
            return True
        else:
            print(f"❌ 获取用户信息失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 获取用户信息请求异常: {e}")
        return False

def test_logout(token):
    """测试用户登出"""
    print("\n🧪 测试用户登出...")
    
    url = f"{API_BASE_URL}/api/auth/logout"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print("✅ 登出成功")
            return True
        else:
            print(f"❌ 登出失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 登出请求异常: {e}")
        return False

def test_health_check():
    """测试API健康检查"""
    print("🧪 测试API健康状态...")
    
    url = f"{API_BASE_URL}/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ API健康检查通过")
            return True
        else:
            print(f"❌ API健康检查失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API健康检查异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试Supabase认证系统重构")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health_check():
        print("\n❌ API服务不可用，请确保后端服务正在运行")
        print("💡 启动后端服务:")
        print("   python backend/services/comprehensive_api.py")
        print("   或")
        print("   python scripts/start_comprehensive_api.py")
        print("\n⚡ 您也可以运行服务检查脚本:")
        print("   python scripts/check_service.py")
        sys.exit(1)
    
    # 2. 测试注册（可能失败，如果用户已存在）
    register_result = test_register()
    
    # 3. 测试登录
    token = test_login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        sys.exit(1)
    
    # 4. 测试获取用户信息
    if not test_get_current_user(token):
        print("\n❌ 获取用户信息失败")
        sys.exit(1)
    
    # 5. 测试登出
    if not test_logout(token):
        print("\n❌ 登出失败")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 所有认证测试通过！Supabase认证系统重构成功")

if __name__ == "__main__":
    main() 