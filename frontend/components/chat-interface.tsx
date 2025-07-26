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
  const [micPermission, setMicPermission] = useState<'granted' | 'denied' | 'prompt' | 'checking'>('checking')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)
  const baseTextOnRecord = useRef('')

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 检查麦克风权限
  useEffect(() => {
    const checkMicrophonePermission = async () => {
      try {
        if (navigator.permissions) {
          const permission = await navigator.permissions.query({ name: 'microphone' as PermissionName })
          setMicPermission(permission.state as 'granted' | 'denied' | 'prompt')
          
          permission.onchange = () => {
            setMicPermission(permission.state as 'granted' | 'denied' | 'prompt')
          }
        } else {
          // 如果不支持权限API，设置为prompt状态
          setMicPermission('prompt')
        }
      } catch (error) {
        console.error('Error checking microphone permission:', error)
        setMicPermission('prompt')
      }
    }

    checkMicrophonePermission()
  }, [])

  useEffect(() => {
    // 检查浏览器是否支持语音识别
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.warn("Speech recognition not supported in this browser.")
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = language === 'zh' ? 'zh-CN' : 'en-US'

    recognition.onresult = (event: any) => {
      let interimTranscript = ''
      let finalTranscript = ''
      
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript
        } else {
          interimTranscript += event.results[i][0].transcript
        }
      }
      
      // 更新输入框内容：原有文本 + 最终识别结果 + 临时识别结果
      setInputText(baseTextOnRecord.current + finalTranscript + interimTranscript)
    }

    recognition.onstart = () => {
      console.log('Speech recognition started')
      setMicPermission('granted') // 成功启动说明权限已获得
    }

    recognition.onend = () => {
      console.log('Speech recognition ended')
      setIsRecording(false)
    }

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      setIsRecording(false)
      
      // 处理权限相关错误
      if (event.error === 'not-allowed' || event.error === 'permission-denied') {
        setMicPermission('denied')
      }
    }

    recognitionRef.current = recognition

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [language])

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

  const requestMicrophonePermission = async () => {
    try {
      // 通过getUserMedia请求麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // 立即关闭流，我们只需要权限
      stream.getTracks().forEach(track => track.stop())
      setMicPermission('granted')
      return true
    } catch (error) {
      console.error('Microphone permission denied:', error)
      setMicPermission('denied')
      return false
    }
  }

  const toggleRecording = async () => {
    if (!recognitionRef.current) {
      console.warn("Speech recognition not available")
      return
    }

    if (isRecording) {
      // 停止录音
      recognitionRef.current.stop()
      setIsRecording(false)
    } else {
      // 检查权限状态
      if (micPermission === 'denied') {
        alert(language === 'zh' 
          ? '麦克风权限被拒绝，请在浏览器设置中允许麦克风访问' 
          : 'Microphone permission denied. Please allow microphone access in browser settings')
        return
      }

      // 如果权限未知或需要申请，先请求权限
      if (micPermission === 'prompt' || micPermission === 'checking') {
        const hasPermission = await requestMicrophonePermission()
        if (!hasPermission) {
          return
        }
      }

      // 开始录音前保存当前输入的文本
      baseTextOnRecord.current = inputText ? inputText + ' ' : ''
      try {
        recognitionRef.current.start()
        setIsRecording(true)
      } catch (error) {
        console.error('Failed to start speech recognition:', error)
        setIsRecording(false)
        
        // 如果是权限错误，提示用户
        if (error instanceof Error && error.message.includes('not-allowed')) {
          alert(language === 'zh' 
            ? '需要麦克风权限才能使用语音输入功能' 
            : 'Microphone permission is required for voice input')
        }
      }
    }
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
            disabled={micPermission === 'checking' || !recognitionRef.current}
            className={`${isRecording ? 'text-red-500' : ''} ${
              micPermission === 'denied' ? 'text-gray-400' : ''
            }`}
            title={
              micPermission === 'denied' 
                ? (language === 'zh' ? '麦克风权限被拒绝' : 'Microphone permission denied')
                : micPermission === 'checking'
                ? (language === 'zh' ? '检查权限中...' : 'Checking permission...')
                : isRecording 
                ? (language === 'zh' ? '停止录音' : 'Stop recording')
                : (language === 'zh' ? '开始语音输入' : 'Start voice input')
            }
          >
            {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </Button>
          
          <div className="flex-1 relative">
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyPress}
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