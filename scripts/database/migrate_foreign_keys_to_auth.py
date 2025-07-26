#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将数据库中的外键关系从user_id迁移到auth_user_id
更新user_metadata、user_tags等表的外键约束
"""

import os
import sys
import requests
import json
from typing import List, Dict
import dotenv

dotenv.load_dotenv()

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ 请设置环境变量: SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

def generate_migration_sql() -> str:
    """生成完整的迁移SQL脚本"""
    return """
-- 外键迁移脚本：从user_id迁移到auth_user_id
-- 执行前请确保所有数据已经有对应的auth_user_id

BEGIN;

-- 1. 删除旧的外键约束
ALTER TABLE public.user_metadata 
DROP CONSTRAINT IF EXISTS user_metadata_user_id_fkey;

ALTER TABLE public.user_tags 
DROP CONSTRAINT IF EXISTS user_tags_user_id_fkey;

-- 2. 添加新的外键约束到auth.users
ALTER TABLE public.user_metadata 
ADD CONSTRAINT user_metadata_auth_user_id_fkey 
FOREIGN KEY (auth_user_id) 
REFERENCES auth.users(id) 
ON DELETE CASCADE;

ALTER TABLE public.user_tags 
ADD CONSTRAINT user_tags_auth_user_id_fkey 
FOREIGN KEY (auth_user_id) 
REFERENCES auth.users(id) 
ON DELETE CASCADE;

-- 3. 创建索引提升性能
CREATE INDEX IF NOT EXISTS idx_user_metadata_auth_user_id 
ON public.user_metadata(auth_user_id);

CREATE INDEX IF NOT EXISTS idx_user_tags_auth_user_id 
ON public.user_tags(auth_user_id);

-- 4. 更新行级安全策略
DROP POLICY IF EXISTS "Users can only see their own metadata" ON public.user_metadata;
CREATE POLICY "Users can only see their own metadata" ON public.user_metadata
FOR ALL USING (auth_user_id = auth.uid());

DROP POLICY IF EXISTS "Users can only see their own tags" ON public.user_tags;
CREATE POLICY "Users can only see their own tags" ON public.user_tags
FOR ALL USING (auth_user_id = auth.uid());

-- 5. 创建兼容性视图
CREATE OR REPLACE VIEW public.user_metadata_with_profile AS
SELECT 
    um.*,
    up.user_id as legacy_user_id,
    up.display_name,
    up.email
FROM public.user_metadata um
JOIN public.user_profile up ON um.auth_user_id = up.auth_user_id;

CREATE OR REPLACE VIEW public.user_tags_with_profile AS
SELECT 
    ut.*,
    up.user_id as legacy_user_id,
    up.display_name,
    up.email
FROM public.user_tags ut
JOIN public.user_profile up ON ut.auth_user_id = up.auth_user_id;

-- 6. 优化数据库性能
ANALYZE public.user_metadata;
ANALYZE public.user_tags;
ANALYZE public.user_profile;

-- 7. 清理无用的索引（如果存在的话）
DROP INDEX IF EXISTS public.idx_user_metadata_user_id;
DROP INDEX IF EXISTS public.idx_user_tags_user_id;

COMMIT;
"""

def check_data_consistency() -> bool:
    """检查数据一致性，确保所有记录都有对应的auth_user_id"""
    print("🔍 检查数据一致性...")
    
    # 检查user_metadata表
    url = f"{SUPABASE_URL}/rest/v1/user_metadata"
    headers = {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'select': 'count',
        'auth_user_id': 'is.null'
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        null_metadata = len(response.json())
        if null_metadata > 0:
            print(f"⚠️  user_metadata表中有 {null_metadata} 条记录的auth_user_id为空")
            return False
    
    # 检查user_tags表
    url = f"{SUPABASE_URL}/rest/v1/user_tags"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        null_tags = len(response.json())
        if null_tags > 0:
            print(f"⚠️  user_tags表中有 {null_tags} 条记录的auth_user_id为空")
            return False
    
    print("✅ 数据一致性检查通过")
    return True

def write_migration_file(sql_content: str) -> str:
    """将SQL内容写入迁移文件"""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"migration_{timestamp}_foreign_keys_to_auth.sql"
    filepath = os.path.join("scripts", filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        print(f"✅ 迁移文件已生成: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ 生成迁移文件失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 外键迁移脚本生成器：从user_id到auth_user_id")
    print("=" * 60)
    
    # 1. 检查数据一致性
    if not check_data_consistency():
        print("\n❌ 数据一致性检查失败，请先运行用户迁移脚本")
        print("   python scripts/migrate_users_to_auth.py")
        return
    
    # 2. 生成迁移SQL
    print("\n📋 将生成以下操作的SQL脚本:")
    print("   • 删除旧的外键约束 (user_id)")
    print("   • 添加新的外键约束 (auth_user_id -> auth.users.id)")
    print("   • 更新行级安全策略")
    print("   • 创建兼容性视图")
    print("   • 创建索引优化性能")
    print("   • 清理无用索引")
    
    confirm = input("\n是否生成迁移SQL文件? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 用户取消操作")
        return
    
    # 3. 生成SQL文件
    migration_sql = generate_migration_sql()
    migration_file = write_migration_file(migration_sql)
    
    if migration_file:
        print("\n" + "=" * 60)
        print("🎉 迁移SQL文件生成成功!")
        print(f"\n📄 文件位置: {migration_file}")
        
        print("\n🚀 执行迁移的步骤:")
        print("1. 备份数据库（重要！）")
        print("2. 在Supabase Dashboard中执行SQL:")
        print("   • 进入 SQL Editor")
        print("   • 粘贴并执行生成的SQL脚本")
        print("3. 或者使用MCP工具执行:")
        print("   • 通过mcp_supabase_apply_migration执行")
        
        print("\n✅ 迁移完成后的变化:")
        print("   • user_metadata.auth_user_id -> auth.users.id (外键)")
        print("   • user_tags.auth_user_id -> auth.users.id (外键)")
        print("   • 更新了行级安全策略使用auth_user_id")
        print("   • 创建了兼容性视图包含legacy_user_id")
        print("   • 创建了性能优化索引")
        
        print("\n📝 重要提醒:")
        print("   • 旧的user_id字段仍然保留，但不再作为外键")
        print("   • 兼容性视图提供legacy_user_id字段")
        print("   • 建议应用代码逐步迁移到使用auth_user_id")
        print("   • RLS策略已更新，确保安全性")
        
        print("\n🔗 相关表结构:")
        print("   user_profile: user_id (主键) + auth_user_id (外键到auth.users)")
        print("   user_metadata: auth_user_id (外键到auth.users)")
        print("   user_tags: auth_user_id (外键到auth.users)")
    else:
        print("❌ 生成迁移文件失败")

if __name__ == "__main__":
    main() 