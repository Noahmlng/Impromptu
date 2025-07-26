 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Supabase连接和基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from supabase import create_client, Client

# 配置
SUPABASE_URL = 'https://anxbbsrnjgmotxzysqwf.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0'

def test_supabase_connection():
    """测试基本连接"""
    print("🔍 测试Supabase连接...")
    
    try:
        # 创建客户端
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase客户端创建成功")
        
        # 测试简单查询
        response = supabase.table('user_profile').select('count').execute()
        print("✅ 数据库连接测试成功")
        
        return supabase
        
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_auth_signup(supabase):
    """测试用户注册"""
    print("\n🔍 测试用户注册...")
    
    import time
    # 使用真实的邮箱域名，Supabase不接受example.com
    test_email = f"test_{int(time.time())}@gmail.com"
    test_password = "testpassword123"
    
    try:
        response = supabase.auth.sign_up({
            "email": test_email,
            "password": test_password,
            "options": {
                "data": {
                    "display_name": "测试用户"
                }
            }
        })
        
        print(f"注册响应: user={response.user is not None}, session={response.session is not None}")
        
        if response.user:
            print("✅ 用户注册成功")
            print(f"   用户ID: {response.user.id}")
            print(f"   邮箱: {response.user.email}")
            return response.user, test_password
        else:
            print("❌ 用户注册失败")
            return None, None
            
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def test_auth_signin(supabase, user, password):
    """测试用户登录"""
    print("\n🔍 测试用户登录...")
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": password
        })
        
        print(f"登录响应: user={response.user is not None}, session={response.session is not None}")
        
        if response.user and response.session:
            print("✅ 用户登录成功")
            print(f"   用户ID: {response.user.id}")
            print(f"   Token: {response.session.access_token[:20]}...")
            return response.session.access_token
        else:
            print("❌ 用户登录失败")
            return None
            
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("🚀 开始测试Supabase连接和认证")
    print("=" * 50)
    
    # 1. 测试连接
    supabase = test_supabase_connection()
    if not supabase:
        print("\n❌ Supabase连接失败，无法继续测试")
        return 1
    
    # 2. 测试注册
    user, password = test_auth_signup(supabase)
    if not user:
        print("\n❌ 用户注册失败，无法继续测试")
        return 1
    
    # 3. 测试登录
    token = test_auth_signin(supabase, user, password)
    if not token:
        print("\n❌ 用户登录失败")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 所有Supabase测试通过！")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 