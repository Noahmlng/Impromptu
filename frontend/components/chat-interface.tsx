'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useAppStore } from '@/lib/store'
import { Send, Mic, MicOff, Smile } from 'lucide-react'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai' | 'other'
  timestamp: Date
  type?: 'text' | 'voice' | 'image'
}

interface ChatInterfaceProps {
  matchId?: string
  isAIChat?: boolean
}

export function ChatInterface({ matchId, isAIChat = false }: ChatInterfaceProps) {
  const { language, user } = useAppStore()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 模拟初始消息
  useEffect(() => {
    const initialMessages: Message[] = isAIChat ? [
      {
        id: '1',
        content: language === 'zh' 
          ? '你好！我是你的AI匹配助手。让我们开始了解你的需求吧！'
          : 'Hello! I\'m your AI matching assistant. Let\'s start understanding your needs!',
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      }
    ] : [
      {
        id: '1',
        content: language === 'zh' ? '你好！很高兴与你匹配！' : 'Hello! Nice to match with you!',
        sender: 'other',
        timestamp: new Date(),
        type: 'text'
      }
    ]
    setMessages(initialMessages)
  }, [isAIChat, language])

  const handleSendMessage = async () => {
    if (!inputText.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputText,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, newMessage])
    setInputText('')
    setIsLoading(true)

    // 模拟AI或其他用户回复
    setTimeout(() => {
      const response: Message = {
        id: (Date.now() + 1).toString(),
        content: isAIChat 
          ? (language === 'zh' 
              ? '让我分析一下你的需求。你更偏向于什么类型的匹配呢？'
              : 'Let me analyze your needs. What type of matching do you prefer?')
          : (language === 'zh' 
              ? '我也很期待我们的合作！'
              : 'I\'m also looking forward to our collaboration!'),
        sender: isAIChat ? 'ai' : 'other',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, response])
      setIsLoading(false)
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // 这里实现语音录制逻辑
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString(language === 'zh' ? 'zh-CN' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="flex flex-col h-full max-h-[600px] border rounded-lg bg-background">
      {/* Chat Header */}
      <div className="border-b p-4">
        <div className="flex items-center space-x-3">
          <Avatar className="h-10 w-10">
            <AvatarImage src={isAIChat ? undefined : "/api/placeholder/40/40"} />
            <AvatarFallback>
              {isAIChat ? '🤖' : 'M'}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <h3 className="font-semibold">
              {isAIChat 
                ? (language === 'zh' ? 'AI匹配助手' : 'AI Matching Assistant')
                : (language === 'zh' ? '匹配用户' : 'Matched User')
              }
            </h3>
            <p className="text-sm text-muted-foreground">
              {isAIChat 
                ? (language === 'zh' ? '在线 - 准备帮助你' : 'Online - Ready to help')
                : (language === 'zh' ? '在线' : 'Online')
              }
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-end space-x-2 max-w-[70%] ${
              message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}>
              {message.sender !== 'user' && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback>
                    {message.sender === 'ai' ? '🤖' : 'M'}
                  </AvatarFallback>
                </Avatar>
              )}
              <div
                className={`rounded-lg px-3 py-2 ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {formatTime(message.timestamp)}
                </p>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-end space-x-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback>
                  {isAIChat ? '🤖' : 'M'}
                </AvatarFallback>
              </Avatar>
              <div className="bg-muted rounded-lg px-3 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleRecording}
            className={isRecording ? 'text-red-500' : ''}
          >
            {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </Button>
          
          <div className="flex-1 relative">
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={language === 'zh' ? '输入消息...' : 'Type a message...'}
              disabled={isLoading}
            />
          </div>
          
          <Button
            variant="ghost"
            size="icon"
          >
            <Smile className="h-4 w-4" />
          </Button>
          
          <Button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
} 