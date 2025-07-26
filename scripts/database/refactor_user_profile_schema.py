#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户表结构重构脚本
将user_metadata和user_tags的关联从user_profile.user_id改为user_profile.id
最终移除user_profile.user_id列，使user_profile成为真正的主表

重构步骤：
1. 在user_metadata和user_tags表中添加新的profile_id列(UUID)
2. 更新数据：将user_id映射到对应的user_profile.id
3. 创建新的外键约束
4. 删除旧的外键约束和user_id列
5. 重命名profile_id为user_id以保持API兼容性
6. 最后删除user_profile.user_id列
"""

import os
import sys
import dotenv
from typing import List, Dict

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
-- ========================================
-- 用户表结构重构迁移脚本
-- 将关联关系从user_profile.user_id改为user_profile.id
-- ========================================

-- 开始事务
BEGIN;

-- 第1步：检查数据完整性
DO $$
DECLARE 
    orphaned_metadata_count INTEGER;
    orphaned_tags_count INTEGER;
    profiles_without_id_count INTEGER;
BEGIN
    -- 检查孤立的metadata记录
    SELECT COUNT(*) INTO orphaned_metadata_count
    FROM public.user_metadata um
    LEFT JOIN public.user_profile up ON um.user_id = up.user_id
    WHERE up.id IS NULL;
    
    -- 检查孤立的tags记录
    SELECT COUNT(*) INTO orphaned_tags_count
    FROM public.user_tags ut
    LEFT JOIN public.user_profile up ON ut.user_id = up.user_id
    WHERE up.id IS NULL;
    
    -- 检查没有id的user_profile记录
    SELECT COUNT(*) INTO profiles_without_id_count
    FROM public.user_profile
    WHERE id IS NULL;
    
    -- 输出检查结果
    RAISE NOTICE '数据完整性检查:';
    RAISE NOTICE '- 孤立的metadata记录: %', orphaned_metadata_count;
    RAISE NOTICE '- 孤立的tags记录: %', orphaned_tags_count;
    RAISE NOTICE '- 没有id的profile记录: %', profiles_without_id_count;
    
    -- 如果有孤立数据，抛出错误
    IF orphaned_metadata_count > 0 OR orphaned_tags_count > 0 OR profiles_without_id_count > 0 THEN
        RAISE EXCEPTION '发现数据完整性问题，迁移终止。请先清理孤立数据。';
    END IF;
END $$;

-- 第2步：在user_metadata表中添加新的profile_id列
ALTER TABLE public.user_metadata 
ADD COLUMN IF NOT EXISTS profile_id UUID;

-- 第3步：在user_tags表中添加新的profile_id列  
ALTER TABLE public.user_tags 
ADD COLUMN IF NOT EXISTS profile_id UUID;

-- 第4步：更新user_metadata表的profile_id
UPDATE public.user_metadata 
SET profile_id = (
    SELECT up.id 
    FROM public.user_profile up 
    WHERE up.user_id = user_metadata.user_id
)
WHERE profile_id IS NULL;

-- 第5步：更新user_tags表的profile_id
UPDATE public.user_tags 
SET profile_id = (
    SELECT up.id 
    FROM public.user_profile up 
    WHERE up.user_id = user_tags.user_id
)
WHERE profile_id IS NULL;

-- 第6步：验证数据迁移完整性
DO $$
DECLARE 
    null_profile_id_metadata_count INTEGER;
    null_profile_id_tags_count INTEGER;
BEGIN
    -- 检查是否还有NULL的profile_id
    SELECT COUNT(*) INTO null_profile_id_metadata_count
    FROM public.user_metadata
    WHERE profile_id IS NULL;
    
    SELECT COUNT(*) INTO null_profile_id_tags_count
    FROM public.user_tags
    WHERE profile_id IS NULL;
    
    RAISE NOTICE '数据迁移验证:';
    RAISE NOTICE '- user_metadata中NULL profile_id记录: %', null_profile_id_metadata_count;
    RAISE NOTICE '- user_tags中NULL profile_id记录: %', null_profile_id_tags_count;
    
    IF null_profile_id_metadata_count > 0 OR null_profile_id_tags_count > 0 THEN
        RAISE EXCEPTION '数据迁移不完整，发现NULL的profile_id';
    END IF;
END $$;

-- 第7步：删除旧的外键约束
ALTER TABLE public.user_metadata 
DROP CONSTRAINT IF EXISTS user_metadata_user_id_fkey;

ALTER TABLE public.user_tags 
DROP CONSTRAINT IF EXISTS user_tags_user_id_fkey;

-- 第8步：设置profile_id为NOT NULL
ALTER TABLE public.user_metadata 
ALTER COLUMN profile_id SET NOT NULL;

ALTER TABLE public.user_tags 
ALTER COLUMN profile_id SET NOT NULL;

-- 第9步：创建新的外键约束
ALTER TABLE public.user_metadata 
ADD CONSTRAINT user_metadata_profile_id_fkey 
FOREIGN KEY (profile_id) 
REFERENCES public.user_profile(id) 
ON DELETE CASCADE;

ALTER TABLE public.user_tags 
ADD CONSTRAINT user_tags_profile_id_fkey 
FOREIGN KEY (profile_id) 
REFERENCES public.user_profile(id) 
ON DELETE CASCADE;

-- 第10步：创建索引提升性能
CREATE INDEX IF NOT EXISTS idx_user_metadata_profile_id 
ON public.user_metadata(profile_id);

CREATE INDEX IF NOT EXISTS idx_user_tags_profile_id 
ON public.user_tags(profile_id);

-- 第11步：删除旧的user_id列
ALTER TABLE public.user_metadata 
DROP COLUMN IF EXISTS user_id;

ALTER TABLE public.user_tags 
DROP COLUMN IF EXISTS user_id;

-- 第12步：重命名profile_id为user_id以保持API兼容性
ALTER TABLE public.user_metadata 
RENAME COLUMN profile_id TO user_id;

ALTER TABLE public.user_tags 
RENAME COLUMN profile_id TO user_id;

-- 第13步：重命名外键约束以保持一致性
ALTER TABLE public.user_metadata 
RENAME CONSTRAINT user_metadata_profile_id_fkey TO user_metadata_user_id_fkey;

ALTER TABLE public.user_tags 
RENAME CONSTRAINT user_tags_profile_id_fkey TO user_tags_user_id_fkey;

-- 第14步：重命名索引以保持一致性
ALTER INDEX IF EXISTS idx_user_metadata_profile_id 
RENAME TO idx_user_metadata_user_id;

ALTER INDEX IF EXISTS idx_user_tags_profile_id 
RENAME TO idx_user_tags_user_id;

-- 第15步：删除user_profile表中的旧user_id列
ALTER TABLE public.user_profile 
DROP COLUMN IF EXISTS user_id;

-- 第16步：更新行级安全策略
-- 删除旧的策略
DROP POLICY IF EXISTS "Users can only see their own metadata" ON public.user_metadata;
DROP POLICY IF EXISTS "Users can only see their own tags" ON public.user_tags;

-- 创建新的策略（基于user_profile.auth_user_id）
CREATE POLICY "Users can only see their own metadata" ON public.user_metadata
FOR ALL USING (
    user_id IN (
        SELECT id FROM public.user_profile 
        WHERE auth_user_id = auth.uid()
    )
);

CREATE POLICY "Users can only see their own tags" ON public.user_tags
FOR ALL USING (
    user_id IN (
        SELECT id FROM public.user_profile 
        WHERE auth_user_id = auth.uid()
    )
);

-- 第17步：创建便利视图（可选）
CREATE OR REPLACE VIEW public.user_metadata_with_profile AS
SELECT 
    um.*,
    up.display_name,
    up.email,
    up.auth_user_id
FROM public.user_metadata um
JOIN public.user_profile up ON um.user_id = up.id;

CREATE OR REPLACE VIEW public.user_tags_with_profile AS
SELECT 
    ut.*,
    up.display_name,
    up.email,
    up.auth_user_id
FROM public.user_tags ut
JOIN public.user_profile up ON ut.user_id = up.id;

-- 第18步：优化数据库性能
ANALYZE public.user_metadata;
ANALYZE public.user_tags;
ANALYZE public.user_profile;

-- 第19步：输出迁移完成信息
DO $$
DECLARE 
    profile_count INTEGER;
    metadata_count INTEGER;
    tags_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO profile_count FROM public.user_profile;
    SELECT COUNT(*) INTO metadata_count FROM public.user_metadata;
    SELECT COUNT(*) INTO tags_count FROM public.user_tags;
    
    RAISE NOTICE '=== 迁移完成 ===';
    RAISE NOTICE '- user_profile记录数: %', profile_count;
    RAISE NOTICE '- user_metadata记录数: %', metadata_count;
    RAISE NOTICE '- user_tags记录数: %', tags_count;
    RAISE NOTICE '- user_profile现在是真正的主表';
    RAISE NOTICE '- user_metadata和user_tags现在关联到user_profile.id';
END $$;

-- 提交事务
COMMIT;

-- 输出成功消息
SELECT 'Database schema refactoring completed successfully!' as message;
"""

def main():
    """执行迁移脚本"""
    
    print("🔄 准备执行用户表结构重构...")
    print("\n本次重构将：")
    print("1. 将user_metadata和user_tags的关联从user_profile.user_id改为user_profile.id")
    print("2. 删除user_profile.user_id列")
    print("3. 使user_profile成为真正的主表")
    print("4. 保持API兼容性")
    
    response = input("\n⚠️  这是一个重要的数据库结构变更，确定要继续吗？(输入 'YES' 确认): ")
    
    if response != 'YES':
        print("❌ 迁移已取消")
        return
    
    migration_sql = generate_migration_sql()
    
    print("\n📋 生成的迁移SQL脚本：")
    print("=" * 60)
    print(migration_sql)
    print("=" * 60)
    
    confirm = input("\n✅ 请检查SQL脚本，确认无误后输入 'EXECUTE' 执行: ")
    
    if confirm != 'EXECUTE':
        print("❌ 迁移已取消")
        return
    
    print("\n🚀 开始执行迁移...")
    print("📝 请将上述SQL脚本复制到Supabase SQL编辑器中执行")
    print("🔍 或使用Supabase CLI: supabase db push")
    
    print("\n✅ 迁移脚本已准备就绪！")

if __name__ == "__main__":
    main() 