'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import MatchSearch from '@/components/match-search'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/lib/hooks/useAuth'
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
  TrendingUp
} from 'lucide-react'

export default function HomePage() {
  const { user: authUser } = useRequireAuth()
  const { themeMode, language, user, setUser, userTags, setUserTags } = useAppStore()
  
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [recentTags, setRecentTags] = useState<UserTag[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!user && authUser) {
      setUser({
        id: authUser.user_id,
        name: authUser.display_name || 'User',
        email: authUser.email,
        credits: 1250,
        subscription: 'pro'
      })
    }
  }, [user, authUser, setUser])

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
      {/* Welcome Section */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3">
          {themeMode === 'romantic' ? (
            <Heart className="h-12 w-12 text-romantic-pink-500" />
          ) : (
            <Users className="h-12 w-12 text-miami-blue-500" />
          )}
          <h1 className="text-4xl font-bold">
            {language === 'zh' ? '智能匹配中心' : 'AI Matching Center'}
          </h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {language === 'zh' 
            ? `欢迎回来，${user?.name || 'User'}！通过先进的AI算法，为您找到最合适的伙伴。`
            : `Welcome back, ${user?.name || 'User'}! Find your perfect match with advanced AI algorithms.`
          }
        </p>
      </div>

      {/* Stats Cards */}
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

      {/* Getting Started */}
      {(!userTags || userTags.length === 0) && (
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-lg p-8 border border-primary/20">
          <div className="text-center space-y-4">
            <Sparkles className="h-12 w-12 text-primary mx-auto" />
            <h3 className="text-xl font-semibold">
              {language === 'zh' ? '开始您的匹配旅程' : 'Start Your Matching Journey'}
            </h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              {language === 'zh' 
                ? '完善您的个人资料并生成标签，让我们为您找到最合适的伙伴。'
                : 'Complete your profile and generate tags to help us find the perfect match for you.'
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
      )}

      {/* Recent Activity */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">
          {language === 'zh' ? '最近活动' : 'Recent Activity'}
        </h2>
        <div className="bg-card rounded-lg border">
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm">
                    {language === 'zh' ? '生成了新的标签集合' : 'Generated new tag collection'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {language === 'zh' ? '2小时前' : '2 hours ago'}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <Users className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm">
                    {language === 'zh' ? '找到了3个高匹配度用户' : 'Found 3 high-compatibility users'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {language === 'zh' ? '1天前' : '1 day ago'}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                  <Settings className="h-4 w-4 text-purple-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm">
                    {language === 'zh' ? '更新了个人资料信息' : 'Updated profile information'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {language === 'zh' ? '3天前' : '3 days ago'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Match Search Modal */}
      <MatchSearch 
        isOpen={isSearchOpen} 
        onClose={() => setIsSearchOpen(false)} 
      />
    </div>
  )
} 