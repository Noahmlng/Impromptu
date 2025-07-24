'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ChatInterface } from '@/components/chat-interface'
import { useAppStore } from '@/lib/store'
import { MessageCircle, Bot, Users, Heart } from 'lucide-react'

export default function ChatPage() {
  const { themeMode, language } = useAppStore()
  const [activeChatType, setActiveChatType] = useState<'ai' | 'match' | null>(null)

  const chatOptions = [
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
      id: 'match',
      title: language === 'zh' ? '匹配对话' : 'Match Conversations',
      description: language === 'zh' 
        ? '与你的匹配用户开始对话'
        : 'Start conversations with your matches',
      icon: themeMode === 'romantic' ? Heart : Users,
      color: themeMode === 'romantic' ? 'text-romantic-pink-500' : 'text-miami-blue-500'
    }
  ]

  const recentMatches = [
    { id: '1', name: 'Alice Chen', lastMessage: language === 'zh' ? '你好！' : 'Hello!', time: '2分钟前', unread: 2 },
    { id: '2', name: 'Bob Wang', lastMessage: language === 'zh' ? '很期待合作' : 'Looking forward to working together', time: '1小时前', unread: 0 },
    { id: '3', name: 'Carol Li', lastMessage: language === 'zh' ? '项目进展如何？' : 'How is the project going?', time: '昨天', unread: 1 },
  ]

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
          return (
            <Card 
              key={option.id}
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setActiveChatType(option.id as 'ai' | 'match')}
            >
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <OptionIcon className={`h-8 w-8 ${option.color}`} />
                  <span>{option.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">{option.description}</p>
                <Button className="w-full">
                  {language === 'zh' ? '开始对话' : 'Start Chat'}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Matches */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>{language === 'zh' ? '最近匹配' : 'Recent Matches'}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentMatches.map((match) => (
              <div 
                key={match.id}
                className="flex items-center justify-between p-3 hover:bg-muted/50 rounded-lg cursor-pointer"
                onClick={() => setActiveChatType('match')}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-primary/20 to-primary/10 rounded-full flex items-center justify-center">
                    <span className="font-semibold text-primary">
                      {match.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-medium">{match.name}</h3>
                    <p className="text-sm text-muted-foreground">{match.lastMessage}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">{match.time}</p>
                  {match.unread > 0 && (
                    <div className="w-5 h-5 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs mt-1">
                      {match.unread}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 