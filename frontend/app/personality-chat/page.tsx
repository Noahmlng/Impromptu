'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PersonalityAnalysisChat } from '@/components/personality-analysis-chat'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/hooks/useAuth'
import { Brain, MessageCircle, User, BarChart3, Target, Sparkles } from 'lucide-react'

export default function PersonalityChatPage() {
  // Auth check
  const { user: authUser, isLoading: authLoading } = useRequireAuth()
  
  const { 
    themeMode, 
    language,
    setError,
    error
  } = useAppStore()
  
  const [chatStarted, setChatStarted] = useState(false)
  const [analysisStage, setAnalysisStage] = useState<'intro' | 'analysis' | 'complete'>('intro')

  const analysisFeatures = themeMode === 'romantic' ? [
    {
      icon: Brain,
      title: language === 'zh' ? '深度人格分析' : 'Deep Personality Analysis',
      description: language === 'zh' 
        ? '通过智能对话了解你的性格特征、价值观和偏好'
        : 'Understand your personality traits, values and preferences through intelligent conversation'
    },
    {
      icon: Target,
      title: language === 'zh' ? '精准匹配建议' : 'Precise Matching Suggestions',
      description: language === 'zh' 
        ? '基于分析结果为你推荐最适合的恋爱对象'
        : 'Recommend the most suitable romantic matches based on analysis results'
    },
    {
      icon: Sparkles,
      title: language === 'zh' ? '智能对话引导' : 'Intelligent Conversation Guide',
      description: language === 'zh' 
        ? 'AI会根据你的回答调整问题，让人格分析更加准确'
        : 'AI adjusts questions based on your responses for more accurate personality analysis'
    },
    {
      icon: BarChart3,
      title: language === 'zh' ? '详细分析报告' : 'Detailed Analysis Report',
      description: language === 'zh' 
        ? '生成完整的人格分析报告，持续优化恋爱匹配效果'
        : 'Generate comprehensive personality analysis reports for continuous romantic matching optimization'
    }
  ] : [
    {
      icon: Brain,
      title: language === 'zh' ? '专业技能分析' : 'Professional Skills Analysis',
      description: language === 'zh' 
        ? '通过智能对话了解你的专业技能、工作风格和合作偏好'
        : 'Understand your professional skills, work style and collaboration preferences through intelligent conversation'
    },
    {
      icon: Target,
      title: language === 'zh' ? '团队匹配建议' : 'Team Matching Suggestions',
      description: language === 'zh' 
        ? '基于分析结果为你推荐最适合的合作伙伴'
        : 'Recommend the most suitable collaboration partners based on analysis results'
    },
    {
      icon: Sparkles,
      title: language === 'zh' ? '智能对话引导' : 'Intelligent Conversation Guide',
      description: language === 'zh' 
        ? 'AI会根据你的回答调整问题，让技能分析更加准确'
        : 'AI adjusts questions based on your responses for more accurate skills analysis'
    },
    {
      icon: BarChart3,
      title: language === 'zh' ? '详细分析报告' : 'Detailed Analysis Report',
      description: language === 'zh' 
        ? '生成完整的技能分析报告，持续优化团队匹配效果'
        : 'Generate comprehensive skills analysis reports for continuous team matching optimization'
    }
  ]

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (chatStarted) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-4 flex items-center justify-between">
          <Button
            variant="outline"
            onClick={() => setChatStarted(false)}
          >
            ← {language === 'zh' ? '返回' : 'Back'}
          </Button>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Brain className="h-4 w-4" />
            <span>
              {language === 'zh' ? 'AI人格分析进行中...' : 'AI Personality Analysis in progress...'}
            </span>
          </div>
        </div>
        
        <Card>
          <CardContent className="p-0">
            <PersonalityAnalysisChat 
              onStageChange={setAnalysisStage}
              currentStage={analysisStage}
            />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3">
                      <div className={`p-3 rounded-full ${themeMode === 'romantic' ? 'bg-pink-500/10' : 'bg-blue-500/10'}`}>
            <Brain className={`h-12 w-12 ${themeMode === 'romantic' ? 'text-pink-500' : 'text-blue-500'}`} />
          </div>
          <h1 className="text-4xl font-bold">
            Talk to Linker
          </h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {themeMode === 'romantic' 
            ? (language === 'zh' 
                ? '通过智能对话深度了解你的人格特征，为你匹配最合适的恋爱伙伴。支持语音和文字交流，让分析更加准确和自然。'
                : 'Deeply understand your personality through intelligent conversation to match you with the most suitable romantic partners. Support voice and text communication for more accurate and natural analysis.')
            : (language === 'zh' 
                ? '通过智能对话深度了解你的专业技能和合作风格，为你匹配最合适的团队伙伴。支持语音和文字交流，让分析更加准确和自然。'
                : 'Deeply understand your professional skills and collaboration style through intelligent conversation to match you with the most suitable team partners. Support voice and text communication for more accurate and natural analysis.')
          }
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {analysisFeatures.map((feature, index) => {
          const FeatureIcon = feature.icon
          return (
            <Card key={index} className="transition-all hover:shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${themeMode === 'romantic' ? 'bg-romantic-pink-500/10' : 'bg-miami-blue-500/10'}`}>
                    <FeatureIcon className={`h-6 w-6 ${themeMode === 'romantic' ? 'text-romantic-pink-500' : 'text-miami-blue-500'}`} />
                  </div>
                  <span className="text-lg">{feature.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Start Analysis Section */}
      <Card className="border-2 border-dashed">
        <CardContent className="text-center py-12 space-y-6">
          <div className={`inline-flex p-4 rounded-full ${themeMode === 'romantic' ? 'bg-romantic-pink-500/10' : 'bg-miami-blue-500/10'}`}>
            <MessageCircle className={`h-12 w-12 ${themeMode === 'romantic' ? 'text-romantic-pink-500' : 'text-miami-blue-500'}`} />
          </div>
          
          <div className="space-y-3">
            <h3 className="text-2xl font-bold">
              {themeMode === 'romantic' 
                ? (language === 'zh' ? '开始分析人格' : 'Start Your Personality Analysis Journey')
                : (language === 'zh' ? '开始分析技能' : 'Start Your Skills Analysis Journey')
              }
            </h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              {themeMode === 'romantic' 
                ? (language === 'zh' 
                    ? '大约需要10-15分钟，AI会通过自然对话深入了解你的性格特征和偏好。'
                    : 'Takes about 10-15 minutes. AI will understand your personality traits and preferences through natural conversation.')
                : (language === 'zh' 
                    ? '大约需要10-15分钟，AI会通过自然对话深入了解你的专业技能和合作风格。'
                    : 'Takes about 10-15 minutes. AI will understand your professional skills and collaboration style through natural conversation.')
              }
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={() => setChatStarted(true)}
              size="lg"
              className={`px-8 py-3 text-lg ${themeMode === 'romantic' ? 'bg-romantic-pink-500 hover:bg-romantic-pink-600' : 'bg-miami-blue-500 hover:bg-miami-blue-600'}`}
            >
              <Brain className="h-5 w-5 mr-2" />
              {language === 'zh' ? '开始分析' : 'Start Analysis'}
            </Button>
            
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>
                {language === 'zh' ? '完全保密，仅用于匹配优化' : 'Completely confidential, only for matching optimization'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Process Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>{language === 'zh' ? '分析流程' : 'Analysis Process'}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center space-y-3">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full ${themeMode === 'romantic' ? 'bg-romantic-pink-500/10 text-romantic-pink-500' : 'bg-miami-blue-500/10 text-miami-blue-500'} font-bold text-lg`}>
                1
              </div>
              <h4 className="font-semibold">
                {language === 'zh' ? '基础信息收集' : 'Basic Information Collection'}
              </h4>
              <p className="text-sm text-muted-foreground">
                {language === 'zh' 
                  ? '了解你的基本情况和期望'
                  : 'Understand your basic situation and expectations'
                }
              </p>
            </div>
            
            <div className="text-center space-y-3">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full ${themeMode === 'romantic' ? 'bg-romantic-pink-500/10 text-romantic-pink-500' : 'bg-miami-blue-500/10 text-miami-blue-500'} font-bold text-lg`}>
                2
              </div>
              <h4 className="font-semibold">
                {language === 'zh' ? '深度性格探索' : 'Deep Personality Exploration'}
              </h4>
              <p className="text-sm text-muted-foreground">
                {language === 'zh' 
                  ? '通过场景问题了解性格特征'
                  : 'Understand personality traits through scenario questions'
                }
              </p>
            </div>
            
            <div className="text-center space-y-3">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full ${themeMode === 'romantic' ? 'bg-romantic-pink-500/10 text-romantic-pink-500' : 'bg-miami-blue-500/10 text-miami-blue-500'} font-bold text-lg`}>
                3
              </div>
              <h4 className="font-semibold">
                {language === 'zh' ? '生成分析报告' : 'Generate Analysis Report'}
              </h4>
              <p className="text-sm text-muted-foreground">
                {language === 'zh' 
                  ? '创建详细的人格档案和匹配建议'
                  : 'Create detailed personality profile and matching suggestions'
                }
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 