'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Progress } from './ui/progress'
import { Target, Zap } from 'lucide-react'

interface ReactionGameProps {
  onGameComplete: (score: number, duration: number) => void
  timeLimit: number // 秒
}

interface GameTarget {
  id: number
  x: number
  y: number
  isActive: boolean
  timeCreated: number
}

export default function ReactionGame({ onGameComplete, timeLimit }: ReactionGameProps) {
  const [targets, setTargets] = useState<GameTarget[]>([])
  const [score, setScore] = useState(0)
  const [hits, setHits] = useState(0)
  const [misses, setMisses] = useState(0)
  const [totalTargets, setTotalTargets] = useState(0)
  const [timeLeft, setTimeLeft] = useState(timeLimit)
  const [gameStarted, setGameStarted] = useState(false)
  const [gameEnded, setGameEnded] = useState(false)
  const [reactionTimes, setReactionTimes] = useState<number[]>([])
  const [nextTargetTimeout, setNextTargetTimeout] = useState<NodeJS.Timeout | null>(null)

  // 创建新目标
  const createTarget = useCallback(() => {
    if (!gameStarted || gameEnded) return

    const newTarget: GameTarget = {
      id: Date.now(),
      x: Math.random() * 80 + 10, // 10-90% of container width
      y: Math.random() * 80 + 10, // 10-90% of container height
      isActive: true,
      timeCreated: Date.now()
    }

    setTargets(prev => [...prev, newTarget])
    setTotalTargets(prev => prev + 1)

    // 目标2秒后自动消失
    setTimeout(() => {
      setTargets(prev => prev.filter(t => t.id !== newTarget.id))
      setMisses(prev => prev + 1)
    }, 2000)

    // 安排下一个目标（随机间隔1-3秒）
    if (gameStarted && !gameEnded) {
      const nextDelay = 1000 + Math.random() * 2000
      const timeout = setTimeout(createTarget, nextDelay)
      setNextTargetTimeout(timeout)
    }
  }, [gameStarted, gameEnded])

  // 开始游戏
  const startGame = () => {
    setGameStarted(true)
    setTargets([])
    setScore(0)
    setHits(0)
    setMisses(0)
    setTotalTargets(0)
    setReactionTimes([])
    
    // 创建第一个目标
    setTimeout(createTarget, 1000)
  }

  // 点击目标
  const hitTarget = (target: GameTarget) => {
    if (!gameStarted || gameEnded) return

    const reactionTime = Date.now() - target.timeCreated
    const newReactionTimes = [...reactionTimes, reactionTime]
    setReactionTimes(newReactionTimes)

    // 移除被点击的目标
    setTargets(prev => prev.filter(t => t.id !== target.id))
    setHits(prev => prev + 1)

    // 计算分数（反应时间越快分数越高）
    let points = 10
    if (reactionTime < 300) points = 20      // 超快反应
    else if (reactionTime < 500) points = 15 // 快速反应
    else if (reactionTime < 800) points = 10 // 正常反应
    else points = 5                          // 慢反应

    setScore(prev => prev + points)
  }

  // 点击空白区域（失误）
  const missClick = () => {
    if (!gameStarted || gameEnded) return
    setMisses(prev => prev + 1)
    setScore(prev => Math.max(0, prev - 5)) // 失误扣5分
  }

  // 计算最终分数
  const calculateFinalScore = useCallback(() => {
    if (hits === 0) return 0

    const accuracy = hits / (hits + misses)
    const avgReactionTime = reactionTimes.length > 0 
      ? reactionTimes.reduce((sum, time) => sum + time, 0) / reactionTimes.length 
      : 1000

    // 基础分：准确率 * 50
    const accuracyScore = accuracy * 50

    // 反应时间分：越快分数越高
    let speedScore = 0
    if (avgReactionTime < 300) speedScore = 50
    else if (avgReactionTime < 400) speedScore = 40
    else if (avgReactionTime < 500) speedScore = 30
    else if (avgReactionTime < 600) speedScore = 20
    else if (avgReactionTime < 800) speedScore = 10
    else speedScore = 5

    // 最低命中数要求
    const minHitsBonus = hits >= 10 ? 10 : 0

    return Math.min(100, Math.round(accuracyScore + speedScore + minHitsBonus))
  }, [hits, misses, reactionTimes])

  // 游戏计时器
  useEffect(() => {
    if (!gameStarted || gameEnded) return

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          setGameEnded(true)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [gameStarted, gameEnded])

  // 游戏结束处理
  useEffect(() => {
    if (gameEnded) {
      // 清除下一个目标的定时器
      if (nextTargetTimeout) {
        clearTimeout(nextTargetTimeout)
      }
      
      const finalScore = calculateFinalScore()
      const duration = (timeLimit - timeLeft) * 1000
      setTimeout(() => {
        onGameComplete(finalScore, duration)
      }, 2000)
    }
  }, [gameEnded, calculateFinalScore, onGameComplete, timeLimit, timeLeft, nextTargetTimeout])

  // 清理定时器
  useEffect(() => {
    return () => {
      if (nextTargetTimeout) {
        clearTimeout(nextTargetTimeout)
      }
    }
  }, [nextTargetTimeout])

  const progressPercentage = (timeLeft / timeLimit) * 100
  const accuracy = totalTargets > 0 ? (hits / totalTargets) * 100 : 0
  const avgReactionTime = reactionTimes.length > 0 
    ? reactionTimes.reduce((sum, time) => sum + time, 0) / reactionTimes.length 
    : 0

  if (!gameStarted) {
    return (
      <div className="max-w-2xl mx-auto p-4 text-center">
        <h3 className="text-2xl font-bold mb-2">反应速度挑战</h3>
        <p className="text-muted-foreground mb-6">
          快速点击出现的目标，测试你的反应速度！
        </p>
        
        <div className="mb-6 p-4 bg-muted rounded-lg">
          <h4 className="font-medium mb-2">游戏规则：</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• 点击屏幕上出现的目标获得分数</li>
            <li>• 反应越快分数越高</li>
            <li>• 目标2秒后自动消失</li>
            <li>• 点击空白区域会扣分</li>
            <li>• 时间限制{timeLimit}秒</li>
            <li>• 目标分数85分以上解锁成功</li>
          </ul>
        </div>

        <Button onClick={startGame} size="lg">
          <Zap className="mr-2 h-5 w-5" />
          开始挑战
        </Button>
      </div>
    )
  }

  if (gameEnded) {
    const finalScore = calculateFinalScore()
    
    return (
      <div className="max-w-2xl mx-auto p-4 text-center">
        <div className="p-6 bg-muted rounded-lg">
          <h3 className="text-2xl font-bold mb-4">挑战完成！</h3>
          <div className="text-4xl font-bold text-primary mb-4">{finalScore}分</div>
          
          <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-green-600 font-medium">命中率</div>
              <div className="text-lg font-bold">{accuracy.toFixed(1)}%</div>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-blue-600 font-medium">平均反应</div>
              <div className="text-lg font-bold">{avgReactionTime.toFixed(0)}ms</div>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <div className="text-purple-600 font-medium">命中数</div>
              <div className="text-lg font-bold">{hits}/{totalTargets}</div>
            </div>
          </div>

          <p className="text-muted-foreground">
            {finalScore >= 85 ? '恭喜！反应速度优秀，即将免费解锁用户' : '反应速度有待提高，但别担心，我们会帮你解锁的'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="mb-4">
        {/* 游戏信息 */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex space-x-6 text-sm">
            <span className="font-medium">分数: {score}</span>
            <span>命中: {hits}</span>
            <span>失误: {misses}</span>
            <span>准确率: {accuracy.toFixed(1)}%</span>
          </div>
          <div className="text-sm font-medium">
            时间: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
          </div>
        </div>

        {/* 时间进度条 */}
        <Progress value={progressPercentage} className="mb-4" />
      </div>

      {/* 游戏区域 */}
      <Card 
        className="relative bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-dashed border-gray-300"
        style={{ height: '400px' }}
        onClick={missClick}
      >
        <div className="absolute inset-0 p-4">
          {/* 游戏提示 */}
          {targets.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">等待目标出现...</p>
              </div>
            </div>
          )}

          {/* 目标 */}
          {targets.map((target) => (
            <div
              key={target.id}
              className="absolute w-12 h-12 bg-red-500 rounded-full cursor-pointer
                         border-4 border-white shadow-lg transform transition-transform
                         hover:scale-110 animate-pulse"
              style={{
                left: `${target.x}%`,
                top: `${target.y}%`,
                transform: 'translate(-50%, -50%)'
              }}
              onClick={(e) => {
                e.stopPropagation()
                hitTarget(target)
              }}
            >
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-3 h-3 bg-white rounded-full"></div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* 游戏提示 */}
      <div className="mt-4 text-center text-sm text-muted-foreground">
        <p>快速点击红色目标获得分数，避免点击空白区域</p>
        {reactionTimes.length > 0 && (
          <p className="mt-1">
            最快反应: {Math.min(...reactionTimes)}ms | 
            平均反应: {avgReactionTime.toFixed(0)}ms
          </p>
        )}
      </div>
    </div>
  )
} 