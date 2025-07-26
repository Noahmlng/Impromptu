'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ChatInterface } from '@/components/chat-interface'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/hooks/useAuth'
import { matching } from '@/lib/api'
import { MatchUser } from '@/lib/types'
import { MessageCircle, Bot, Users, Heart, Search, Star, MapPin, AlertCircle, Brain } from 'lucide-react'

export default function ChatPage() {
  // Auth check
  const { user: authUser, isLoading: authLoading } = useRequireAuth()
  
  const { 
    themeMode, 
    language, 
    userTags,
    setIsLoading,
    setError,
    error,
    isLoading
  } = useAppStore()
  
  const [activeChatType, setActiveChatType] = useState<'ai' | 'match' | 'search' | null>(null)
  const [matchResults, setMatchResults] = useState<MatchUser[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [searchTags, setSearchTags] = useState<string[]>([])

  const chatOptions = [
    {
      id: 'personality',
      title: 'Talk to Linker',
      description: themeMode === 'romantic' 
        ? (language === 'zh' 
            ? '深度人格分析，支持语音对话，优化恋爱匹配效果'
            : 'Deep personality analysis with voice support to optimize romantic matching')
        : (language === 'zh' 
            ? '深度技能分析，支持语音对话，优化团队匹配效果'
            : 'Deep skills analysis with voice support to optimize team matching'),
      icon: Brain,
      color: themeMode === 'romantic' ? 'text-pink-500' : 'text-blue-500',
      special: true
    },
    {
      id: 'ai',
      title: language === 'zh' ? 'AI匹配助手' : 'AI Matching Assistant',
      description: language === 'zh' 
        ? '与AI助手对话，优化你的匹配设置'
        : 'Chat with AI to optimize your matching preferences',
      icon: Bot,
      color: 'text-blue-500'
    },
    {
      id: 'search',
      title: language === 'zh' ? '智能匹配' : 'Smart Matching',
      description: language === 'zh' 
        ? '基于描述和标签找到合适的匹配用户'
        : 'Find suitable matches based on description and tags',
      icon: Search,
      color: themeMode === 'romantic' ? 'text-romantic-pink-500' : 'text-miami-blue-500'
    },
    {
      id: 'match',
      title: language === 'zh' ? '匹配对话' : 'Match Conversations',
      description: language === 'zh' 
        ? '与你的匹配用户开始对话'
        : 'Start conversations with your matches',
      icon: themeMode === 'romantic' ? Heart : Users,
      color: themeMode === 'romantic' ? 'text-romantic-pink-500' : 'text-miami-blue-500'
    }
  ]

  const performSearch = async () => {
    if (!authUser || !searchQuery.trim()) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const matchType = themeMode === 'romantic' ? '找对象' : '找队友'
      const response = await matching.search(
        searchQuery,
        searchTags,
        matchType,
        10
      )
      
      if (response.success) {
        setMatchResults(response.data)
      }
    } catch (error: any) {
      setError(error.message || 'Search failed')
    } finally {
      setIsLoading(false)
    }
  }

  const addSearchTag = (tag: string) => {
    if (!searchTags.includes(tag)) {
      setSearchTags([...searchTags, tag])
    }
  }

  const removeSearchTag = (tag: string) => {
    setSearchTags(searchTags.filter(t => t !== tag))
  }

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (activeChatType === 'search') {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={() => setActiveChatType(null)}
          >
            ← {language === 'zh' ? '返回' : 'Back'}
          </Button>
          <h1 className="text-2xl font-bold">
            {language === 'zh' ? '智能匹配搜索' : 'Smart Match Search'}
          </h1>
          <div />
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-destructive" />
            <span className="text-sm text-destructive">{error}</span>
          </div>
        )}

        {/* Search Interface */}
        <Card>
          <CardHeader>
            <CardTitle>
              {language === 'zh' ? '搜索匹配用户' : 'Search for Matches'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search Query */}
            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'zh' ? '描述您的需求' : 'Describe what you are looking for'}
              </label>
              <textarea
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={language === 'zh' 
                  ? '例如：寻找一起创业的技术合伙人，有产品开发经验...'
                  : 'e.g., Looking for a technical co-founder with product development experience...'
                }
                rows={3}
                className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
              />
            </div>

            {/* Tag Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'zh' ? '添加标签' : 'Add Tags'}
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {userTags.slice(0, 10).map((tag) => (
                  <Button
                    key={tag.id}
                    variant="outline"
                    size="sm"
                    onClick={() => addSearchTag(tag.tag_name)}
                    disabled={searchTags.includes(tag.tag_name)}
                  >
                    {tag.tag_name}
                  </Button>
                ))}
              </div>
              
              {/* Selected Tags */}
              {searchTags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {searchTags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-primary text-primary-foreground rounded-full text-sm flex items-center space-x-1"
                    >
                      <span>{tag}</span>
                      <button
                        onClick={() => removeSearchTag(tag)}
                        className="ml-1 hover:bg-primary/80 rounded"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Search Button */}
            <Button
              onClick={performSearch}
              disabled={isLoading || !searchQuery.trim()}
              className="w-full"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>{language === 'zh' ? '搜索中...' : 'Searching...'}</span>
                </div>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  {language === 'zh' ? '开始搜索' : 'Start Search'}
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Search Results */}
        {matchResults.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>
                {language === 'zh' ? `找到 ${matchResults.length} 个匹配用户` : `Found ${matchResults.length} matches`}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {matchResults.map((match) => (
                  <div
                    key={match.user_id}
                    className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-r from-primary/20 to-primary/10 rounded-full flex items-center justify-center">
                          <span className="font-semibold text-primary text-lg">
                            {match.display_name.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <h3 className="font-semibold">{match.display_name}</h3>
                          <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            <span>{(match.match_score * 10).toFixed(1)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      {match.user_tags.slice(0, 3).map((tag: string, index: number) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-muted text-muted-foreground rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                      {match.user_tags.length > 3 && (
                        <span className="px-2 py-1 bg-muted text-muted-foreground rounded text-xs">
                          +{match.user_tags.length - 3}
                        </span>
                      )}
                    </div>

                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => {
                        // Start conversation with this match
                        console.log('Start conversation with', match.user_id)
                      }}
                    >
                      {language === 'zh' ? '开始对话' : 'Start Conversation'}
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  if (activeChatType) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-4">
          <Button
            variant="outline"
            onClick={() => setActiveChatType(null)}
          >
            ← {language === 'zh' ? '返回' : 'Back'}
          </Button>
        </div>
        
        <Card>
          <CardContent className="p-0">
            <ChatInterface 
              isAIChat={activeChatType === 'ai'} 
              matchId={activeChatType === 'match' ? '1' : undefined}
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
          <MessageCircle className={`h-12 w-12 ${themeMode === 'romantic' ? 'text-romantic-pink-500' : 'text-miami-blue-500'}`} />
          <h1 className="text-4xl font-bold">
            {language === 'zh' ? '智能对话中心' : 'Smart Chat Center'}
          </h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {language === 'zh' 
            ? '通过AI助手优化匹配，或与你的匹配用户开始深度对话。'
            : 'Optimize matching with AI assistant or start deep conversations with your matches.'
          }
        </p>
      </div>

      {/* Chat Options */}
      <div className="grid md:grid-cols-2 gap-6">
        {chatOptions.map((option) => {
          const OptionIcon = option.icon
          const isPersonality = option.id === 'personality'
          return (
            <Card 
              key={option.id}
              className={`cursor-pointer hover:shadow-lg transition-shadow ${
                isPersonality 
                  ? (themeMode === 'romantic' 
                      ? 'border-pink-200 bg-gradient-to-br from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20' 
                      : 'border-blue-200 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20') 
                  : ''
              }`}
              onClick={() => {
                if (isPersonality) {
                  window.location.href = '/personality-chat'
                } else {
                  setActiveChatType(option.id as 'ai' | 'match')
                }
              }}
            >
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <OptionIcon className={`h-8 w-8 ${option.color}`} />
                  <span>{option.title}</span>
                  {isPersonality && (
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      themeMode === 'romantic' 
                        ? 'bg-pink-100 dark:bg-pink-800 text-pink-800 dark:text-pink-200' 
                        : 'bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
                    }`}>
                      {language === 'zh' ? '新功能' : 'New'}
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">{option.description}</p>
                <Button className={`w-full ${
                  isPersonality 
                    ? (themeMode === 'romantic' 
                        ? 'bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700' 
                        : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700') 
                    : ''
                }`}>
                  {isPersonality 
                    ? (language === 'zh' ? '开始分析' : 'Start Analysis')
                    : (language === 'zh' ? '开始对话' : 'Start Chat')
                  }
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>{language === 'zh' ? '使用提示' : 'Getting Started'}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-muted/50 rounded-lg">
              <h4 className="font-medium mb-2">
                {language === 'zh' ? '1. 完善个人资料' : '1. Complete Your Profile'}
              </h4>
              <p className="text-sm text-muted-foreground">
                {language === 'zh' 
                  ? '前往个人资料页面，填写详细信息并生成个人标签'
                  : 'Go to profile page, fill in details and generate personal tags'
                }
              </p>
                  </div>
            
            <div className="p-4 bg-muted/50 rounded-lg">
              <h4 className="font-medium mb-2">
                {language === 'zh' ? '2. 智能匹配搜索' : '2. Smart Matching Search'}
              </h4>
              <p className="text-sm text-muted-foreground">
                {language === 'zh' 
                  ? '使用智能匹配功能找到符合您需求的用户'
                  : 'Use smart matching to find users that meet your needs'
                }
              </p>
                  </div>
            
            <div className="p-4 bg-muted/50 rounded-lg">
              <h4 className="font-medium mb-2">
                {language === 'zh' ? '3. AI助手优化' : '3. AI Assistant Optimization'}
              </h4>
              <p className="text-sm text-muted-foreground">
                {language === 'zh' 
                  ? '与AI助手对话，获得个性化的匹配建议'
                  : 'Chat with AI assistant for personalized matching advice'
                }
              </p>
              </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 