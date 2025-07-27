'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Progress } from './ui/progress'

interface MemoryGameProps {
  onGameComplete: (score: number, duration: number) => void
  timeLimit: number // 秒
}

interface GameCard {
  id: number
  symbol: string
  isFlipped: boolean
  isMatched: boolean
}

const CARD_SYMBOLS = ['🎵', '🎨', '🎮', '📚', '✈️', '🏃', '🍳', '📷', '🎭', '🧘']

export default function MemoryGame({ onGameComplete, timeLimit }: MemoryGameProps) {
  const [cards, setCards] = useState<GameCard[]>([])
  const [flippedCards, setFlippedCards] = useState<number[]>([])
  const [matchedPairs, setMatchedPairs] = useState(0)
  const [moves, setMoves] = useState(0)
  const [timeLeft, setTimeLeft] = useState(timeLimit)
  const [gameStarted, setGameStarted] = useState(false)
  const [gameEnded, setGameEnded] = useState(false)
  const [score, setScore] = useState(0)

  // 初始化游戏
  const initializeGame = useCallback(() => {
    const symbols = CARD_SYMBOLS.slice(0, 8) // 8对卡片
    const gameCards: GameCard[] = []
    
    // 创建卡片对
    symbols.forEach((symbol, index) => {
      gameCards.push(
        { id: index * 2, symbol, isFlipped: false, isMatched: false },
        { id: index * 2 + 1, symbol, isFlipped: false, isMatched: false }
      )
    })
    
    // 打乱卡片顺序
    const shuffledCards = gameCards.sort(() => Math.random() - 0.5)
    setCards(shuffledCards)
    setFlippedCards([])
    setMatchedPairs(0)
    setMoves(0)
    setTimeLeft(timeLimit)
    setGameStarted(false)
    setGameEnded(false)
    setScore(0)
  }, [timeLimit])

  // 开始游戏
  const startGame = () => {
    setGameStarted(true)
  }

  // 翻牌逻辑
  const flipCard = (cardId: number) => {
    if (!gameStarted || gameEnded || flippedCards.length >= 2) return
    
    const card = cards.find(c => c.id === cardId)
    if (!card || card.isFlipped || card.isMatched) return

    const newFlippedCards = [...flippedCards, cardId]
    setFlippedCards(newFlippedCards)
    
    // 更新卡片状态
    setCards(prev => prev.map(c => 
      c.id === cardId ? { ...c, isFlipped: true } : c
    ))

    // 检查匹配
    if (newFlippedCards.length === 2) {
      setMoves(prev => prev + 1)
      const [firstId, secondId] = newFlippedCards
      const firstCard = cards.find(c => c.id === firstId)
      const secondCard = cards.find(c => c.id === secondId)

      if (firstCard && secondCard && firstCard.symbol === secondCard.symbol) {
        // 匹配成功
        setTimeout(() => {
          setCards(prev => prev.map(c => 
            c.id === firstId || c.id === secondId 
              ? { ...c, isMatched: true }
              : c
          ))
          setMatchedPairs(prev => prev + 1)
          setFlippedCards([])
        }, 1000)
      } else {
        // 匹配失败，翻回去
        setTimeout(() => {
          setCards(prev => prev.map(c => 
            c.id === firstId || c.id === secondId 
              ? { ...c, isFlipped: false }
              : c
          ))
          setFlippedCards([])
        }, 1500)
      }
    }
  }

  // 计算分数
  const calculateScore = useCallback(() => {
    if (matchedPairs === 8) {
      // 全部匹配完成
      const timeBonus = Math.max(0, timeLeft * 2)
      const movesPenalty = Math.max(0, (moves - 16) * 2) // 最佳16步
      const finalScore = Math.min(100, Math.max(0, 60 + timeBonus - movesPenalty))
      return Math.round(finalScore)
    } else if (timeLeft === 0) {
      // 时间到
      const partialScore = (matchedPairs / 8) * 50
      return Math.round(partialScore)
    }
    return 0
  }, [matchedPairs, timeLeft, moves])

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

  // 检查游戏结束
  useEffect(() => {
    if (matchedPairs === 8 && !gameEnded) {
      setGameEnded(true)
    }
  }, [matchedPairs, gameEnded])

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

  // 初始化游戏
  useEffect(() => {
    initializeGame()
  }, [initializeGame])

  const progressPercentage = (timeLeft / timeLimit) * 100

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="mb-6 text-center">
        <h3 className="text-2xl font-bold mb-2">记忆配对游戏</h3>
        <p className="text-muted-foreground mb-4">找到所有相同的卡片对</p>
        
        {/* 游戏信息 */}
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm">
            <span className="font-medium">配对: {matchedPairs}/8</span>
          </div>
          <div className="text-sm">
            <span className="font-medium">步数: {moves}</span>
          </div>
          <div className="text-sm">
            <span className="font-medium">时间: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</span>
          </div>
        </div>

        {/* 时间进度条 */}
        <Progress value={progressPercentage} className="mb-4" />

        {/* 游戏状态 */}
        {!gameStarted && !gameEnded && (
          <Button onClick={startGame} size="lg">
            开始游戏
          </Button>
        )}

        {gameEnded && (
          <div className="text-center p-4 bg-muted rounded-lg">
            <h4 className="text-lg font-bold mb-2">
              {matchedPairs === 8 ? '恭喜完成！' : '时间到！'}
            </h4>
            <p className="text-2xl font-bold text-primary">得分: {score}</p>
            <p className="text-sm text-muted-foreground mt-2">
              配对: {matchedPairs}/8 | 步数: {moves} | 用时: {Math.floor((timeLimit - timeLeft) / 60)}:{((timeLimit - timeLeft) % 60).toString().padStart(2, '0')}
            </p>
          </div>
        )}
      </div>

      {/* 游戏区域 */}
      <div className="grid grid-cols-4 gap-3 max-w-md mx-auto">
        {cards.map((card) => (
          <Card
            key={card.id}
            className={`
              aspect-square flex items-center justify-center text-2xl cursor-pointer
              transition-all duration-300 hover:scale-105
              ${card.isFlipped || card.isMatched ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'}
              ${card.isMatched ? 'opacity-60' : ''}
              ${!gameStarted || gameEnded ? 'pointer-events-none' : ''}
            `}
            onClick={() => flipCard(card.id)}
          >
            {card.isFlipped || card.isMatched ? card.symbol : '?'}
          </Card>
        ))}
      </div>

      {/* 游戏说明 */}
      {!gameStarted && (
        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>点击卡片找到相同的配对</p>
          <p>越快完成，分数越高！</p>
        </div>
      )}
    </div>
  )
} 