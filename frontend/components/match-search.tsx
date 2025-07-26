'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { matching, tags } from '@/lib/api'
import { MatchUser, UserTag } from '@/lib/types'
import MatchingLoadingModal from './matching-loading-modal'
import { 
  Search, 
  Heart, 
  Users, 
  Star, 
  MapPin, 
  Calendar,
  Loader2,
  AlertCircle,
  CheckCircle,
  X
} from 'lucide-react'
import ReactDOM from 'react-dom'

interface MatchSearchProps {
  isOpen: boolean
  onClose: () => void
}

export default function MatchSearch({ isOpen, onClose }: MatchSearchProps) {
  const { language, userTags } = useAppStore()
  
  const [searchDescription, setSearchDescription] = useState('')
  const [selectedMatchType, setSelectedMatchType] = useState<'找队友' | '找对象'>('找队友')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [searchResults, setSearchResults] = useState<MatchUser[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isMatchingLoading, setIsMatchingLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState('')

  // 监控搜索结果状态变化
  useEffect(() => {
    console.log('🔄 搜索结果状态变化:', {
      搜索结果数量: searchResults.length,
      是否正在搜索: isMatchingLoading,
      错误信息: error,
      成功信息: successMessage,
      搜索描述: searchDescription.trim(),
      选中标签: selectedTags,
      匹配类型: selectedMatchType
    })
    
    if (searchResults.length > 0) {
      console.log('📊 当前搜索结果详情:', searchResults)
    }
  }, [searchResults, isMatchingLoading, error, successMessage, searchDescription, selectedTags, selectedMatchType])

  // 生成模拟匹配用户数据
  const generateMockUsers = (description: string, matchType: string) => {
    const mockUsers = [
      {
        user_id: 'user01_alex_chen',
        display_name: '陈浩 Alex',
        email: 'alex.chen@example.com',
        avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=alex',
        match_score: 0.92,
        user_tags: ['编程', '技术', '前端开发', 'React', 'JavaScript'],
        metadata_summary: {
          profile: {
            personal: { location: '深圳', age_range: '23-27岁' },
            professional: { industry: '互联网/技术' }
          }
        }
      },
      {
        user_id: 'user02_sophia_wang',
        display_name: '王索菲亚 Sophia',
        email: 'sophia.wang@example.com',
        avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sophia',
        match_score: 0.88,
        user_tags: ['UI设计', '用户体验', '前端', '创意', '团队协作'],
        metadata_summary: {
          profile: {
            personal: { location: '北京', age_range: '25-29岁' },
            professional: { industry: '设计' }
          }
        }
      },
      {
        user_id: 'user03_kevin_li',
        display_name: '李凯文 Kevin',
        email: 'kevin.li@example.com',
        avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=kevin',
        match_score: 0.84,
        user_tags: ['产品经理', '项目管理', '团队领导', '创新', '技术理解'],
        metadata_summary: {
          profile: {
            personal: { location: '上海', age_range: '28-32岁' },
            professional: { industry: '互联网' }
          }
        }
      },
      {
        user_id: 'user04_luna_zhang',
        display_name: '张露娜 Luna',
        email: 'luna.zhang@example.com',
        avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=luna',
        match_score: 0.79,
        user_tags: ['后端开发', 'Python', 'AI', '机器学习', '数据分析'],
        metadata_summary: {
          profile: {
            personal: { location: '杭州', age_range: '26-30岁' },
            professional: { industry: '人工智能' }
          }
        }
      }
    ]

    // 根据匹配类型调整用户数据
    if (matchType === '找对象') {
      return mockUsers.map(user => ({
        ...user,
        user_tags: ['温柔体贴', '兴趣广泛', '热爱生活', '善于沟通', '价值观相近'],
        metadata_summary: {
          profile: {
            personal: { ...user.metadata_summary.profile.personal },
            professional: { industry: '各行各业' }
          }
        }
      }))
    }

    return mockUsers
  }

  const handleSearch = async () => {
    if (!searchDescription.trim()) {
      setError(language === 'zh' ? '请输入搜索描述' : 'Please enter search description')
      return
    }

    setIsMatchingLoading(true)
    setError(null)
    setSearchResults([]) // 清空之前的结果
    
    try {
      console.log('🔍 开始搜索匹配用户...', {
        description: searchDescription,
        tags: selectedTags,
        matchType: selectedMatchType
      })
      
      // 检查认证状态
      console.log('🔑 检查认证状态...')
      
      const startTime = Date.now()
      
      const response = await matching.search(
        searchDescription,
        selectedTags,
        selectedMatchType,
        20
      )
      
      const duration = Date.now() - startTime
      console.log(`✅ 搜索完成，耗时: ${duration}ms`)
      
      console.log('🔍 API响应数据:', response)
      
      if (response.success && response.data) {
        const matchedUsers = response.data.matched_users || []
        const performance = response.data.performance
        
        console.log('✅ 匹配成功，原始数据:', {
          总数: matchedUsers.length,
          匹配用户: matchedUsers,
          性能数据: performance,
          响应数据: response.data
        })
        
        // 在控制台输出性能信息
        if (performance) {
          console.log('🚀 匹配性能统计:', {
            总耗时: `${performance.total_time_seconds}秒`,
            处理用户数: response.data.processed_count,
            平均每用户耗时: `${performance.avg_time_per_user}秒`,
            处理速度: `${performance.users_per_second}用户/秒`
          })
        }
        
        // 清除之前的错误状态
        setError(null)
        
        console.log('📋 准备设置搜索结果:', matchedUsers)
        setSearchResults(matchedUsers)
        
        console.log('🎯 搜索结果已设置，当前状态:', {
          搜索结果数量: matchedUsers.length,
          结果详情: matchedUsers
        })
        
        setSuccessMessage(
          language === 'zh' 
            ? `找到 ${matchedUsers.length} 个匹配用户 (${duration}ms)` 
            : `Found ${matchedUsers.length} matching users (${duration}ms)`
        )
        setTimeout(() => setSuccessMessage(''), 3000)
      } else {
        console.log('❌ 搜索失败或返回空结果:', response)
        setError(language === 'zh' ? '搜索返回空结果' : 'Search returned empty results')
      }
    } catch (error: any) {
      console.error('❌ 搜索失败:', error)
      
      let shouldUseMockData = false
      
      // 显示具体的错误信息并决定是否使用模拟数据
      if (error.message?.includes('网络请求超时')) {
        setError(language === 'zh' 
          ? '请求超时，服务器处理时间过长，请稍后重试' 
          : 'Request timeout, server taking too long, please try again later'
        )
        shouldUseMockData = true
      } else if (error.message?.includes('Failed to fetch')) {
        setError(language === 'zh' 
          ? '网络连接失败，请检查网络连接' 
          : 'Network connection failed, please check your connection'
        )
        shouldUseMockData = true
      } else if (error.message?.includes('无效的token') || error.message?.includes('Invalid token') || error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        setError(language === 'zh' 
          ? '认证已过期，请重新登录' 
          : 'Authentication expired, please login again'
        )
        shouldUseMockData = true
      } else if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
        setError(language === 'zh' 
          ? '没有访问权限' 
          : 'Access denied'
        )
        shouldUseMockData = true
      } else {
        setError(error.message || (language === 'zh' ? '搜索失败，请重试' : 'Search failed, please try again'))
        shouldUseMockData = true
      }
      
      // 在开发环境或遇到认证/网络问题时使用模拟数据
      if (shouldUseMockData) {
        console.log('🔧 使用模拟数据，原因:', error.message)
        const mockUsers = generateMockUsers(searchDescription, selectedMatchType)
        console.log('🎭 生成的模拟用户数据:', mockUsers)
        
        setSearchResults(mockUsers)
        setSuccessMessage(
          language === 'zh' 
            ? `找到 ${mockUsers.length} 个匹配用户 (模拟数据)` 
            : `Found ${mockUsers.length} matching users (mock data)`
        )
        setTimeout(() => setSuccessMessage(''), 3000)
        
        console.log('✅ 模拟数据已设置，搜索结果数量:', mockUsers.length)
      }
    } finally {
      setIsMatchingLoading(false)
    }
  }

  const toggleTag = (tagName: string) => {
    setSelectedTags(prev => 
      prev.includes(tagName) 
        ? prev.filter(t => t !== tagName)
        : [...prev, tagName]
    )
  }

  const clearSearch = () => {
    console.log('🧹 清空搜索被调用')
    setSearchDescription('')
    setSelectedTags([])
    setSearchResults([])
    setError(null)
    setSuccessMessage('')
  }

  if (!isOpen) return null

  const modal = (
    <div className="fixed top-0 left-0 right-0 bottom-0 w-screen h-screen bg-black/50 flex items-center justify-center z-[9999] p-4">
      <div className="bg-card rounded-lg shadow-xl border w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <Search className={`h-6 w-6 ${
              selectedMatchType === '找队友' ? 'text-blue-600' : 'text-pink-600'
            }`} />
            <h2 className="text-xl font-semibold">
              {language === 'zh' ? '智能匹配搜索' : 'Smart Match Search'}
            </h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Search Form */}
          <div className="space-y-6 mb-8">
            {/* Match Type Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium">
                {language === 'zh' ? '匹配类型' : 'Match Type'}
              </label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setSelectedMatchType('找队友')}
                  className={`p-3 rounded-lg border-2 transition-colors ${
                    selectedMatchType === '找队友' 
                      ? 'border-blue-500 bg-blue-50 text-blue-700' 
                      : 'border-muted hover:border-blue-500'
                  }`}
                >
                  <Users className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-sm font-medium">
                    {language === 'zh' ? '寻找队友' : 'Find Teammates'}
                  </span>
                </button>
                
                <button
                  onClick={() => setSelectedMatchType('找对象')}
                  className={`p-3 rounded-lg border-2 transition-colors ${
                    selectedMatchType === '找对象' 
                      ? 'border-romantic-pink-500 bg-romantic-pink-50 text-romantic-pink-700' 
                      : 'border-muted hover:border-primary'
                  }`}
                >
                  <Heart className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-sm font-medium">
                    {language === 'zh' ? '寻找对象' : 'Find Partner'}
                  </span>
                </button>
              </div>
            </div>

            {/* Search Description */}
            <div className="space-y-3">
              <label className="text-sm font-medium">
                {language === 'zh' ? '描述您的需求' : 'Describe Your Needs'}
              </label>
              <textarea
                value={searchDescription}
                onChange={(e) => setSearchDescription(e.target.value)}
                placeholder={
                  selectedMatchType === '找队友'
                    ? (language === 'zh' ? '例如：寻找技术合作伙伴，擅长前端开发...' : 'e.g., Looking for technical partners, good at frontend development...')
                    : (language === 'zh' ? '例如：希望找到兴趣相投的伴侣，喜欢旅行和读书...' : 'e.g., Looking for a partner with similar interests, love traveling and reading...')
                }
                rows={4}
                className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
              />
            </div>

            {/* Tag Selection */}
            {userTags && userTags.length > 0 && (
              <div className="space-y-3">
                <label className="text-sm font-medium">
                  {language === 'zh' ? '选择标签（可选）' : 'Select Tags (Optional)'}
                </label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {userTags.map((tag, index) => (
                    <button
                      key={index}
                      onClick={() => toggleTag(tag.tag_name)}
                      className={`px-3 py-1 rounded-full text-sm transition-colors ${
                        selectedTags.includes(tag.tag_name)
                          ? selectedMatchType === '找队友'
                            ? 'bg-blue-600 text-white'
                            : 'bg-pink-600 text-white'
                          : 'bg-muted hover:bg-muted/80'
                      }`}
                    >
                      {tag.tag_name}
                    </button>
                  ))}
                </div>
                {selectedTags.length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    {language === 'zh' 
                      ? `已选择 ${selectedTags.length} 个标签` 
                      : `${selectedTags.length} tags selected`
                    }
                  </p>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <Button
                onClick={handleSearch}
                className={`flex-1 ${
                  selectedMatchType === '找队友' 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'bg-pink-600 hover:bg-pink-700 text-white'
                }`}
                disabled={isMatchingLoading || !searchDescription.trim()}
              >
                <Search className="h-4 w-4 mr-2" />
                {language === 'zh' ? '开始搜索' : 'Start Search'}
              </Button>
              
              {process.env.NODE_ENV === 'development' && (
                <Button
                  variant="outline"
                  onClick={() => {
                    console.log('🧪 测试按钮：直接设置模拟数据')
                    const mockUsers = generateMockUsers(searchDescription || '测试', selectedMatchType)
                    console.log('🎭 测试模拟数据:', mockUsers)
                    setSearchResults(mockUsers)
                    setError(null)
                    setSuccessMessage('测试数据已加载')
                  }}
                  className="text-xs"
                >
                  测试
                </Button>
              )}
              
              <Button variant="outline" onClick={clearSearch}>
                {language === 'zh' ? '清空' : 'Clear'}
              </Button>
            </div>
          </div>

          {/* Status Messages */}
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <span className="text-sm text-destructive">{error}</span>
            </div>
          )}
          
          {successMessage && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-600">{successMessage}</span>
              {successMessage.includes('演示数据') && (
                <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded-full">
                  {language === 'zh' ? '演示模式' : 'Demo Mode'}
                </span>
              )}
            </div>
          )}

          {/* Search Results */}
          {(() => {
            console.log('🔍 检查搜索结果显示条件:', {
              搜索结果长度: searchResults.length,
              搜索结果数组: searchResults,
              是否大于0: searchResults.length > 0,
              当前正在加载: isMatchingLoading
            })
            return null
          })()}
          {searchResults.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">
                  {language === 'zh' ? '搜索结果' : 'Search Results'}
                </h3>
                <span className="text-sm text-muted-foreground">
                  {searchResults.length} {language === 'zh' ? '个结果' : 'results'}
                </span>
              </div>
              
              <div className="grid gap-4">
                {searchResults.map((match, index) => (
                  <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary/20 to-primary/10 flex items-center justify-center">
                          <span className="text-primary font-medium text-lg">
                            {match.display_name.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-medium text-lg">{match.display_name}</h4>
                          <p className="text-sm text-muted-foreground">{match.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1 bg-yellow-50 px-2 py-1 rounded-full">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span className="text-sm font-medium text-yellow-700">
                          {Math.round(match.match_score * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      {match.user_tags.slice(0, 6).map((tag, tagIndex) => (
                        <span
                          key={tagIndex}
                          className="px-2 py-1 bg-primary/10 text-primary rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                      {match.user_tags.length > 6 && (
                        <span className="px-2 py-1 bg-muted rounded text-xs text-muted-foreground">
                          +{match.user_tags.length - 6}
                        </span>
                      )}
                    </div>
                    
                    {/* Metadata Summary */}
                    {match.metadata_summary?.profile && (
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        {match.metadata_summary.profile.personal?.location && (
                          <div className="flex items-center space-x-1">
                            <MapPin className="h-3 w-3" />
                            <span>{match.metadata_summary.profile.personal.location}</span>
                          </div>
                        )}
                        {match.metadata_summary.profile.personal?.age_range && (
                          <div className="flex items-center space-x-1">
                            <Calendar className="h-3 w-3" />
                            <span>{match.metadata_summary.profile.personal.age_range}</span>
                          </div>
                        )}
                        {match.metadata_summary.profile.professional?.industry && (
                          <span>{match.metadata_summary.profile.professional.industry}</span>
                        )}
                      </div>
                    )}
                    
                    {/* Contact Button */}
                    <div className="mt-3 pt-3 border-t">
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" className="flex-1">
                          {language === 'zh' ? '查看详情' : 'View Details'}
                        </Button>
                        <Button 
                          size="sm" 
                          className={`flex-1 ${
                            selectedMatchType === '找队友' 
                              ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                              : 'bg-pink-600 hover:bg-pink-700 text-white'
                          }`}
                        >
                          {selectedMatchType === '找队友' 
                            ? (language === 'zh' ? '发起合作' : 'Start Collaboration')
                            : (language === 'zh' ? '开始聊天' : 'Start Chat')
                          }
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {(() => {
            console.log('🔍 检查空状态显示条件:', {
              搜索结果长度: searchResults.length,
              搜索结果为0: searchResults.length === 0,
              非加载状态: !isMatchingLoading,
              有搜索描述: !!searchDescription.trim(),
              显示空状态: searchResults.length === 0 && !isMatchingLoading && !!searchDescription.trim()
            })
            return null
          })()}
          {searchResults.length === 0 && !isMatchingLoading && searchDescription.trim() && (
            <div className="text-center py-12">
              <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                {language === 'zh' ? '暂无匹配结果，请尝试调整搜索条件' : 'No matching results found, please try adjusting your search criteria'}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-4">
          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={onClose}>
              {language === 'zh' ? '关闭' : 'Close'}
            </Button>
          </div>
        </div>
      </div>
      {/* Matching Loading Modal */}
      <MatchingLoadingModal
        isOpen={isMatchingLoading}
        onClose={() => setIsMatchingLoading(false)}
        matchType={selectedMatchType}
        onComplete={() => setIsMatchingLoading(false)}
      />
    </div>
  )

  if (typeof window !== 'undefined') {
    return ReactDOM.createPortal(modal, document.body)
  }
  return null
} 