from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class UnlockRecord:
    """用户解锁记录"""
    id: str
    unlocker_user_id: str  # 解锁者
    target_user_id: str    # 被解锁的用户
    unlock_type: str       # 解锁方式：game_success/game_fail/credits_direct
    game_type: Optional[str] = None  # 游戏类型：memory/quiz/puzzle/reaction
    game_score: Optional[int] = None # 游戏得分
    credits_spent: int = 0           # 消费积分
    unlocked_at: datetime = None
    expires_at: Optional[datetime] = None  # 解锁有效期

@dataclass
class GameResult:
    """游戏结果"""
    success: bool
    score: int
    game_type: str
    duration_ms: int
    unlock_granted: bool = False
    credits_spent: int = 0
    message: str = ""

@dataclass
class UnlockStatus:
    """解锁状态"""
    is_unlocked: bool
    unlock_method: Optional[str] = None
    remaining_time: Optional[int] = None  # 剩余时间（秒）
    can_play_game: bool = True
    credits_needed: int = 10  # 直接解锁需要的积分

@dataclass
class GameConfig:
    """游戏配置"""
    game_type: str
    difficulty: str = "normal"
    time_limit: int = 60  # 秒
    success_threshold: int = 70  # 成功阈值分数
    credits_on_fail: int = 5  # 失败时扣除的积分 