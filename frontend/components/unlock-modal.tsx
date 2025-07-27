'use client'

import React, { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Progress } from './ui/progress'
import { X, Gamepad2, Coins, Trophy, Clock } from 'lucide-react'
import MemoryGame from './memory-game'
import QuizGame from './quiz-game'
import PuzzleGame from './puzzle-game'
import ReactionGame from './reaction-game'

interface UnlockModalProps {
  isOpen: boolean
  onClose: () => void
  targetUser: {
    id: string
    display_name: string
    email: string
    match_score: number
  }
  userCredits: number
  onUnlockSuccess: () => void
}

interface GameConfig {
  id: string
  name: string
  description: string
  timeLimit: number
  successThreshold: number
  creditsOnFail: number
  difficulty: string
  icon: string
}

const GAME_CONFIGS: GameConfig[] = [
  {
    id: 'memory',
    name: '记忆配对',
    description: '翻牌找相同图案，考验你的记忆力',
    timeLimit: 90,
    successThreshold: 80,
    creditsOnFail: 5,
    difficulty: '中等',
    icon: '🧠'
  },
  {
    id: 'quiz',
    name: '兴趣问答',
    description: '回答关于生活方式的问题',
    timeLimit: 60,
    successThreshold: 70,
    creditsOnFail: 3,
    difficulty: '简单',
    icon: '❓'
  },
  {
    id: 'puzzle',
    name: '拼图挑战',
    description: '在时间内完成数字拼图',
    timeLimit: 120,
    successThreshold: 75,
    creditsOnFail: 4,
    difficulty: '中等',
    icon: '🧩'
  },
  {
    id: 'reaction',
    name: '反应速度',
    description: '快速反应测试你的敏捷度',
    timeLimit: 30,
    successThreshold: 85,
    creditsOnFail: 2,
    difficulty: '困难',
    icon: '⚡'
  }
]

type GamePhase = 'selection' | 'playing' | 'result'

export default function UnlockModal({ isOpen, onClose, targetUser, userCredits, onUnlockSuccess }: UnlockModalProps) {
  const [currentPhase, setCurrentPhase] = useState<GamePhase>('selection')
  const [selectedGame, setSelectedGame] = useState<string | null>(null)
  const [gameResult, setGameResult] = useState<{
    score: number
    duration: number
    success: boolean
    unlocked: boolean
    message: string
  } | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // 重置状态
  useEffect(() => {
    if (isOpen) {
      setCurrentPhase('selection')
      setSelectedGame(null)
      setGameResult(null)
      setIsSubmitting(false)
    }
  }, [isOpen])

  // 开始游戏
  const startGame = (gameId: string) => {
    setSelectedGame(gameId)
    setCurrentPhase('playing')
  }

  // 游戏完成回调
  const handleGameComplete = async (score: number, duration: number) => {
    const gameConfig = GAME_CONFIGS.find(g => g.id === selectedGame)
    if (!gameConfig) return

    const success = score >= gameConfig.successThreshold
    setIsSubmitting(true)

    try {
      // 调用后端API提交游戏结果
      const response = await fetch('/api/unlock/game/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          target_user_id: targetUser.id,
          game_type: selectedGame,
          score: score,
          duration_ms: duration
        })
      })

      const result = await response.json()
      
      if (result.success) {
        setGameResult({
          score,
          duration,
          success: result.data.game_success,
          unlocked: result.data.unlock_granted,
          message: result.data.message
        })
        
        if (result.data.unlock_granted) {
          onUnlockSuccess()
        }
      } else {
        setGameResult({
          score,
          duration,
          success: false,
          unlocked: false,
          message: '提交结果失败，请重试'
        })
      }
    } catch (error) {
      console.error('提交游戏结果失败:', error)
      setGameResult({
        score,
        duration,
        success: false,
        unlocked: false,
        message: '网络错误，请重试'
      })
    } finally {
      setIsSubmitting(false)
      setCurrentPhase('result')
    }
  }

  // 直接用积分解锁
  const handleDirectUnlock = async () => {
    setIsSubmitting(true)

    try {
      const response = await fetch('/api/unlock/direct', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          target_user_id: targetUser.id
        })
      })

      const result = await response.json()
      
      if (result.success) {
        onUnlockSuccess()
        onClose()
      } else {
        alert(result.message)
      }
    } catch (error) {
      console.error('直接解锁失败:', error)
      alert('解锁失败，请重试')
    } finally {
      setIsSubmitting(false)
    }
  }

  // 返回游戏选择
  const backToSelection = () => {
    setCurrentPhase('selection')
    setSelectedGame(null)
    setGameResult(null)
  }

  if (!isOpen) return null

  // 游戏进行中
  if (currentPhase === 'playing' && selectedGame) {
    const gameConfig = GAME_CONFIGS.find(g => g.id === selectedGame)!
    
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          {/* 头部 */}
          <div className="p-4 border-b flex items-center justify-between">
            <h2 className="text-xl font-bold flex items-center">
              <span className="text-2xl mr-2">{gameConfig.icon}</span>
              {gameConfig.name}
            </h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* 游戏区域 */}
          <div className="p-4">
            {selectedGame === 'memory' && <MemoryGame onGameComplete={handleGameComplete} timeLimit={gameConfig.timeLimit} />}
            {selectedGame === 'quiz' && <QuizGame onGameComplete={handleGameComplete} timeLimit={gameConfig.timeLimit} />}
            {selectedGame === 'puzzle' && <PuzzleGame onGameComplete={handleGameComplete} timeLimit={gameConfig.timeLimit} />}
            {selectedGame === 'reaction' && <ReactionGame onGameComplete={handleGameComplete} timeLimit={gameConfig.timeLimit} />}
          </div>
        </div>
      </div>
    )
  }

  // 游戏结果
  if (currentPhase === 'result' && gameResult) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg w-full max-w-2xl">
          {/* 头部 */}
          <div className="p-6 border-b text-center">
            <h2 className="text-2xl font-bold mb-2">游戏结果</h2>
            <div className="flex items-center justify-center space-x-2">
              <span className="w-8 h-8 rounded-full bg-gradient-to-r from-primary/20 to-primary/10 flex items-center justify-center">
                {targetUser.display_name.charAt(0)}
              </span>
              <span className="font-medium">{targetUser.display_name}</span>
            </div>
          </div>

          {/* 结果内容 */}
          <div className="p-6">
            <div className="text-center mb-6">
              {gameResult.unlocked ? (
                <div className="text-center">
                  <Trophy className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-green-600 mb-2">解锁成功！</h3>
                  <p className="text-muted-foreground">你已成功解锁该用户，现在可以查看完整信息</p>
                </div>
              ) : (
                <div className="text-center">
                  <div className="h-16 w-16 rounded-full bg-orange-100 flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">😔</span>
                  </div>
                  <h3 className="text-2xl font-bold text-orange-600 mb-2">游戏未达标</h3>
                  <p className="text-muted-foreground">但是已经扣除少量积分帮你解锁了</p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
              <div className="p-3 bg-blue-50 rounded-lg text-center">
                <div className="text-blue-600 font-medium">游戏得分</div>
                <div className="text-2xl font-bold">{gameResult.score}</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg text-center">
                <div className="text-green-600 font-medium">用时</div>
                <div className="text-2xl font-bold">
                  {Math.floor(gameResult.duration / 60000)}:{((gameResult.duration % 60000) / 1000).toFixed(0).padStart(2, '0')}
                </div>
              </div>
            </div>

            <div className="text-center p-4 bg-muted rounded-lg mb-6">
              <p className="text-sm">{gameResult.message}</p>
            </div>

            <div className="flex space-x-3">
              <Button variant="outline" onClick={backToSelection} className="flex-1">
                再试一次
              </Button>
              <Button onClick={onClose} className="flex-1">
                完成
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 游戏选择界面
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* 头部 */}
        <div className="p-6 border-b">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">解锁用户</h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex items-center space-x-3 p-4 bg-muted rounded-lg">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary/20 to-primary/10 flex items-center justify-center">
              <span className="text-primary font-medium text-lg">
                {targetUser.display_name.charAt(0)}
              </span>
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-lg">{targetUser.display_name}</h3>
              <p className="text-sm text-muted-foreground">匹配度: {Math.round(targetUser.match_score * 100)}%</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">你的积分</div>
              <div className="text-lg font-bold flex items-center">
                <Coins className="h-4 w-4 mr-1" />
                {userCredits}
              </div>
            </div>
          </div>
        </div>

        {/* 内容 */}
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-lg font-bold mb-2">解锁方式</h3>
            <p className="text-muted-foreground text-sm">
              选择一个小游戏挑战，成功完成即可免费解锁用户！失败也会扣除少量积分帮你解锁。
            </p>
          </div>

          {/* 游戏选项 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {GAME_CONFIGS.map((game) => (
              <Card key={game.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer border-2 hover:border-primary" onClick={() => startGame(game.id)}>
                <div className="flex items-start space-x-3">
                  <div className="text-3xl">{game.icon}</div>
                  <div className="flex-1">
                    <h4 className="font-medium text-lg">{game.name}</h4>
                    <p className="text-sm text-muted-foreground mb-3">{game.description}</p>
                    
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{game.timeLimit}秒</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Trophy className="h-3 w-3" />
                        <span>{game.successThreshold}分通过</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Gamepad2 className="h-3 w-3" />
                        <span>{game.difficulty}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Coins className="h-3 w-3" />
                        <span>失败扣{game.creditsOnFail}分</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* 直接解锁选项 */}
          <div className="border-t pt-6">
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div>
                <h4 className="font-medium">直接解锁</h4>
                <p className="text-sm text-muted-foreground">跳过游戏，直接消费10积分解锁</p>
              </div>
              <Button 
                variant="outline" 
                onClick={handleDirectUnlock}
                disabled={userCredits < 10 || isSubmitting}
                className="min-w-[120px]"
              >
                {isSubmitting ? '处理中...' : `花费10积分解锁`}
              </Button>
            </div>
            
            {userCredits < 10 && (
              <p className="text-sm text-red-500 mt-2">积分不足，需要10积分才能直接解锁</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 