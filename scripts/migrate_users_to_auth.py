#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Supabase Admin API将user_profile表中的用户迁移到auth.users表
需要设置环境变量: SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY
"""

import os
import sys
import requests
import json
from typing import List, Dict
import time
import uuid
import dotenv

dotenv.load_dotenv()

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ 请设置环境变量: SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

def get_unmigrated_users() -> List[Dict]:
    """获取需要迁移的用户列表"""
    print("📋 获取需要迁移的用户...")
    
    url = f"{SUPABASE_URL}/rest/v1/user_profile"
    headers = {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'select': 'user_id,email,display_name,phone,created_at',
        'auth_user_id': 'is.null'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ 找到 {len(users)} 个需要迁移的用户")
        return users
    else:
        print(f"❌ 获取用户失败: {response.status_code} - {response.text}")
        return []

def create_auth_user(user_data: Dict) -> Dict:
    """使用Admin API创建认证用户，返回包含auth_user_id和email的字典"""
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 生成唯一的mock邮箱，避免冲突
    mock_email = f"migrated_{user_data['user_id']}_{uuid.uuid4().hex[:8]}@auth.linker.internal"
    
    # 创建用户数据
    create_data = {
        'email': mock_email,
        'email_confirm': True,  # 直接确认邮箱
        'phone_confirm': True,  # 直接确认手机
        'user_metadata': {
            'display_name': user_data['display_name'],
            'original_user_id': user_data['user_id'],
            'original_email': user_data['email'],  # 保存原始邮箱
            'migrated_from_profile': True
        }
    }
    
    if user_data.get('phone'):
        create_data['phone'] = user_data['phone']
    
    print(f"   创建用户: {mock_email} (原邮箱: {user_data['email']}, 显示名: {user_data['display_name']})")
    
    response = requests.post(url, headers=headers, json=create_data)
    
    if response.status_code == 200:
        auth_user = response.json()
        auth_user_id = auth_user['id']
        auth_email = auth_user['email']
        print(f"   ✅ 成功创建: {auth_user_id}")
        return {
            'auth_user_id': auth_user_id,
            'auth_email': auth_email
        }
    else:
        print(f"   ❌ 创建失败: {response.status_code} - {response.text}")
        return None

def update_user_profile_auth_id(user_id: str, auth_user_id: str, auth_email: str) -> bool:
    """更新user_profile表的auth_user_id字段（暂时不更新email避免冲突）"""
    url = f"{SUPABASE_URL}/rest/v1/user_profile"
    headers = {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    update_data = {
        'auth_user_id': auth_user_id
        # 暂时不更新email，避免约束冲突
        # 'email': auth_email  
    }
    
    params = {
        'user_id': f'eq.{user_id}'
    }
    
    print(f"      更新user_profile: {user_id} -> {auth_user_id}")
    response = requests.patch(url, headers=headers, json=update_data, params=params)
    
    if response.status_code == 204:
        print(f"      ✅ user_profile更新成功")
        return True
    else:
        print(f"      ❌ 更新user_profile失败: {response.status_code} - {response.text}")
        return False

def update_user_metadata_auth_id(user_id: str, auth_user_id: str) -> bool:
    """更新user_metadata表的auth_user_id字段"""
    url = f"{SUPABASE_URL}/rest/v1/user_metadata"
    headers = {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    update_data = {
        'auth_user_id': auth_user_id
    }
    
    params = {
        'user_id': f'eq.{user_id}'
    }
    
    print(f"      更新user_metadata: {user_id} -> {auth_user_id}")
    response = requests.patch(url, headers=headers, json=update_data, params=params)
    
    if response.status_code == 204:
        return True
    else:
        print(f"      ❌ 更新user_metadata失败: {response.status_code} - {response.text}")
        return False

def update_user_tags_auth_id(user_id: str, auth_user_id: str) -> bool:
    """更新user_tags表的auth_user_id字段"""
    url = f"{SUPABASE_URL}/rest/v1/user_tags"
    headers = {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    update_data = {
        'auth_user_id': auth_user_id
    }
    
    params = {
        'user_id': f'eq.{user_id}'
    }
    
    print(f"      更新user_tags: {user_id} -> {auth_user_id}")
    response = requests.patch(url, headers=headers, json=update_data, params=params)
    
    if response.status_code == 204:
        return True
    else:
        print(f"      ❌ 更新user_tags失败: {response.status_code} - {response.text}")
        return False

def migrate_user(user_data: Dict) -> bool:
    """迁移单个用户"""
    print(f"\n🔄 迁移用户: {user_data['user_id']}")
    
    # 1. 创建auth用户
    auth_result = create_auth_user(user_data)
    if not auth_result:
        return False
    
    auth_user_id = auth_result['auth_user_id']
    auth_email = auth_result['auth_email']
    
    # 2. 更新user_profile表（同时更新email）
    if not update_user_profile_auth_id(user_data['user_id'], auth_user_id, auth_email):
        print(f"   ⚠️  更新user_profile失败")
        return False
    
    # 3. 更新user_metadata表
    if not update_user_metadata_auth_id(user_data['user_id'], auth_user_id):
        print(f"   ⚠️  更新user_metadata失败")
    
    # 4. 更新user_tags表
    if not update_user_tags_auth_id(user_data['user_id'], auth_user_id):
        print(f"   ⚠️  更新user_tags失败")
    
    print(f"   ✅ 用户迁移完成，auth用户ID: {auth_user_id}")
    print(f"      原始邮箱: {user_data['email']} -> Auth邮箱: {auth_email}")
    return True

def main():
    """主函数"""
    print("🚀 开始用户迁移到auth.users表")
    print("=" * 50)
    
    # 获取需要迁移的用户
    users_to_migrate = get_unmigrated_users()
    
    if not users_to_migrate:
        print("✅ 没有需要迁移的用户")
        return
    
    # 确认迁移
    print(f"\n⚡ 即将迁移 {len(users_to_migrate)} 个用户")
    confirm = input("是否继续? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 用户取消迁移")
        return
    
    # 逐个迁移用户
    success_count = 0
    failed_count = 0
    
    for i, user in enumerate(users_to_migrate, 1):
        print(f"\n[{i}/{len(users_to_migrate)}]", end="")
        
        if migrate_user(user):
            success_count += 1
        else:
            failed_count += 1
        
        # 避免API请求过于频繁
        time.sleep(0.5)
    
    # 输出结果
    print("\n" + "=" * 50)
    print(f"🎉 迁移完成!")
    print(f"   成功: {success_count} 个用户")
    print(f"   失败: {failed_count} 个用户")
    
    if failed_count > 0:
        print(f"\n⚠️  有 {failed_count} 个用户迁移失败，请检查日志")

if __name__ == "__main__":
    main() 