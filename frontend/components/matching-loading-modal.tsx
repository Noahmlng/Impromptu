'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { useAppStore } from '@/lib/store'
import { 
  Loader2,
  X,
  Users,
  Heart,
  CheckCircle
} from 'lucide-react'

interface MatchingLoadingModalProps {
  isOpen: boolean
  onClose: () => void
  matchType: '找队友' | '找对象'
  onComplete?: () => void
}

export default function MatchingLoadingModal({ 
  isOpen, 
  onClose, 
  matchType,
  onComplete 
}: MatchingLoadingModalProps) {
  const { language } = useAppStore()
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    {
      title: language === 'zh' ? '分析用户需求' : 'Analyzing User Requirements',
      description: language === 'zh' ? '正在分析您的搜索描述和标签...' : 'Analyzing your search description and tags...'
    },
    {
      title: language === 'zh' ? '搜索匹配用户' : 'Searching Matching Users',
      description: language === 'zh' ? '在数据库中搜索符合条件的用户...' : 'Searching for qualified users in database...'
    },
    {
      title: language === 'zh' ? '计算兼容性分数' : 'Calculating Compatibility Scores',
      description: language === 'zh' ? '使用AI算法计算用户间的兼容性...' : 'Using AI algorithms to calculate compatibility...'
    },
    {
      title: language === 'zh' ? '生成匹配结果' : 'Generating Match Results',
      description: language === 'zh' ? '整理并排序最终的匹配结果...' : 'Organizing and ranking final match results...'
    }
  ]

  useEffect(() => {
    if (!isOpen) {
      setProgress(0)
      setCurrentStep(0)
      return
    }

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          // 添加完成时的延迟，让用户看到100%的状态
          setTimeout(() => {
            onComplete?.()
          }, 1000)
          return 100
        }
        return prev + 2
      })
    }, 100)

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= steps.length - 1) {
          clearInterval(stepInterval)
          return steps.length - 1
        }
        return prev + 1
      })
    }, 2000)

    return () => {
      clearInterval(interval)
      clearInterval(stepInterval)
    }
  }, [isOpen, onComplete, steps.length])

  // Reset progress when modal opens
  useEffect(() => {
    if (isOpen) {
      setProgress(0)
      setCurrentStep(0)
    }
  }, [isOpen])

  // Handle ESC key to close modal
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEsc)
      return () => document.removeEventListener('keydown', handleEsc)
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const imageSrc = matchType === '找队友' ? '/kapi.png' : '/kapi2.png'
  const imageSize = matchType === '找队友' ? 'w-64 h-64' : 'w-20 h-20'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg shadow-xl border w-full max-w-4xl max-h-[90vh] overflow-hidden mt-[33px]" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            {progress >= 100 ? (
              <CheckCircle className={`h-6 w-6 ${
                matchType === '找队友' ? 'text-green-600' : 'text-green-600'
              }`} />
            ) : (
              <Loader2 className={`h-6 w-6 animate-spin ${
                matchType === '找队友' ? 'text-blue-600' : 'text-pink-600'
              }`} />
            )}
            <h2 className="text-xl font-semibold">
              {progress >= 100 
                ? (language === 'zh' ? '匹配完成' : 'Matching Complete')
                : (language === 'zh' ? '正在匹配中...' : 'Matching in Progress...')
              }
            </h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-6 max-h-[calc(90vh-220px)] flex flex-col">
          {/* Match Type Icon and Progress Bar - Centered at top */}
          <div className="flex flex-col items-center justify-center mb-6 pt-6">
            <div className="relative mb-4 -mt-[30px]">
              <img 
                src={imageSrc} 
                alt={matchType === '找队友' ? 'Team Matching' : 'Partner Matching'}
                className={`${matchType === '找队友' ? 'w-64 h-64' : 'w-72 h-72'} object-contain transition-all duration-500 -my-5 ${
                  progress >= 100 ? 'scale-110' : ''
                }`}
                onError={(e) => {
                  // 如果图片加载失败，隐藏图片元素
                  e.currentTarget.style.display = 'none'
                }}
              />
            </div>

            {/* Progress Bar */}
            <div className="space-y-3 w-full max-w-lg -mt-[30px]">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">
                  {language === 'zh' ? '匹配进度' : 'Matching Progress'}
                </span>
                <span className={`font-medium ${progress >= 90 ? 'text-green-600' : ''}`}>
                  {progress}%
                </span>
              </div>
              <Progress 
                value={progress} 
                className={`h-3 ${
                  matchType === '找队友' ? '[&>div]:bg-blue-600' : '[&>div]:bg-pink-600'
                }`} 
              />
              <div className="text-xs text-muted-foreground text-center">
                {progress >= 100 
                  ? (language === 'zh' ? '匹配完成！正在显示结果...' : 'Matching complete! Showing results...')
                  : progress >= 90 
                  ? (language === 'zh' ? '即将完成匹配...' : 'Matching almost complete...')
                  : (language === 'zh' ? '请稍候，正在为您寻找最佳匹配...' : 'Please wait, finding the best matches for you...')
                }
              </div>
            </div>
          </div>

          {/* Current Step and All Steps */}
          <div className="mt-6 space-y-4 flex-1">
            {/* Current Step */}
            <div className={`space-y-2 p-3 rounded-lg border transition-all duration-300 ${
              progress >= 100 
                ? 'bg-green-50 border-green-200' 
                : matchType === '找队友'
                ? 'bg-blue-50 border-blue-200'
                : 'bg-pink-50 border-pink-200'
            }`}>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  progress >= 100 ? 'bg-green-500' : 
                  matchType === '找队友' ? 'bg-blue-600 animate-pulse' : 'bg-pink-600 animate-pulse'
                }`}></div>
                <span className="font-semibold text-sm">
                  {steps[currentStep]?.title}
                </span>
              </div>
              <p className="text-xs text-muted-foreground pl-4">
                {progress >= 100 
                  ? (language === 'zh' ? '所有步骤已完成，匹配结果已生成' : 'All steps completed, match results generated')
                  : steps[currentStep]?.description
                }
              </p>
              {progress < 100 ? (
                <div className="pl-4">
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>
                      {language === 'zh' ? '正在处理...' : 'Processing...'}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="pl-4">
                  <div className="flex items-center space-x-2 text-xs text-green-600">
                    <CheckCircle className="h-3 w-3" />
                    <span>
                      {language === 'zh' ? '处理完成' : 'Processing complete'}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* All Steps */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {steps.map((step, index) => (
                <div 
                  key={index} 
                  className={`flex items-center space-x-3 text-sm transition-all duration-300 p-3 rounded-lg border hover:shadow-md ${
                    index <= currentStep ? 
                      (matchType === '找队友' ? 'text-foreground bg-blue-50 border-blue-200 shadow-sm' : 'text-foreground bg-pink-50 border-pink-200 shadow-sm')
                      : 'text-muted-foreground bg-muted/30 border-muted'
                  }`}
                >
                                  <div className={`w-3 h-3 rounded-full transition-colors duration-300 ${
                  progress >= 100 ? 'bg-green-500' :
                  index < currentStep ? 'bg-green-500' : 
                  index === currentStep ? 
                    (matchType === '找队友' ? 'bg-blue-600 animate-pulse' : 'bg-pink-600 animate-pulse') 
                    : 'bg-muted'
                }`}></div>
                  <span className={`transition-all duration-300 ${index <= currentStep ? 'font-semibold' : 'font-medium'}`}>
                    {step.title}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t p-4">
          <div className="flex justify-end space-x-3">
            <Button 
              variant="outline" 
              onClick={onClose}
              className={progress >= 100 
                ? (matchType === '找队友' ? "hover:bg-blue-600 hover:text-white" : "hover:bg-pink-600 hover:text-white")
                : "hover:bg-destructive hover:text-destructive-foreground"
              }
            >
              {progress >= 100 
                ? (language === 'zh' ? '查看结果' : 'View Results')
                : (language === 'zh' ? '取消匹配' : 'Cancel Matching')
              }
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
} 