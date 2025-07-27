from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from backend.services.auth_service import get_current_user
from backend.services.unlock_service import unlock_service
from backend.models.unlock_result import GameResult

router = APIRouter()

class GameSubmissionRequest(BaseModel):
    """游戏提交请求"""
    target_user_id: str
    game_type: str  # memory, quiz, puzzle, reaction
    score: int
    duration_ms: int

class DirectUnlockRequest(BaseModel):
    """直接解锁请求"""
    target_user_id: str

@router.get("/status/{target_user_id}")
async def check_unlock_status(target_user_id: str, current_user: Dict = Depends(get_current_user)):
    """检查用户解锁状态"""
    try:
        unlocker_user_id = current_user['user_id']
        status = await unlock_service.check_unlock_status(unlocker_user_id, target_user_id)
        
        return {
            "success": True,
            "data": {
                "is_unlocked": status.is_unlocked,
                "unlock_method": status.unlock_method,
                "remaining_time": status.remaining_time,
                "can_play_game": status.can_play_game,
                "credits_needed": status.credits_needed
            }
        }
        
    except Exception as e:
        print(f"检查解锁状态失败: {e}")
        raise HTTPException(status_code=500, detail="检查解锁状态失败")

@router.post("/game/submit")
async def submit_game_result(request: GameSubmissionRequest, current_user: Dict = Depends(get_current_user)):
    """提交游戏结果"""
    try:
        unlocker_user_id = current_user['user_id']
        user_credits = current_user['profile'].get('credits', 0)
        
        # 检查是否已解锁
        status = await unlock_service.check_unlock_status(unlocker_user_id, request.target_user_id)
        if status.is_unlocked:
            return {
                "success": False,
                "message": "用户已经解锁"
            }
        
        # 处理游戏结果
        game_result = GameResult(
            success=False,  # 这个会在服务中重新计算
            score=request.score,
            game_type=request.game_type,
            duration_ms=request.duration_ms
        )
        
        result = await unlock_service.process_game_result(
            unlocker_user_id, request.target_user_id, game_result, user_credits
        )
        
        return {
            "success": True,
            "data": {
                "game_success": result.success,
                "score": result.score,
                "unlock_granted": result.unlock_granted,
                "credits_spent": result.credits_spent,
                "message": result.message
            }
        }
        
    except Exception as e:
        print(f"提交游戏结果失败: {e}")
        raise HTTPException(status_code=500, detail="提交游戏结果失败")

@router.post("/direct")
async def direct_unlock(request: DirectUnlockRequest, current_user: Dict = Depends(get_current_user)):
    """直接用积分解锁"""
    try:
        unlocker_user_id = current_user['user_id']
        user_credits = current_user['profile'].get('credits', 0)
        
        # 检查是否已解锁
        status = await unlock_service.check_unlock_status(unlocker_user_id, request.target_user_id)
        if status.is_unlocked:
            return {
                "success": False,
                "message": "用户已经解锁"
            }
        
        result = await unlock_service.direct_unlock_with_credits(
            unlocker_user_id, request.target_user_id, user_credits
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "data": {
                "credits_spent": result.get("credits_spent", 0)
            }
        }
        
    except Exception as e:
        print(f"直接解锁失败: {e}")
        raise HTTPException(status_code=500, detail="直接解锁失败")

@router.get("/games/config")
async def get_game_configs():
    """获取游戏配置信息"""
    try:
        configs = {
            "memory": {
                "name": "记忆配对",
                "description": "翻牌找相同图案，考验你的记忆力",
                "time_limit": 90,
                "success_threshold": 80,
                "credits_on_fail": 5,
                "difficulty": "中等"
            },
            "quiz": {
                "name": "兴趣问答",
                "description": "回答关于对方兴趣的问题",
                "time_limit": 60,
                "success_threshold": 70,
                "credits_on_fail": 3,
                "difficulty": "简单"
            },
            "puzzle": {
                "name": "拼图挑战",
                "description": "在时间内完成拼图",
                "time_limit": 120,
                "success_threshold": 75,
                "credits_on_fail": 4,
                "difficulty": "中等"
            },
            "reaction": {
                "name": "反应速度",
                "description": "快速反应测试你的敏捷度",
                "time_limit": 30,
                "success_threshold": 85,
                "credits_on_fail": 2,
                "difficulty": "困难"
            }
        }
        
        return {
            "success": True,
            "data": configs
        }
        
    except Exception as e:
        print(f"获取游戏配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取游戏配置失败") 