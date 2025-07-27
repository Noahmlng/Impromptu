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

-- 创建触发器用于自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_unlocks_modtime 
    BEFORE UPDATE ON user_unlocks 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- 添加注释
COMMENT ON TABLE user_unlocks IS '用户解锁记录表，记录低匹配度用户的解锁信息';
COMMENT ON COLUMN user_unlocks.unlocker_user_id IS '解锁者的用户ID';
COMMENT ON COLUMN user_unlocks.target_user_id IS '被解锁用户的ID';
COMMENT ON COLUMN user_unlocks.unlock_type IS '解锁方式：game_success(游戏成功), game_fail(游戏失败), credits_direct(直接积分)';
COMMENT ON COLUMN user_unlocks.game_type IS '游戏类型：memory(记忆), quiz(问答), puzzle(拼图), reaction(反应)';
COMMENT ON COLUMN user_unlocks.game_score IS '游戏得分(0-100)';
COMMENT ON COLUMN user_unlocks.credits_spent IS '消费的积分数量';
COMMENT ON COLUMN user_unlocks.unlocked_at IS '解锁时间';
COMMENT ON COLUMN user_unlocks.expires_at IS '解锁过期时间，NULL表示永不过期'; 