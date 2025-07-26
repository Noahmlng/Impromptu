#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为 user_profile 表添加 password 字段的数据库迁移脚本
用于支持直接的用户认证，而不依赖 Supabase Auth
"""

import os
import sys
import dotenv
from supabase import create_client

# 获取项目根目录并加载环境变量
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
dotenv.load_dotenv(os.path.join(project_root, '.env.local'))
dotenv.load_dotenv(os.path.join(project_root, '.env'))

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') 

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ 请设置环境变量: SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

def generate_migration_sql() -> str:
    """生成添加password字段的迁移SQL脚本"""
    return """
-- ========================================
-- 为 user_profile 表添加 password 字段
-- 支持直接的用户认证
-- ========================================

-- 开始事务
BEGIN;

-- 1. 为 user_profile 表添加 password 字段
ALTER TABLE public.user_profile 
ADD COLUMN IF NOT EXISTS password VARCHAR(255);

-- 2. 为 email 字段添加唯一约束（如果还没有的话）
ALTER TABLE public.user_profile 
ADD CONSTRAINT IF NOT EXISTS user_profile_email_unique 
UNIQUE (email);

-- 3. 创建 email 索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_user_profile_email 
ON public.user_profile(email);

-- 4. 为现有用户设置默认密码（可选，建议后续让用户重新设置）
-- UPDATE public.user_profile 
-- SET password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewfBGSO39c6P5LE6' -- 默认密码: 'password123'
-- WHERE password IS NULL;

-- 5. 如果需要，可以设置 password 为 NOT NULL（建议等数据迁移完成后再执行）
-- ALTER TABLE public.user_profile 
-- ALTER COLUMN password SET NOT NULL;

-- 6. 输出迁移完成信息
DO $$
DECLARE 
    profile_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO profile_count FROM public.user_profile;
    
    RAISE NOTICE '=== 迁移完成 ===';
    RAISE NOTICE '- user_profile 表已添加 password 字段';
    RAISE NOTICE '- email 字段已添加唯一约束';
    RAISE NOTICE '- 创建了 email 索引以提升查询性能';
    RAISE NOTICE '- user_profile 记录总数: %', profile_count;
    RAISE NOTICE '- 建议为现有用户设置初始密码';
END $$;

-- 提交事务
COMMIT;

-- 输出成功消息
SELECT 'Password field migration completed successfully!' as message;
"""

def run_migration():
    """执行迁移脚本"""
    try:
        # 创建 Supabase 客户端
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # 获取迁移 SQL
        migration_sql = generate_migration_sql()
        
        print("🚀 开始执行 user_profile 表密码字段迁移...")
        print("=" * 60)
        
        # 执行迁移
        response = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        if response.data:
            print("✅ 迁移执行成功!")
            print(f"📊 响应数据: {response.data}")
        else:
            print("❌ 迁移失败:")
            print(f"错误信息: {response}")
            
    except Exception as e:
        print(f"❌ 迁移执行失败: {e}")
        sys.exit(1)

def print_migration_sql():
    """打印迁移SQL以供手动执行"""
    print("=" * 60)
    print("📋 完整的迁移SQL脚本:")
    print("=" * 60)
    print(generate_migration_sql())
    print("=" * 60)

if __name__ == "__main__":
    print("🔧 User Profile Password Field Migration")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--sql-only":
        print_migration_sql()
    else:
        print("⚠️  这将为 user_profile 表添加 password 字段")
        print("⚠️  请确保已备份数据库")
        
        response = input("是否继续执行迁移? (y/N): ").strip().lower()
        if response == 'y':
            run_migration()
        else:
            print("❌ 迁移已取消")
            print_migration_sql()
            print("\n�� 您可以手动执行上述SQL脚本") 