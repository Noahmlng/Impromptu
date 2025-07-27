#!/usr/bin/env python3
"""
直接通过REST API执行SQL的脚本
"""

import os
import requests
import json

def execute_sql_via_rest_api():
    """通过REST API执行SQL"""
    
    # 获取环境变量
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("❌ 缺少SUPABASE_URL或SUPABASE_SERVICE_KEY环境变量")
        return False
    
    # SQL语句分割成单独的命令
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS user_unlocks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            unlocker_user_id UUID NOT NULL,
            target_user_id UUID NOT NULL,
            unlock_type VARCHAR(50) NOT NULL CHECK (unlock_type IN ('game_success', 'game_fail', 'credits_direct')),
            game_type VARCHAR(20) CHECK (game_type IN ('memory', 'quiz', 'puzzle', 'reaction')),
            game_score INTEGER,
            credits_spent INTEGER DEFAULT 0,
            unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker ON user_unlocks(unlocker_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_unlocks_target ON user_unlocks(target_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker_target ON user_unlocks(unlocker_user_id, target_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_unlocks_expires ON user_unlocks(expires_at) WHERE expires_at IS NOT NULL"
    ]
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    success_count = 0
    total_commands = len(sql_commands)
    
    print("🔄 开始执行SQL命令...")
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"   执行命令 {i}/{total_commands}...")
        
        try:
            # 使用rpc接口执行SQL
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/query",
                headers=headers,
                json={"query": sql.strip()},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ 命令 {i} 执行成功")
                success_count += 1
            else:
                print(f"   ⚠️ 命令 {i} 可能已存在或完成: {response.status_code}")
                # 对于CREATE TABLE和CREATE INDEX，409或类似状态码是正常的
                if response.status_code in [409, 201]:
                    success_count += 1
                
        except Exception as e:
            print(f"   ❌ 命令 {i} 执行失败: {e}")
    
    print(f"\n📊 执行结果: {success_count}/{total_commands} 命令成功")
    return success_count > 0

def verify_table_creation():
    """验证表是否创建成功"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        return False
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 尝试查询表结构
        response = requests.get(
            f"{supabase_url}/rest/v1/user_unlocks?select=count&limit=0",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ user_unlocks表验证成功!")
            
            # 获取表的count
            count_response = requests.get(
                f"{supabase_url}/rest/v1/user_unlocks?select=*&head=true",
                headers={**headers, 'Prefer': 'count=exact'},
                timeout=10
            )
            
            if 'Content-Range' in count_response.headers:
                count = count_response.headers['Content-Range'].split('/')[-1]
                print(f"📊 当前表中记录数: {count}")
            
            return True
        else:
            print(f"❌ 表验证失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

if __name__ == "__main__":
    print("🚀 直接执行SQL创建user_unlocks表")
    print("=" * 50)
    
    # 设置环境变量（如果需要）
    if not os.getenv("SUPABASE_URL"):
        os.environ["SUPABASE_URL"] = "https://anxbbsrnjgmotxzysqwf.supabase.co"
    if not os.getenv("SUPABASE_SERVICE_KEY"):
        os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDQwNjQ5MiwiZXhwIjoyMDY1OTgyNDkyfQ.MZnYmDJlObiaJiwxmRTWBQGZnIl0mrDTY92X9qpOCfc"
    
    # 先检查表是否存在
    print("🔍 检查表是否已存在...")
    if verify_table_creation():
        print("✅ 表已存在，无需重复创建!")
    else:
        # 执行SQL创建表
        if execute_sql_via_rest_api():
            print("\n⏳ 验证表创建结果...")
            if verify_table_creation():
                print("\n🎉 user_unlocks表创建成功!")
                print("📝 现在可以使用游戏解锁功能了!")
            else:
                print("\n⚠️ 表创建可能失败，请手动检查")
        else:
            print("\n❌ SQL执行失败") 