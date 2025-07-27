
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
    