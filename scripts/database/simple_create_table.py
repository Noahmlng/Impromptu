#!/usr/bin/env python3
"""
简化的数据库表创建脚本 - 直接使用SQL语句
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def create_unlock_table_directly():
    """使用直接的方式创建表"""
    
    # SQL语句
    create_table_sql = """
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
    );
    
    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker ON user_unlocks(unlocker_user_id);
    CREATE INDEX IF NOT EXISTS idx_user_unlocks_target ON user_unlocks(target_user_id);
    CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker_target ON user_unlocks(unlocker_user_id, target_user_id);
    CREATE INDEX IF NOT EXISTS idx_user_unlocks_expires ON user_unlocks(expires_at) WHERE expires_at IS NOT NULL;
    """
    
    print("🔄 创建user_unlocks表...")
    print("📝 SQL语句:")
    print(create_table_sql)
    print("\n" + "="*60)
    
    # 提供多种执行方法
    print("请选择执行方法:")
    print("1. 复制SQL到Supabase SQL编辑器手动执行")
    print("2. 使用psql命令行工具执行")
    print("3. 保存SQL到文件")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        print("\n📋 请按以下步骤操作:")
        print("1. 打开 Supabase Dashboard")
        print("2. 进入 SQL Editor")
        print("3. 复制上面的SQL语句")
        print("4. 粘贴并运行")
        return True
        
    elif choice == "2":
        print("\n💻 使用psql执行:")
        supabase_url = os.getenv("SUPABASE_URL", "")
        if supabase_url:
            # 从URL提取连接信息
            print("请使用以下命令:")
            print(f"psql '{supabase_url.replace('https://', 'postgresql://postgres:[PASSWORD]@').replace('.supabase.co', '.supabase.co:5432/postgres')}' -c \"$(cat create_table.sql)\"")
        else:
            print("无法获取Supabase URL")
        return True
        
    elif choice == "3":
        # 保存到文件
        sql_file = Path(__file__).parent / "user_unlocks_table.sql"
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(create_table_sql)
        print(f"\n💾 SQL已保存到: {sql_file}")
        print("你可以在Supabase SQL编辑器中执行此文件")
        return True
        
    else:
        print("❌ 无效选择")
        return False

def test_table_creation():
    """测试表是否创建成功"""
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("❌ 缺少Supabase连接信息")
            return False
            
        supabase = create_client(url, key)
        
        # 尝试查询表
        result = supabase.table('user_unlocks').select('count', count='exact').limit(0).execute()
        print(f"✅ user_unlocks表验证成功! 当前记录数: {result.count}")
        return True
        
    except Exception as e:
        if "does not exist" in str(e).lower():
            print("❌ user_unlocks表尚未创建")
        else:
            print(f"❓ 表状态检查: {e}")
        return False

if __name__ == "__main__":
    print("🚀 创建游戏解锁功能数据库表")
    print("=" * 50)
    
    # 先检查表是否已存在
    print("🔍 检查表是否已存在...")
    if test_table_creation():
        print("✅ 表已存在，无需重复创建!")
        sys.exit(0)
    
    # 创建表
    if create_unlock_table_directly():
        print("\n⏳ 请执行SQL后，再次运行此脚本验证...")
        input("按回车键验证表创建结果...")
        
        if test_table_creation():
            print("\n🎉 游戏解锁功能数据库表创建完成！")
        else:
            print("\n⚠️ 请检查SQL是否正确执行")
    else:
        print("\n❌ 操作失败")
        sys.exit(1) 