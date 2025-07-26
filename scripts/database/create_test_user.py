#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建测试用户脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.database_service import get_supabase

def create_test_user():
    """创建测试用户"""
    try:
        supabase = get_supabase()
        
        # 创建测试用户
        test_email = "test@impromptu.com"
        test_password = "123456789"
        
        print(f"🔧 创建测试用户: {test_email}")
        
        # 注册用户
        response = supabase.auth.sign_up({
            "email": test_email,
            "password": test_password,
            "options": {
                "data": {
                    "display_name": "测试用户"
                }
            }
        })
        
        if response.user:
            print(f"✅ 成功创建测试用户: {response.user.id}")
            print(f"📧 邮箱: {test_email}")
            print(f"🔑 密码: {test_password}")
            
            # 将用户信息写入user_profile表
            user_data = {
                'user_id': f'test_user_{response.user.id[:8]}',
                'display_name': '测试用户',
                'email': test_email,
                'auth_user_id': response.user.id,
                'status': 'active'
            }
            
            profile_response = supabase.table('user_profile').insert(user_data).execute()
            print(f"✅ 用户档案创建成功")
            
            return response.user.id
        else:
            print(f"❌ 用户创建失败")
            return None
            
    except Exception as e:
        print(f"❌ 创建测试用户失败: {e}")
        return None

if __name__ == "__main__":
    create_test_user() 