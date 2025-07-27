'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Progress } from './ui/progress'
import { CheckCircle, XCircle } from 'lucide-react'

interface QuizGameProps {
  onGameComplete: (score: number, duration: number) => void
  timeLimit: number // 秒
  targetUserTags?: string[] // 目标用户的标签，用于生成相关问题
}

interface QuizQuestion {
  id: number
  question: string
  options: string[]
  correctAnswer: number
  category: string
}

// 预设问题库
const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: 1,
    question: "在团队合作中，最重要的是什么？",
    options: ["个人能力", "沟通协调", "领导权威", "竞争意识"],
    correctAnswer: 1,
    category: "团队合作"
  },
  {
    id: 2,
    question: "你认为理想的休闲方式是？",
    options: ["运动健身", "看书学习", "旅行探索", "宅家放松"],
    correctAnswer: -1, // 没有标准答案，根据用户标签判断
    category: "生活方式"
  },
  {
    id: 3,
    question: "在职业发展中，你最看重什么？",
    options: ["薪资待遇", "个人成长", "工作稳定", "团队氛围"],
    correctAnswer: 1,
    category: "职业发展"
  },
  {
    id: 4,
    question: "你更喜欢哪种学习方式？",
    options: ["独立研究", "小组讨论", "导师指导", "实践操作"],
    correctAnswer: -1,
    category: "学习偏好"
  },
  {
    id: 5,
    question: "面对挑战时，你的第一反应是？",
    options: ["仔细分析", "请教他人", "立即行动", "寻找资源"],
    correctAnswer: 0,
    category: "解决问题"
  },
  {
    id: 6,
    question: "你认为创新最重要的要素是？",
    options: ["大胆想象", "实际执行", "团队配合", "技术支撑"],
    correctAnswer: 1,
    category: "创新思维"
  },
  {
    id: 7,
    question: "在压力大的情况下，你会？",
    options: ["制定计划", "寻求帮助", "暂时休息", "咬牙坚持"],
    correctAnswer: 0,
    category: "压力管理"
  },
  {
    id: 8,
    question: "你更倾向于哪种工作环境？",
    options: ["安静独立", "活跃互动", "灵活自由", "结构清晰"],
    correctAnswer: -1,
    category: "工作环境"
  }
]

export default function QuizGame({ onGameComplete, timeLimit, targetUserTags = [] }: QuizGameProps) {
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [answers, setAnswers] = useState<number[]>([])
  const [correctAnswers, setCorrectAnswers] = useState(0)
  const [timeLeft, setTimeLeft] = useState(timeLimit)
  const [gameStarted, setGameStarted] = useState(false)
  const [gameEnded, setGameEnded] = useState(false)
  const [showResult, setShowResult] = useState(false)
  const [score, setScore] = useState(0)

  // 根据目标用户标签选择相关问题
  const selectRelevantQuestions = useCallback(() => {
    // 简单的问题选择逻辑，实际可以根据标签智能选择
    const selectedQuestions = QUIZ_QUESTIONS.slice(0, 6) // 选择6道题
    setQuestions(selectedQuestions)
  }, [targetUserTags])

  // 开始游戏
  const startGame = () => {
    setGameStarted(true)
    selectRelevantQuestions()
  }

  // 选择答案
  const selectAnswer = (answerIndex: number) => {
    if (selectedAnswer !== null || gameEnded) return
    setSelectedAnswer(answerIndex)
  }

  // 确认答案并进入下一题
  const confirmAnswer = () => {
    if (selectedAnswer === null) return

    const newAnswers = [...answers, selectedAnswer]
    setAnswers(newAnswers)

    const currentQ = questions[currentQuestion]
    const isCorrect = currentQ.correctAnswer === -1 || currentQ.correctAnswer === selectedAnswer
    
    if (isCorrect) {
      setCorrectAnswers(prev => prev + 1)
    }

    setShowResult(true)

    // 2秒后进入下一题或结束游戏
    setTimeout(() => {
      setShowResult(false)
      setSelectedAnswer(null)
      
      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(prev => prev + 1)
      } else {
        setGameEnded(true)
      }
    }, 2000)
  }

  // 计算分数
  const calculateScore = useCallback(() => {
    const baseScore = (correctAnswers / questions.length) * 70 // 基础分70%
    const timeBonus = Math.max(0, (timeLeft / timeLimit) * 30) // 时间奖励30%
    return Math.min(100, Math.round(baseScore + timeBonus))
  }, [correctAnswers, questions.length, timeLeft, timeLimit])

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
      }, 3000)
    }
  }, [gameEnded, calculateScore, onGameComplete, timeLimit, timeLeft])

  const progressPercentage = (timeLeft / timeLimit) * 100
  const questionProgress = ((currentQuestion + 1) / questions.length) * 100

  if (!gameStarted) {
    return (
      <div className="max-w-2xl mx-auto p-4 text-center">
        <h3 className="text-2xl font-bold mb-2">兴趣问答挑战</h3>
        <p className="text-muted-foreground mb-6">
          回答关于生活方式和价值观的问题，看看你和TA有多了解！
        </p>
        
        <div className="mb-6 p-4 bg-muted rounded-lg">
          <h4 className="font-medium mb-2">游戏规则：</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• 总共{QUIZ_QUESTIONS.slice(0, 6).length}道问题</li>
            <li>• 时间限制{timeLimit}秒</li>
            <li>• 答对得分，剩余时间有奖励</li>
            <li>• 目标分数70分以上解锁成功</li>
          </ul>
        </div>

        <Button onClick={startGame} size="lg">
          开始答题
        </Button>
      </div>
    )
  }

  if (gameEnded) {
    return (
      <div className="max-w-2xl mx-auto p-4 text-center">
        <div className="p-6 bg-muted rounded-lg">
          <h3 className="text-2xl font-bold mb-4">答题完成！</h3>
          <div className="text-4xl font-bold text-primary mb-4">{score}分</div>
          
          <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-green-600 font-medium">正确答题</div>
              <div className="text-lg font-bold">{correctAnswers}/{questions.length}</div>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-blue-600 font-medium">用时</div>
              <div className="text-lg font-bold">
                {Math.floor((timeLimit - timeLeft) / 60)}:{((timeLimit - timeLeft) % 60).toString().padStart(2, '0')}
              </div>
            </div>
          </div>

          <p className="text-muted-foreground">
            {score >= 70 ? '恭喜！答题成功，即将免费解锁用户' : '答题未达标，但别担心，我们会帮你解锁的'}
          </p>
        </div>
      </div>
    )
  }

  const currentQ = questions[currentQuestion]
  if (!currentQ) return null

  const isCorrectAnswer = currentQ.correctAnswer === -1 || currentQ.correctAnswer === selectedAnswer
  const correctOption = currentQ.correctAnswer !== -1 ? currentQ.correctAnswer : null

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="mb-6">
        {/* 顶部信息 */}
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-muted-foreground">
            问题 {currentQuestion + 1}/{questions.length}
          </div>
          <div className="text-sm font-medium">
            时间: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
          </div>
        </div>

        {/* 进度条 */}
        <div className="space-y-2">
          <Progress value={questionProgress} className="mb-2" />
          <Progress value={progressPercentage} className="h-2" />
        </div>
      </div>

      {/* 问题区域 */}
      <Card className="p-6 mb-6">
        <div className="mb-2 text-sm text-muted-foreground">{currentQ.category}</div>
        <h3 className="text-xl font-medium mb-6">{currentQ.question}</h3>

        <div className="space-y-3">
          {currentQ.options.map((option, index) => (
            <Button
              key={index}
              variant={selectedAnswer === index ? "default" : "outline"}
              className={`
                w-full text-left justify-start p-4 h-auto whitespace-normal
                ${showResult && selectedAnswer === index && isCorrectAnswer ? 'bg-green-500 text-white' : ''}
                ${showResult && selectedAnswer === index && !isCorrectAnswer ? 'bg-red-500 text-white' : ''}
                ${showResult && correctOption === index && selectedAnswer !== index ? 'bg-green-100 text-green-800' : ''}
                ${showResult ? 'pointer-events-none' : ''}
              `}
              onClick={() => selectAnswer(index)}
              disabled={selectedAnswer !== null}
            >
              <div className="flex items-center space-x-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-muted flex items-center justify-center text-sm">
                  {String.fromCharCode(65 + index)}
                </span>
                <span>{option}</span>
                {showResult && selectedAnswer === index && (
                  isCorrectAnswer ? <CheckCircle className="ml-auto h-5 w-5" /> : <XCircle className="ml-auto h-5 w-5" />
                )}
              </div>
            </Button>
          ))}
        </div>

        {selectedAnswer !== null && !showResult && (
          <div className="mt-6 text-center">
            <Button onClick={confirmAnswer}>
              确认答案
            </Button>
          </div>
        )}

        {showResult && (
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              {isCorrectAnswer ? '回答正确！' : '答案有误，但这题没有标准答案'}
            </p>
          </div>
        )}
      </Card>
    </div>
  )
} 