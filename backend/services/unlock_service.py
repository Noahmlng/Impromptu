import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from backend.services.database_service import get_supabase
from backend.models.unlock_result import UnlockRecord, GameResult, UnlockStatus, GameConfig

class UnlockService:
    """用户解锁服务"""
    
    def __init__(self):
        self.client = get_supabase()
        
    async def check_unlock_status(self, unlocker_user_id: str, target_user_id: str) -> UnlockStatus:
        """检查解锁状态"""
        try:
            # 查询是否已解锁
            response = self.client.table('user_unlocks').select('*').eq(
                'unlocker_user_id', unlocker_user_id
            ).eq('target_user_id', target_user_id).execute()
            
            if response.data:
                unlock_record = response.data[0]
                expires_at = datetime.fromisoformat(unlock_record['expires_at']) if unlock_record['expires_at'] else None
                
                # 检查是否过期
                if expires_at and expires_at > datetime.utcnow():
                    remaining_time = int((expires_at - datetime.utcnow()).total_seconds())
                    return UnlockStatus(
                        is_unlocked=True,
                        unlock_method=unlock_record['unlock_type'],
                        remaining_time=remaining_time,
                        can_play_game=False
                    )
            
            return UnlockStatus(
                is_unlocked=False,
                can_play_game=True,
                credits_needed=10
            )
            
        except Exception as e:
            print(f"检查解锁状态失败: {e}")
            return UnlockStatus(is_unlocked=False, can_play_game=True)
    
    async def create_unlock_record(self, record: UnlockRecord) -> bool:
        """创建解锁记录"""
        try:
            data = {
                'id': record.id,
                'unlocker_user_id': record.unlocker_user_id,
                'target_user_id': record.target_user_id,
                'unlock_type': record.unlock_type,
                'game_type': record.game_type,
                'game_score': record.game_score,
                'credits_spent': record.credits_spent,
                'unlocked_at': record.unlocked_at.isoformat() if record.unlocked_at else datetime.utcnow().isoformat(),
                'expires_at': record.expires_at.isoformat() if record.expires_at else None
            }
            
            response = self.client.table('user_unlocks').insert(data).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"创建解锁记录失败: {e}")
            return False
    
    async def process_game_result(self, unlocker_user_id: str, target_user_id: str, 
                                game_result: GameResult, user_credits: int) -> GameResult:
        """处理游戏结果"""
        try:
            config = self.get_game_config(game_result.game_type)
            
            # 判断游戏是否成功
            success = game_result.score >= config.success_threshold
            unlock_granted = False
            credits_spent = 0
            message = ""
            
            if success:
                # 游戏成功，免费解锁
                unlock_granted = True
                message = "恭喜！游戏成功，免费解锁用户！"
                unlock_type = "game_success"
            else:
                # 游戏失败，检查积分是否足够
                if user_credits >= config.credits_on_fail:
                    unlock_granted = True
                    credits_spent = config.credits_on_fail
                    message = f"游戏失败，但已扣除{credits_spent}积分解锁用户"
                    unlock_type = "game_fail"
                else:
                    message = f"游戏失败且积分不足（需要{config.credits_on_fail}积分）"
                    unlock_type = "game_fail_no_credits"
            
            if unlock_granted:
                # 创建解锁记录
                record = UnlockRecord(
                    id=str(uuid.uuid4()),
                    unlocker_user_id=unlocker_user_id,
                    target_user_id=target_user_id,
                    unlock_type=unlock_type,
                    game_type=game_result.game_type,
                    game_score=game_result.score,
                    credits_spent=credits_spent,
                    unlocked_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=7)  # 7天有效期
                )
                
                await self.create_unlock_record(record)
                
                # 如果需要扣积分，更新用户积分
                if credits_spent > 0:
                    await self.update_user_credits(unlocker_user_id, -credits_spent)
            
            return GameResult(
                success=success,
                score=game_result.score,
                game_type=game_result.game_type,
                duration_ms=game_result.duration_ms,
                unlock_granted=unlock_granted,
                credits_spent=credits_spent,
                message=message
            )
            
        except Exception as e:
            print(f"处理游戏结果失败: {e}")
            return GameResult(
                success=False,
                score=0,
                game_type=game_result.game_type,
                duration_ms=0,
                message="处理游戏结果时发生错误"
            )
    
    async def direct_unlock_with_credits(self, unlocker_user_id: str, target_user_id: str, 
                                       user_credits: int) -> Dict:
        """直接用积分解锁"""
        try:
            credits_needed = 10
            
            if user_credits < credits_needed:
                return {
                    "success": False,
                    "message": f"积分不足，需要{credits_needed}积分"
                }
            
            # 创建解锁记录
            record = UnlockRecord(
                id=str(uuid.uuid4()),
                unlocker_user_id=unlocker_user_id,
                target_user_id=target_user_id,
                unlock_type="credits_direct",
                credits_spent=credits_needed,
                unlocked_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            
            success = await self.create_unlock_record(record)
            if success:
                await self.update_user_credits(unlocker_user_id, -credits_needed)
                return {
                    "success": True,
                    "message": f"成功解锁！扣除{credits_needed}积分",
                    "credits_spent": credits_needed
                }
            else:
                return {
                    "success": False,
                    "message": "解锁失败，请重试"
                }
                
        except Exception as e:
            print(f"直接解锁失败: {e}")
            return {
                "success": False,
                "message": "解锁失败，请重试"
            }
    
    async def update_user_credits(self, user_id: str, credits_change: int) -> bool:
        """更新用户积分"""
        try:
            # 获取当前积分
            response = self.client.table('user_profile').select('credits').eq('id', user_id).execute()
            if not response.data:
                return False
            
            current_credits = response.data[0].get('credits', 0)
            new_credits = max(0, current_credits + credits_change)
            
            # 更新积分
            update_response = self.client.table('user_profile').update({
                'credits': new_credits
            }).eq('id', user_id).execute()
            
            return len(update_response.data) > 0
            
        except Exception as e:
            print(f"更新用户积分失败: {e}")
            return False
    
    def get_game_config(self, game_type: str) -> GameConfig:
        """获取游戏配置"""
        configs = {
            "memory": GameConfig(
                game_type="memory",
                time_limit=90,
                success_threshold=80,
                credits_on_fail=5
            ),
            "quiz": GameConfig(
                game_type="quiz",
                time_limit=60,
                success_threshold=70,
                credits_on_fail=3
            ),
            "puzzle": GameConfig(
                game_type="puzzle",
                time_limit=120,
                success_threshold=75,
                credits_on_fail=4
            ),
            "reaction": GameConfig(
                game_type="reaction",
                time_limit=30,
                success_threshold=85,
                credits_on_fail=2
            )
        }
        
        return configs.get(game_type, configs["memory"])

unlock_service = UnlockService() 