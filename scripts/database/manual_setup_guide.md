# 游戏解锁功能数据库表创建指南

## 🎯 目标
为低匹配度用户的游戏解锁功能创建 `user_unlocks` 表。

## 📋 方法一：Supabase Dashboard（推荐）

### 步骤：
1. 打开浏览器，访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 登录你的账户
3. 选择项目：`anxbbsrnjgmotxzysqwf`
4. 点击左侧菜单的 "SQL Editor"
5. 点击 "New query" 创建新查询
6. 复制下面的SQL语句，粘贴到编辑器中
7. 点击 "Run" 按钮执行

### SQL 语句：
```sql
-- 创建用户解锁记录表
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

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker ON user_unlocks(unlocker_user_id);
CREATE INDEX IF NOT EXISTS idx_user_unlocks_target ON user_unlocks(target_user_id);
CREATE INDEX IF NOT EXISTS idx_user_unlocks_unlocker_target ON user_unlocks(unlocker_user_id, target_user_id);
CREATE INDEX IF NOT EXISTS idx_user_unlocks_expires ON user_unlocks(expires_at) WHERE expires_at IS NOT NULL;

-- 添加表注释
COMMENT ON TABLE user_unlocks IS '用户解锁记录表，记录低匹配度用户的解锁信息';
COMMENT ON COLUMN user_unlocks.unlocker_user_id IS '解锁者的用户ID';
COMMENT ON COLUMN user_unlocks.target_user_id IS '被解锁用户的ID';
COMMENT ON COLUMN user_unlocks.unlock_type IS '解锁方式：game_success(游戏成功), game_fail(游戏失败), credits_direct(直接积分)';
COMMENT ON COLUMN user_unlocks.game_type IS '游戏类型：memory(记忆), quiz(问答), puzzle(拼图), reaction(反应)';
COMMENT ON COLUMN user_unlocks.game_score IS '游戏得分(0-100)';
COMMENT ON COLUMN user_unlocks.credits_spent IS '消费的积分数量';
COMMENT ON COLUMN user_unlocks.expires_at IS '解锁过期时间，NULL表示永不过期';
```

## 📋 方法二：命令行 psql（高级用户）

如果你有 psql 客户端：

```bash
# 使用Supabase连接字符串
psql "postgresql://postgres:[YOUR_PASSWORD]@db.anxbbsrnjgmotxzysqwf.supabase.co:5432/postgres" -f scripts/database/user_unlocks_table.sql
```

## ✅ 验证表创建成功

执行SQL后，可以通过以下方式验证：

### 在 SQL Editor 中运行：
```sql
-- 检查表是否存在
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'user_unlocks'
);

-- 查看表结构
\d user_unlocks

-- 查看索引
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'user_unlocks';
```

### 或者运行验证脚本：
```bash
python scripts/database/simple_create_table.py
```

## 🎮 功能说明

创建成功后，游戏解锁功能将包括：

- **记忆配对游戏** - 80分通过，失败扣5积分
- **兴趣问答挑战** - 70分通过，失败扣3积分  
- **拼图挑战** - 75分通过，失败扣4积分
- **反应速度测试** - 85分通过，失败扣2积分

## 📞 遇到问题？

如果遇到权限或其他问题：
1. 确保使用的是 Service Role Key
2. 检查 Supabase 项目的 RLS 设置
3. 联系项目管理员

## 🔄 完成后下一步

表创建成功后：
1. 启动后端服务验证API
2. 启动前端测试游戏功能
3. 检查低匹配度用户是否显示解锁按钮 