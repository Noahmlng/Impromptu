 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速认证测试脚本
用于验证修复后的认证系统
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from supabase import create_client, Client

# 配置
SUPABASE_URL = 'https://anxbbsrnjgmotxzysqwf.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0'

def main():
    """主函数"""
    print("⚡ 快速认证测试")
    print("=" * 30)
    
    # 创建唯一邮箱
    test_email = f"quicktest_{int(time.time())}@gmail.com"
    test_password = "QuickTest123!"
    
    print(f"📧 测试邮箱: {test_email}")
    
    try:
        # 1. 创建Supabase客户端
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase客户端创建成功")
        
        # 2. 测试注册
        print("\n🔗 测试用户注册...")
        auth_response = supabase.auth.sign_up({
            "email": test_email,
            "password": test_password,
            "options": {
                "data": {
                    "display_name": "快速测试用户"
                }
            }
        })
        
        if auth_response.user:
            print("✅ 注册成功!")
            print(f"   用户ID: {auth_response.user.id}")
            print(f"   邮箱确认: {'已确认' if auth_response.user.email_confirmed_at else '需确认'}")
            
            # 3. 测试登录
            print("\n🔐 测试用户登录...")
            login_response = supabase.auth.sign_in_with_password({
                "email": test_email,
                "password": test_password
            })
            
            if login_response.user and login_response.session:
                print("✅ 登录成功!")
                print(f"   Token: {login_response.session.access_token[:30]}...")
                
                # 4. 测试token解码
                print("\n🔍 测试Token解码...")
                import jwt
                decoded = jwt.decode(login_response.session.access_token, options={"verify_signature": False})
                print(f"   用户ID: {decoded.get('sub')}")
                print(f"   邮箱: {decoded.get('email')}")
                
                print("\n🎉 所有测试通过!")
                return 0
            else:
                print("❌ 登录失败")
                return 1
        else:
            print("❌ 注册失败")
            return 1
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 