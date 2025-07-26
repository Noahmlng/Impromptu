#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试外键迁移SQL脚本
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from migrate_foreign_keys_to_auth import generate_migration_sql

def test_sql_generation():
    """测试SQL生成"""
    print("🧪 测试SQL生成...")
    
    sql = generate_migration_sql()
    
    print("\n📄 生成的SQL内容:")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    
    # 检查关键语句是否存在
    required_statements = [
        "ALTER TABLE public.user_metadata",
        "ALTER TABLE public.user_tags", 
        "DROP CONSTRAINT IF EXISTS",
        "ADD CONSTRAINT",
        "REFERENCES auth.users(id)",
        "CREATE INDEX IF NOT EXISTS",
        "CREATE POLICY",
        "CREATE OR REPLACE VIEW"
    ]
    
    missing_statements = []
    for statement in required_statements:
        if statement not in sql:
            missing_statements.append(statement)
    
    if missing_statements:
        print(f"❌ 缺少必要的SQL语句: {missing_statements}")
        return False
    else:
        print("✅ SQL内容验证通过")
        return True

if __name__ == "__main__":
    test_sql_generation() 