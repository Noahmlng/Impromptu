'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { Heart, Sparkles, Target, Brain, TrendingUp, Users2 } from 'lucide-react'

export default function RomanticPage() {
  const { language, setThemeMode } = useAppStore()

  useEffect(() => {
    setThemeMode('romantic')
  }, [setThemeMode])

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3">
          <Heart className="h-12 w-12 text-romantic-pink-500" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-romantic-pink-500 to-romantic-pink-700 bg-clip-text text-transparent">
            {language === 'zh' ? '浪漫匹配模式' : 'Romantic Matching'}
          </h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {language === 'zh' 
            ? '通过深度心理分析和情感兼容性评估，为您找到心灵契合的完美伴侣。'
            : 'Find your soulmate through deep psychological analysis and emotional compatibility assessment.'
          }
        </p>
      </div>

      {/* Profile Analysis Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-romantic-pink-50 to-romantic-pink-100 dark:from-romantic-pink-900/20 dark:to-romantic-pink-800/20 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <Brain className="h-6 w-6 text-romantic-pink-600" />
            <h2 className="text-xl font-semibold">
              {language === 'zh' ? '个性分析' : 'Personality Analysis'}
            </h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>{language === 'zh' ? '外向性' : 'Extraversion'}</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-romantic-pink-500 h-2 rounded-full" style={{width: '75%'}}></div>
                </div>
                <span className="text-sm">75%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>{language === 'zh' ? '随和性' : 'Agreeableness'}</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-romantic-pink-500 h-2 rounded-full" style={{width: '85%'}}></div>
                </div>
                <span className="text-sm">85%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>{language === 'zh' ? '开放性' : 'Openness'}</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-romantic-pink-500 h-2 rounded-full" style={{width: '90%'}}></div>
                </div>
                <span className="text-sm">90%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-romantic-pink-50 to-romantic-pink-100 dark:from-romantic-pink-900/20 dark:to-romantic-pink-800/20 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <Target className="h-6 w-6 text-romantic-pink-600" />
            <h2 className="text-xl font-semibold">
              {language === 'zh' ? '匹配偏好' : 'Matching Preferences'}
            </h2>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span>{language === 'zh' ? '年龄范围' : 'Age Range'}</span>
              <span className="text-romantic-pink-600 font-medium">25-35</span>
            </div>
            <div className="flex items-center justify-between">
              <span>{language === 'zh' ? '兴趣匹配度' : 'Interest Match'}</span>
              <span className="text-romantic-pink-600 font-medium">85%+</span>
            </div>
            <div className="flex items-center justify-between">
              <span>{language === 'zh' ? '价值观匹配' : 'Values Match'}</span>
              <span className="text-romantic-pink-600 font-medium">90%+</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Matches */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold flex items-center space-x-2">
            <Sparkles className="h-6 w-6 text-romantic-pink-500" />
            <span>{language === 'zh' ? '最新匹配' : 'Recent Matches'}</span>
          </h2>
          <Button variant="outline" className="border-romantic-pink-200 text-romantic-pink-600 hover:bg-romantic-pink-50">
            {language === 'zh' ? '查看全部' : 'View All'}
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-romantic-pink-200 rounded-lg p-4 space-y-3 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-romantic-pink-100 rounded-full flex items-center justify-center">
                  <Users2 className="h-6 w-6 text-romantic-pink-600" />
                </div>
                <div>
                  <h3 className="font-medium">Match #{i}</h3>
                  <p className="text-sm text-muted-foreground">
                    {language === 'zh' ? '匹配度' : 'Compatibility'}: 92%
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="text-green-600">
                  {language === 'zh' ? '高度匹配' : 'High Match'}
                </span>
              </div>
              <Button size="sm" className="w-full bg-romantic-pink-500 hover:bg-romantic-pink-600">
                {language === 'zh' ? '开始对话' : 'Start Chat'}
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-center">
        <Button size="lg" className="bg-romantic-pink-500 hover:bg-romantic-pink-600">
          <Heart className="h-5 w-5 mr-2" />
          {language === 'zh' ? '开始新的匹配' : 'Start New Match'}
        </Button>
        <Button size="lg" variant="outline" className="border-romantic-pink-200 text-romantic-pink-600 hover:bg-romantic-pink-50">
          <Brain className="h-5 w-5 mr-2" />
          {language === 'zh' ? '完善个人资料' : 'Complete Profile'}
        </Button>
      </div>
    </div>
  )
} 