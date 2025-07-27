'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Progress } from './ui/progress'
import { RotateCcw } from 'lucide-react'

interface PuzzleGameProps {
  onGameComplete: (score: number, duration: number) => void
  timeLimit: number // 秒
}

interface PuzzlePiece {
  id: number
  correctPosition: number
  currentPosition: number
  isEmpty: boolean
}

const PUZZLE_SIZE = 4 // 4x4拼图

export default function PuzzleGame({ onGameComplete, timeLimit }: PuzzleGameProps) {
  const [pieces, setPieces] = useState<PuzzlePiece[]>([])
  const [emptyPosition, setEmptyPosition] = useState(15) // 空格位置
  const [moves, setMoves] = useState(0)
  const [timeLeft, setTimeLeft] = useState(timeLimit)
  const [gameStarted, setGameStarted] = useState(false)
  const [gameEnded, setGameEnded] = useState(false)
  const [score, setScore] = useState(0)
  const [isCompleted, setIsCompleted] = useState(false)

  // 初始化拼图
  const initializePuzzle = useCallback(() => {
    const initialPieces: PuzzlePiece[] = []
    
    // 创建拼图块（除了最后一个空格）
    for (let i = 0; i < PUZZLE_SIZE * PUZZLE_SIZE; i++) {
      initialPieces.push({
        id: i,
        correctPosition: i,
        currentPosition: i,
        isEmpty: i === 15 // 最后一个是空格
      })
    }
    
    // 打乱拼图（确保有解）
    const shuffledPieces = shufflePuzzle(initialPieces)
    setPieces(shuffledPieces)
    setEmptyPosition(15)
    setMoves(0)
    setTimeLeft(timeLimit)
    setGameStarted(false)
    setGameEnded(false)
    setScore(0)
    setIsCompleted(false)
  }, [timeLimit])

  // 打乱拼图（确保可解）
  const shufflePuzzle = (pieces: PuzzlePiece[]): PuzzlePiece[] => {
    const shuffled = [...pieces]
    const moves = 1000 // 进行1000次有效移动
    let currentEmpty = 15
    
    for (let i = 0; i < moves; i++) {
      const possibleMoves = getValidMoves(currentEmpty)
      const randomMove = possibleMoves[Math.floor(Math.random() * possibleMoves.length)]
      
      // 交换空格和随机选择的位置
      const tempPiece = shuffled[currentEmpty]
      shuffled[currentEmpty] = shuffled[randomMove]
      shuffled[randomMove] = tempPiece
      
      // 更新位置信息
      shuffled[currentEmpty].currentPosition = currentEmpty
      shuffled[randomMove].currentPosition = randomMove
      
      currentEmpty = randomMove
    }
    
    return shuffled
  }

  // 获取可以移动的位置
  const getValidMoves = (emptyPos: number): number[] => {
    const row = Math.floor(emptyPos / PUZZLE_SIZE)
    const col = emptyPos % PUZZLE_SIZE
    const validMoves: number[] = []
    
    // 上
    if (row > 0) validMoves.push((row - 1) * PUZZLE_SIZE + col)
    // 下
    if (row < PUZZLE_SIZE - 1) validMoves.push((row + 1) * PUZZLE_SIZE + col)
    // 左
    if (col > 0) validMoves.push(row * PUZZLE_SIZE + (col - 1))
    // 右
    if (col < PUZZLE_SIZE - 1) validMoves.push(row * PUZZLE_SIZE + (col + 1))
    
    return validMoves
  }

  // 开始游戏
  const startGame = () => {
    setGameStarted(true)
  }

  // 重置拼图
  const resetPuzzle = () => {
    initializePuzzle()
  }

  // 移动拼图块
  const movePiece = (position: number) => {
    if (!gameStarted || gameEnded || isCompleted) return
    
    const validMoves = getValidMoves(emptyPosition)
    if (!validMoves.includes(position)) return
    
    // 交换空格和点击的拼图块
    const newPieces = [...pieces]
    const emptyPiece = newPieces[emptyPosition]
    const clickedPiece = newPieces[position]
    
    // 交换位置
    newPieces[emptyPosition] = clickedPiece
    newPieces[position] = emptyPiece
    
    // 更新位置信息
    newPieces[emptyPosition].currentPosition = emptyPosition
    newPieces[position].currentPosition = position
    
    setPieces(newPieces)
    setEmptyPosition(position)
    setMoves(prev => prev + 1)
    
    // 检查是否完成
    checkCompletion(newPieces)
  }

  // 检查是否完成
  const checkCompletion = (currentPieces: PuzzlePiece[]) => {
    const isComplete = currentPieces.every((piece, index) => {
      if (piece.isEmpty) return index === 15 // 空格应该在最后
      return piece.correctPosition === piece.currentPosition
    })
    
    if (isComplete) {
      setIsCompleted(true)
      setGameEnded(true)
    }
  }

  // 计算分数
  const calculateScore = useCallback(() => {
    if (isCompleted) {
      // 完成拼图
      const timeBonus = Math.max(0, (timeLeft / timeLimit) * 40) // 时间奖励40%
      const movesPenalty = Math.max(0, (moves - 50) * 0.5) // 最优50步，超出扣分
      const baseScore = 60 // 基础分60%
      return Math.min(100, Math.round(baseScore + timeBonus - movesPenalty))
    } else {
      // 未完成，根据正确位置的拼图块数量给分
      const correctPieces = pieces.filter((piece, index) => {
        if (piece.isEmpty) return index === 15
        return piece.correctPosition === piece.currentPosition
      }).length
      return Math.round((correctPieces / 16) * 40) // 最多40分
    }
  }, [isCompleted, timeLeft, timeLimit, moves, pieces])

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
      const finalScore = calculateScore()
      setScore(finalScore)
      const duration = (timeLimit - timeLeft) * 1000
      setTimeout(() => {
        onGameComplete(finalScore, duration)
      }, 2000)
    }
  }, [gameEnded, calculateScore, onGameComplete, timeLimit, timeLeft])

  // 初始化拼图
  useEffect(() => {
    initializePuzzle()
  }, [initializePuzzle])

  const progressPercentage = (timeLeft / timeLimit) * 100

  // 获取拼图块显示的数字
  const getPieceNumber = (piece: PuzzlePiece): number => {
    return piece.isEmpty ? 0 : piece.correctPosition + 1
  }

  // 获取拼图块的颜色
  const getPieceColor = (piece: PuzzlePiece, position: number): string => {
    if (piece.isEmpty) return 'bg-muted/30'
    
    const isCorrectPosition = piece.correctPosition === piece.currentPosition
    if (isCorrectPosition) return 'bg-green-100 text-green-800 border-green-300'
    
    const validMoves = getValidMoves(emptyPosition)
    if (validMoves.includes(position)) return 'bg-blue-50 hover:bg-blue-100 border-blue-300 cursor-pointer'
    
    return 'bg-white border-gray-300'
  }

  if (!gameStarted) {
    return (
      <div className="max-w-2xl mx-auto p-4 text-center">
        <h3 className="text-2xl font-bold mb-2">拼图挑战</h3>
        <p className="text-muted-foreground mb-6">
          移动拼图块，将数字按顺序排列完成挑战！
        </p>
        
        <div className="mb-6 p-4 bg-muted rounded-lg">
          <h4 className="font-medium mb-2">游戏规则：</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• 4x4数字拼图，将1-15按顺序排列</li>
            <li>• 只能点击空格附近的拼图块移动</li>
            <li>• 时间限制{timeLimit}秒</li>
            <li>• 完成越快分数越高</li>
            <li>• 目标分数75分以上解锁成功</li>
          </ul>
        </div>

        <div className="flex justify-center space-x-4">
          <Button onClick={startGame} size="lg">
            开始游戏
          </Button>
        </div>
      </div>
    )
  }

  if (gameEnded) {
    return (
      <div className="max-w-2xl mx-auto p-4 text-center">
        <div className="p-6 bg-muted rounded-lg">
          <h3 className="text-2xl font-bold mb-4">
            {isCompleted ? '拼图完成！' : '时间到！'}
          </h3>
          <div className="text-4xl font-bold text-primary mb-4">{score}分</div>
          
          <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-blue-600 font-medium">移动步数</div>
              <div className="text-lg font-bold">{moves}</div>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-green-600 font-medium">用时</div>
              <div className="text-lg font-bold">
                {Math.floor((timeLimit - timeLeft) / 60)}:{((timeLimit - timeLeft) % 60).toString().padStart(2, '0')}
              </div>
            </div>
          </div>

          <p className="text-muted-foreground">
            {score >= 75 ? '恭喜！拼图成功，即将免费解锁用户' : '拼图未达标，但别担心，我们会帮你解锁的'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="mb-6 text-center">
        <h3 className="text-2xl font-bold mb-2">拼图挑战</h3>
        
        {/* 游戏信息 */}
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm">
            <span className="font-medium">步数: {moves}</span>
          </div>
          <div className="text-sm">
            <span className="font-medium">时间: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={resetPuzzle}
            className="text-xs"
          >
            <RotateCcw className="h-3 w-3 mr-1" />
            重置
          </Button>
        </div>

        {/* 时间进度条 */}
        <Progress value={progressPercentage} className="mb-4" />
      </div>

      {/* 拼图区域 */}
      <div className="max-w-md mx-auto">
        <div className="grid grid-cols-4 gap-1 p-4 bg-muted rounded-lg">
          {Array.from({ length: 16 }, (_, index) => {
            const piece = pieces[index]
            if (!piece) return null
            
            return (
              <Card
                key={`${index}-${piece.id}`}
                className={`
                  aspect-square flex items-center justify-center text-lg font-bold
                  border-2 transition-all duration-200
                  ${getPieceColor(piece, index)}
                  ${piece.isEmpty ? '' : 'hover:scale-105'}
                `}
                onClick={() => movePiece(index)}
              >
                {piece.isEmpty ? '' : getPieceNumber(piece)}
              </Card>
            )
          })}
        </div>
      </div>

      {/* 游戏提示 */}
      <div className="mt-6 text-center text-sm text-muted-foreground">
        <p>点击空格附近的数字块来移动它们</p>
        <p>将数字1-15按顺序排列即可完成拼图</p>
      </div>
    </div>
  )
} 