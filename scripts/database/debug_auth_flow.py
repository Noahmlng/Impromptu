 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试认证流程脚本
帮助诊断前端认证问题
"""

import requests
import json
import jwt
import sys

# API配置
API_BASE_URL = 'http://localhost:5003'
SUPABASE_URL = 'https://anxbbsrnjgmotxzysqwf.supabase.co'

def test_supabase_auth():
    """测试Supabase认证"""
    print("🔍 测试Supabase认证...")
    
    import time
    # 使用真实邮箱域名，避免Supabase拒绝example.com
    test_email = f"test_{int(time.time())}@gmail.com"
    
    test_credentials = {
        "email": test_email,
        "password": "testpassword123"
    }
    
    # 正确的Supabase API key和headers
    SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0'
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 尝试通过Supabase直接登录
    supabase_auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    
    try:
        response = requests.post(supabase_auth_url, json=test_credentials, headers=headers)
        print(f"Supabase认证响应状态: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            access_token = auth_data.get('access_token')
            print(f"✅ Supabase认证成功")
            print(f"Token: {access_token[:20]}...")
            
            # 解码token查看内容
            try:
                decoded = jwt.decode(access_token, options={"verify_signature": False})
                print(f"Token内容: {json.dumps(decoded, indent=2)}")
            except Exception as e:
                print(f"Token解码失败: {e}")
                
            return access_token
        else:
            print(f"❌ Supabase认证失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Supabase认证异常: {e}")
        return None

def test_backend_auth(token):
    """测试后端认证"""
    print(f"\n🔍 测试后端认证...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试获取用户信息
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/user", headers=headers)
        print(f"后端认证响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 后端认证成功")
            user_data = response.json()
            print(f"用户信息: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 后端认证失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 后端认证异常: {e}")
        return False

def test_metadata_api(token):
    """测试metadata API"""
    print(f"\n🔍 测试metadata API...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/profile/metadata", headers=headers)
        print(f"Metadata API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Metadata API访问成功")
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Metadata API访问失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Metadata API异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始调试认证流程")
    print("=" * 50)
    
    # 1. 测试Supabase认证
    token = test_supabase_auth()
    if not token:
        print("\n❌ Supabase认证失败，无法继续测试")
        print("💡 请确保:")
        print("   1. Supabase项目配置正确")
        print("   2. 测试用户存在")
        print("   3. 网络连接正常")
        return 1
    
    # 2. 测试后端认证
    if not test_backend_auth(token):
        print("\n❌ 后端认证失败")
        print("💡 请检查:")
        print("   1. 后端服务是否运行")
        print("   2. auth_required装饰器实现")
        print("   3. 用户profile是否存在")
        return 1
    
    # 3. 测试metadata API
    if not test_metadata_api(token):
        print("\n❌ Metadata API访问失败")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 所有认证流程测试通过！")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 