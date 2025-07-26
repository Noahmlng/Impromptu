'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PersonalityAnalysisChat } from '@/components/personality-analysis-chat'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/hooks/useAuth'
import { ArrowLeft, Brain, Sparkles, Target, MessageCircle, Zap } from 'lucide-react'

export default function ChatPage() {
  // Auth check
  const { user: authUser, isLoading: authLoading } = useRequireAuth()
  
  const { 
    themeMode, 
    language,
    setError,
    error
  } = useAppStore()
  
  const [analysisStage, setAnalysisStage] = useState<'intro' | 'analysis' | 'complete'>('intro')
  const [showWelcome, setShowWelcome] = useState(true)
  const [isStoreReady, setIsStoreReady] = useState(false)

  // Wait for store to be hydrated from localStorage
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsStoreReady(true)
      console.log('Chat page - Current themeMode:', themeMode) // Debug log
    }, 100) // Short delay to allow store hydration
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (!isStoreReady) return
    // Auto-hide welcome screen after 3 seconds
    const timer = setTimeout(() => {
      setShowWelcome(false)
    }, 3000)
    return () => clearTimeout(timer)
  }, [isStoreReady])

  if (authLoading || !isStoreReady) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">
            {language === 'zh' ? '正在连接...' : 'Connecting...'}
          </p>
        </div>
      </div>
    )
  }

  // Show welcome animation briefly
  if (showWelcome) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/50">
        <div className="text-center space-y-6 animate-fade-in-up">
          <div className={`inline-flex p-6 rounded-full ${
            themeMode === 'romantic' 
              ? 'bg-gradient-to-r from-pink-500/20 to-purple-500/20' 
              : 'bg-gradient-to-r from-blue-500/20 to-cyan-500/20'
          } backdrop-blur-sm`}>
            <Brain className={`h-16 w-16 ${
              themeMode === 'romantic' ? 'text-pink-500' : 'text-blue-500'
            } animate-pulse`} />
          </div>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
              {language === 'zh' ? '欢迎来到 Linker' : 'Welcome to Linker'}
            </h1>
            <p className="text-lg text-muted-foreground">
              {language === 'zh' ? '准备开始你的个性化分析之旅' : 'Ready to start your personalized analysis journey'}
            </p>
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      <div className="container mx-auto max-w-6xl px-4 py-6">
        {/* Modern Header */}
        <div className="flex items-center justify-between mb-8">
          <Button
            variant="ghost"
            onClick={() => window.history.back()}
            className="flex items-center space-x-2 hover:bg-muted/50 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>{language === 'zh' ? '返回' : 'Back'}</span>
          </Button>
          
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${
              themeMode === 'romantic' 
                ? 'bg-gradient-to-r from-pink-500/10 to-purple-500/10' 
                : 'bg-gradient-to-r from-blue-500/10 to-cyan-500/10'
            }`}>
              <Brain className={`h-6 w-6 ${
                themeMode === 'romantic' ? 'text-pink-500' : 'text-blue-500'
              }`} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Talk to Linker</h1>
              <p className="text-sm text-muted-foreground">
                {analysisStage === 'complete' 
                  ? (language === 'zh' ? '分析完成' : 'Analysis Complete')
                  : analysisStage === 'analysis' 
                    ? (language === 'zh' ? '分析进行中' : 'Analysis in Progress')
                    : (language === 'zh' ? '准备开始' : 'Ready to Start')
                }
              </p>
            </div>
          </div>
        </div>

        {/* Feature Pills */}
        {analysisStage === 'intro' && (
          <div className="flex flex-wrap gap-3 mb-6 justify-center">
            {[
              { icon: Sparkles, text: language === 'zh' ? '智能对话' : 'Smart Chat' },
              { icon: Target, text: language === 'zh' ? '精准分析' : 'Precision Analysis' },
              { icon: MessageCircle, text: language === 'zh' ? '语音支持' : 'Voice Support' },
              { icon: Zap, text: language === 'zh' ? '个性化建议' : 'Personalized Tips' }
            ].map((feature, index) => (
              <div 
                key={index}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full border ${
                  themeMode === 'romantic' 
                    ? 'bg-gradient-to-r from-pink-50 to-purple-50 border-pink-200 dark:from-pink-900/20 dark:to-purple-900/20 dark:border-pink-800' 
                    : 'bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200 dark:from-blue-900/20 dark:to-cyan-900/20 dark:border-blue-800'
                } backdrop-blur-sm`}
              >
                <feature.icon className={`h-4 w-4 ${
                  themeMode === 'romantic' ? 'text-pink-600' : 'text-blue-600'
                }`} />
                <span className="text-sm font-medium">{feature.text}</span>
              </div>
            ))}
          </div>
        )}

        {/* Main Chat Interface */}
        <Card className="shadow-2xl border-0 bg-card/50 backdrop-blur-sm overflow-hidden">
          <CardContent className="p-0">
            <div className="h-[700px] flex flex-col">
              <PersonalityAnalysisChat 
                onStageChange={setAnalysisStage}
                currentStage={analysisStage}
              />
            </div>
          </CardContent>
        </Card>

        {/* Bottom Status Bar */}
        <div className="mt-6 flex items-center justify-center">
          <div className={`flex items-center space-x-4 px-6 py-3 rounded-full ${
            themeMode === 'romantic' 
              ? 'bg-gradient-to-r from-pink-500/10 to-purple-500/10 border border-pink-200/50' 
              : 'bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-200/50'
          } backdrop-blur-sm`}>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-muted-foreground">
                {language === 'zh' ? 'AI 已连接' : 'AI Connected'}
              </span>
            </div>
            <div className="w-px h-4 bg-border" />
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {language === 'zh' ? '深度学习模型' : 'Deep Learning Model'}
              </span>
            </div>
            <div className="w-px h-4 bg-border" />
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">
                {language === 'zh' ? '端到端加密' : 'End-to-End Encrypted'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 