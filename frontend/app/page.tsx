'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { Heart, Users, Search, Plus, ArrowRight, Clock, CheckCircle } from 'lucide-react'

export default function HomePage() {
  const { themeMode, language, user, setUser } = useAppStore()
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    if (!user) {
      setUser({
        id: '1',
        name: 'Alex Chen',
        credits: 1250,
        subscription: 'pro'
      })
    }
  }, [user, setUser])

  return (
    <div className="max-w-6xl mx-auto space-y-8">
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
            ? '通过先进的AI算法，为您找到最合适的伙伴。'
            : 'Find your perfect match with advanced AI algorithms.'
          }
        </p>
      </div>

      <div className="flex gap-4 items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder={language === 'zh' ? '搜索匹配任务...' : 'Search tasks...'}
            className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background"
          />
        </div>
        
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          {language === 'zh' ? '新建匹配' : 'New Match'}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="border rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <Heart className="h-5 w-5 text-romantic-pink-500" />
            <h3 className="font-semibold">
              {language === 'zh' ? '寻找完美恋人' : 'Find Perfect Partner'}
            </h3>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm">{language === 'zh' ? '已完成' : 'Completed'}</span>
          </div>
          <Button variant="ghost" className="w-full">
            {language === 'zh' ? '查看详情' : 'View Details'}
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  )
} 