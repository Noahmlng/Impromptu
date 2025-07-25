'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { Users, Zap, Target, Brain, TrendingUp, Briefcase, Code, Palette } from 'lucide-react'

export default function TeamPage() {
  const { language, setThemeMode } = useAppStore()

  useEffect(() => {
    setThemeMode('team')
  }, [setThemeMode])

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3">
          <Users className="h-12 w-12 text-miami-blue-500" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-miami-blue-500 to-miami-blue-700 bg-clip-text text-transparent">
            {language === 'zh' ? '团队匹配模式' : 'Team Matching'}
          </h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {language === 'zh' 
            ? '基于技能互补和工作风格分析，为您匹配最佳团队合作伙伴。'
            : 'Find your ideal team partners through skill complementarity and work style analysis.'
          }
        </p>
      </div>

      {/* Skills & Expertise */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-miami-blue-50 to-miami-blue-100 dark:from-miami-blue-900/20 dark:to-miami-blue-800/20 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <Brain className="h-6 w-6 text-miami-blue-600" />
            <h2 className="text-xl font-semibold">
              {language === 'zh' ? '技能分析' : 'Skills Analysis'}
            </h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>{language === 'zh' ? '技术开发' : 'Development'}</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-miami-blue-500 h-2 rounded-full" style={{width: '90%'}}></div>
                </div>
                <span className="text-sm">90%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>{language === 'zh' ? '项目管理' : 'Project Management'}</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-miami-blue-500 h-2 rounded-full" style={{width: '75%'}}></div>
                </div>
                <span className="text-sm">75%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>{language === 'zh' ? '设计思维' : 'Design Thinking'}</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-miami-blue-500 h-2 rounded-full" style={{width: '65%'}}></div>
                </div>
                <span className="text-sm">65%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-miami-blue-50 to-miami-blue-100 dark:from-miami-blue-900/20 dark:to-miami-blue-800/20 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <Target className="h-6 w-6 text-miami-blue-600" />
            <h2 className="text-xl font-semibold">
              {language === 'zh' ? '团队偏好' : 'Team Preferences'}
            </h2>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span>{language === 'zh' ? '团队规模' : 'Team Size'}</span>
              <span className="text-miami-blue-600 font-medium">3-5 {language === 'zh' ? '人' : 'people'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>{language === 'zh' ? '工作模式' : 'Work Mode'}</span>
              <span className="text-miami-blue-600 font-medium">{language === 'zh' ? '混合办公' : 'Hybrid'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>{language === 'zh' ? '项目类型' : 'Project Type'}</span>
              <span className="text-miami-blue-600 font-medium">{language === 'zh' ? '科技创业' : 'Tech Startup'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Team Matches */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold flex items-center space-x-2">
            <Zap className="h-6 w-6 text-miami-blue-500" />
            <span>{language === 'zh' ? '推荐团队' : 'Recommended Teams'}</span>
          </h2>
          <Button variant="outline" className="border-miami-blue-200 text-miami-blue-600 hover:bg-miami-blue-50">
            {language === 'zh' ? '查看全部' : 'View All'}
          </Button>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {[
            { name: 'TechVenture Team', members: 4, match: '95%', skills: ['Frontend', 'Backend', 'Design'] },
            { name: 'Innovation Squad', members: 3, match: '88%', skills: ['AI/ML', 'Product', 'Marketing'] }
          ].map((team, i) => (
            <div key={i} className="border border-miami-blue-200 rounded-lg p-6 space-y-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{team.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {team.members} {language === 'zh' ? '成员' : 'members'} • {language === 'zh' ? '匹配度' : 'Match'} {team.match}
                  </p>
                </div>
                <div className="flex items-center space-x-1 text-sm">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-green-600">
                    {language === 'zh' ? '高匹配' : 'High Match'}
                  </span>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-2">
                {team.skills.map((skill, j) => (
                  <span key={j} className="px-2 py-1 bg-miami-blue-100 text-miami-blue-700 rounded-full text-xs">
                    {skill}
                  </span>
                ))}
              </div>

              <div className="flex gap-2">
                <Button size="sm" className="flex-1 bg-miami-blue-500 hover:bg-miami-blue-600">
                  {language === 'zh' ? '申请加入' : 'Apply to Join'}
                </Button>
                <Button size="sm" variant="outline" className="border-miami-blue-200">
                  {language === 'zh' ? '查看详情' : 'View Details'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Project Categories */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">
          {language === 'zh' ? '项目分类' : 'Project Categories'}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { icon: Code, name: language === 'zh' ? '技术开发' : 'Development', count: 12 },
            { icon: Palette, name: language === 'zh' ? '创意设计' : 'Creative Design', count: 8 },
            { icon: Briefcase, name: language === 'zh' ? '商业策略' : 'Business Strategy', count: 15 },
            { icon: Zap, name: language === 'zh' ? '创新研究' : 'Innovation Research', count: 6 }
          ].map((category, i) => (
            <div key={i} className="text-center p-4 border border-miami-blue-200 rounded-lg hover:bg-miami-blue-50 cursor-pointer transition-colors">
              <category.icon className="h-8 w-8 text-miami-blue-500 mx-auto mb-2" />
              <h3 className="font-medium">{category.name}</h3>
              <p className="text-sm text-muted-foreground">{category.count} {language === 'zh' ? '个项目' : 'projects'}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-center">
        <Button size="lg" className="bg-miami-blue-500 hover:bg-miami-blue-600">
          <Users className="h-5 w-5 mr-2" />
          {language === 'zh' ? '创建团队' : 'Create Team'}
        </Button>
        <Button size="lg" variant="outline" className="border-miami-blue-200 text-miami-blue-600 hover:bg-miami-blue-50">
          <Brain className="h-5 w-5 mr-2" />
          {language === 'zh' ? '完善技能档案' : 'Complete Skills Profile'}
        </Button>
      </div>
    </div>
  )
} 