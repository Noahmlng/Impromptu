'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import MatchSearch from '@/components/match-search'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/hooks/useAuth'
import { tags, profile } from '@/lib/api'
import { UserTag } from '@/lib/types'
import { 
  Heart, 
  Users, 
  ArrowRight, 
  CheckCircle,
  Tag,
  Settings,
  Sparkles,
  TrendingUp,
  Search
} from 'lucide-react'

export default function HomePage() {
  const { user: authUser } = useRequireAuth()
  const { themeMode, language, userTags, setUserTags } = useAppStore()
  
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [recentTags, setRecentTags] = useState<UserTag[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // 移除冗余的user状态设置，直接使用authUser（来自store的backendUser）
  
  useEffect(() => {
    const loadUserTags = async () => {
      if (!authUser) return
      
      try {
        const response = await tags.getUserTags()
        if (response.success && response.data) {
          setUserTags(response.data)
          setRecentTags(response.data.slice(0, 8))
        }
      } catch (error) {
        console.error('Failed to load user tags:', error)
      }
    }

    loadUserTags()
  }, [authUser, setUserTags])



  const stats = [
    {
      label: language === 'zh' ? '总匹配数' : 'Total Matches',
      value: '47',
      change: '+12%',
      icon: TrendingUp,
      color: 'text-green-600'
    },
    {
      label: language === 'zh' ? '活跃标签' : 'Active Tags',
      value: userTags?.length.toString() || '0',
      change: '+3',
      icon: Tag,
      color: 'text-blue-600'
    },
    {
      label: language === 'zh' ? '本月连接' : 'Monthly Connections',
      value: '23',
      change: '+18%',
      icon: Users,
      color: 'text-purple-600'
    }
  ]

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Stats Cards
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-card rounded-lg p-6 border shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                <p className="text-3xl font-bold">{stat.value}</p>
                <p className={`text-sm ${stat.color} flex items-center space-x-1 mt-1`}>
                  <stat.icon className="h-3 w-3" />
                  <span>{stat.change}</span>
                </p>
              </div>
              <div className={`p-3 rounded-full bg-primary/10`}>
                <stat.icon className="h-6 w-6 text-primary" />
              </div>
            </div>
          </div>
        ))}
      </div> */}

      {/* Getting Started - Always Show */}
      <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-lg p-8 border border-primary/20">
        <div className="text-center space-y-4">
          <Sparkles className="h-12 w-12 text-primary mx-auto" />
          <h3 className="text-xl font-semibold">
            {userTags && userTags.length > 0 
              ? (language === 'zh' ? '继续完善您的资料' : 'Continue Improving Your Profile')
              : (language === 'zh' ? '开始您的匹配旅程' : 'Start Your Matching Journey')
            }
          </h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            {userTags && userTags.length > 0 
              ? (language === 'zh' 
                  ? '更新您的个人资料和偏好设置，获得更精准的匹配结果。'
                  : 'Update your profile and preferences to get more accurate matching results.')
              : (language === 'zh' 
                  ? '完善您的个人资料并生成标签，让我们为您找到最合适的伙伴。'
                  : 'Complete your profile and generate tags to help us find the perfect match for you.')
            }
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <Button onClick={() => window.location.href = '/profile'}>
              <Settings className="h-4 w-4 mr-2" />
              {language === 'zh' ? '完善资料' : 'Complete Profile'}
            </Button>
            <Button variant="outline" onClick={() => window.location.href = '/onboarding'}>
              <ArrowRight className="h-4 w-4 mr-2" />
              {language === 'zh' ? '引导教程' : 'Onboarding Guide'}
            </Button>
          </div>
        </div>
      </div>

      {/* Talk to Linker */}
      <div className={`bg-gradient-to-r ${
        themeMode === 'romantic' 
          ? 'from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 border-pink-200 dark:border-pink-800' 
          : 'from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-blue-200 dark:border-blue-800'
      } rounded-lg p-6 border`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-3">
              <div className={`p-2 rounded-lg ${
                themeMode === 'romantic' ? 'bg-pink-500/10' : 'bg-blue-500/10'
              }`}>
                <svg className={`h-6 w-6 ${
                  themeMode === 'romantic' ? 'text-pink-600' : 'text-blue-600'
                }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                              <h3 className={`text-lg font-semibold ${
                themeMode === 'romantic' 
                  ? 'text-pink-900 dark:text-pink-100' 
                  : 'text-blue-900 dark:text-blue-100'
              }`}>
                Talk to Linker
              </h3>
              <p className={`text-sm ${
                themeMode === 'romantic' 
                  ? 'text-pink-700 dark:text-pink-300' 
                  : 'text-blue-700 dark:text-blue-300'
              }`}>
                {themeMode === 'romantic' 
                  ? (language === 'zh' ? '通过智能对话深度了解你的人格特征' : 'Understand your personality through intelligent conversation')
                  : (language === 'zh' ? '通过智能对话深度了解你的专业技能' : 'Understand your professional skills through intelligent conversation')
                }
              </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mb-4">
              <span className={`px-3 py-1 rounded-full text-xs ${
                themeMode === 'romantic' 
                  ? 'bg-pink-100 dark:bg-pink-800 text-pink-800 dark:text-pink-200' 
                  : 'bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
              }`}>
                {language === 'zh' ? '语音对话' : 'Voice Chat'}
              </span>
              <span className={`px-3 py-1 rounded-full text-xs ${
                themeMode === 'romantic' 
                  ? 'bg-pink-100 dark:bg-pink-800 text-pink-800 dark:text-pink-200' 
                  : 'bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
              }`}>
                {themeMode === 'romantic' 
                  ? (language === 'zh' ? '人格分析' : 'Personality Analysis')
                  : (language === 'zh' ? '技能分析' : 'Skills Analysis')
                }
              </span>
              <span className={`px-3 py-1 rounded-full text-xs ${
                themeMode === 'romantic' 
                  ? 'bg-pink-100 dark:bg-pink-800 text-pink-800 dark:text-pink-200' 
                  : 'bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
              }`}>
                {language === 'zh' ? '匹配优化' : 'Match Optimization'}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              {themeMode === 'romantic' 
                ? (language === 'zh' 
                    ? '10-15分钟的智能对话，生成详细的人格分析报告，为你提供更精准的恋爱匹配建议。支持语音和文字交流。'
                    : '10-15 minute intelligent conversation to generate detailed personality analysis reports and provide more accurate romantic matching suggestions. Supports voice and text communication.')
                : (language === 'zh' 
                    ? '10-15分钟的智能对话，生成详细的技能分析报告，为你提供更精准的团队匹配建议。支持语音和文字交流。'
                    : '10-15 minute intelligent conversation to generate detailed skills analysis reports and provide more accurate team matching suggestions. Supports voice and text communication.')
              }
            </p>
          </div>
          <div className="ml-4">
            <Button 
              onClick={() => window.location.href = '/chat'}
              className={`bg-gradient-to-r ${
                themeMode === 'romantic' 
                  ? 'from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700' 
                  : 'from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700'
              }`}
            >
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              {language === 'zh' ? '开始分析' : 'Start Analysis'}
            </Button>
          </div>
        </div>
      </div>


      {/* Recent Tags */}
      {recentTags.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">
              {language === 'zh' ? '您的标签' : 'Your Tags'}
            </h2>
            <Button variant="outline" size="sm" onClick={() => window.location.href = '/profile'}>
              {language === 'zh' ? '管理标签' : 'Manage Tags'}
            </Button>
          </div>
          <div className="bg-card rounded-lg p-6 border">
            <div className="flex flex-wrap gap-2">
              {recentTags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-2 bg-primary/10 text-primary rounded-full text-sm flex items-center space-x-2"
                >
                  <span>{tag.tag_name}</span>
                  <span className="text-xs opacity-70 bg-primary/20 px-1 rounded">
                    {Math.round(tag.confidence_score * 100)}%
                  </span>
                </span>
              ))}
            </div>
            {userTags && userTags.length > 8 && (
              <p className="text-sm text-muted-foreground mt-3">
                {language === 'zh' 
                  ? `还有 ${userTags.length - 8} 个标签...` 
                  : `${userTags.length - 8} more tags...`
                }
              </p>
            )}
          </div>
        </div>
      )}

      {/* Start Matching Button */}
      <div className="text-center">
        <div className="mb-4">
          <Button
            onClick={() => setIsSearchOpen(true)}
            size="lg"
            className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <Search className="h-5 w-5 mr-2" />
            {language === 'zh' ? '开始匹配' : 'Start Matching'}
            <ArrowRight className="h-5 w-5 ml-2" />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          {language === 'zh' ? '描述您的需求，找到最合适的伙伴' : 'Describe your needs and find the perfect match'}
        </p>
        <p className="text-xs text-muted-foreground/70 mt-1">
          {language === 'zh' ? '点击按钮即可体验智能匹配功能' : 'Click to experience intelligent matching'}
        </p>
      </div>
      
      {/* Match Search Modal */}
      <MatchSearch 
        isOpen={isSearchOpen} 
        onClose={() => setIsSearchOpen(false)} 
      />
    </div>
  )
} 