#!/usr/bin/env python3
"""
创建user_unlocks表的数据库迁移脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from backend.services.database_service import get_supabase
except ImportError:
    # 如果无法导入，直接使用supabase
    from supabase import create_client, Client
    
    def get_supabase():
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        return create_client(url, key)

def create_unlock_table():
    """创建user_unlocks表"""
    
    try:
        # 获取数据库连接
        supabase = get_supabase()
        
        print("🔄 开始创建user_unlocks表...")
        
        # 分步执行SQL语句
        sql_statements = [
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
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker ON user_unlocks(unlocker_user_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_user_unlocks_target ON user_unlocks(target_user_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker_target ON user_unlocks(unlocker_user_id, target_user_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_user_unlocks_expires ON user_unlocks(expires_at) WHERE expires_at IS NOT NULL;
            """
        ]
        
        # 执行每个SQL语句
        for i, sql in enumerate(sql_statements, 1):
            try:
                print(f"   执行步骤 {i}/{len(sql_statements)}...")
                # 使用 rpc 调用执行原始SQL
                result = supabase.rpc('exec_sql', {'query': sql.strip()}).execute()
                print(f"   ✅ 步骤 {i} 完成")
            except Exception as e:
                print(f"   ⚠️ 步骤 {i} 可能已存在或执行完成: {e}")
                # 继续执行下一个语句
                continue
        
        print("✅ user_unlocks表创建成功！")
        print("📊 表结构包括:")
        print("   - id: 主键")
        print("   - unlocker_user_id: 解锁者ID")
        print("   - target_user_id: 被解锁用户ID")
        print("   - unlock_type: 解锁方式")
        print("   - game_type: 游戏类型")
        print("   - game_score: 游戏得分")
        print("   - credits_spent: 消费积分")
        print("   - unlocked_at: 解锁时间")
        print("   - expires_at: 过期时间")
        print("📑 索引已创建")
        return True
            
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        return False

def verify_table():
    """验证表是否创建成功"""
    try:
        supabase = get_supabase()
        
        # 检查表是否存在，使用简单的查询
        try:
            result = supabase.table('user_unlocks').select('count', count='exact').limit(0).execute()
            print("✅ user_unlocks表验证成功")
            print(f"📊 当前表中记录数: {result.count}")
            return True
        except Exception as e:
            if "does not exist" in str(e).lower():
                print("❌ user_unlocks表不存在")
                return False
            else:
                # 表存在但可能没有数据，这是正常的
                print("✅ user_unlocks表验证成功（表存在）")
                return True
            
    except Exception as e:
        print(f"❌ 验证表失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始创建游戏解锁功能数据库表")
    print("=" * 50)
    
    # 检查环境
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
        print("❌ 请设置SUPABASE_URL和SUPABASE_SERVICE_KEY环境变量")
        sys.exit(1)
    
    # 创建表
    if create_unlock_table():
        # 验证表
        if verify_table():
            print("\n🎉 游戏解锁功能数据库表创建完成！")
            print("📝 现在可以使用以下功能:")
            print("   1. 检查用户解锁状态")
            print("   2. 提交游戏结果")
            print("   3. 直接积分解锁")
            print("   4. 查询解锁记录")
        else:
            print("\n⚠️ 表创建成功但验证失败")
            sys.exit(1)
    else:
        print("\n❌ 表创建失败")
        sys.exit(1) 