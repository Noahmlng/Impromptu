'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { useAppStore } from '@/lib/store'
import { useOpenAI } from '@/hooks/useOpenAI'
import { useSpeech } from '@/hooks/useSpeech'
import { profile } from '@/lib/api'
import { Send, Mic, MicOff, Volume2, VolumeX, Brain, Loader2, Download, Sparkles, User, Bot } from 'lucide-react'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  type?: 'text' | 'voice'
}

interface PersonalityAnalysisChatProps {
  onStageChange: (stage: 'intro' | 'analysis' | 'complete') => void
  currentStage: 'intro' | 'analysis' | 'complete'
}

interface PersonalityAnalysis {
  personality_traits: {
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    neuroticism: number
  }
  communication_style: string
  values: string[]
  interests: string[]
  // Romantic mode specific fields
  ideal_partner_traits?: string[]
  match_preferences?: {
    age_range: string
    personality_compatibility: string
    shared_interests_importance: number
  }
  // Team mode specific fields
  professional_skills?: string[]
  work_experience_level?: string
  ideal_teammate_traits?: string[]
  collaboration_preferences?: {
    project_type: string
    team_size_preference: string
    leadership_style: string
    communication_preference: string
  }
  analysis_summary: string
  recommendations: string[]
}

export function PersonalityAnalysisChat({ onStageChange, currentStage }: PersonalityAnalysisChatProps) {
  const { language, user, themeMode } = useAppStore()
  
  // Debug log to confirm themeMode
  console.log('PersonalityAnalysisChat - themeMode:', themeMode)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationHistory, setConversationHistory] = useState<string[]>([])
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [finalAnalysis, setFinalAnalysis] = useState<PersonalityAnalysis | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { sendMessage, isConnected } = useOpenAI()
  const { 
    isRecording, 
    isPlaying, 
    transcript, 
    startRecording, 
    stopRecording, 
    speak, 
    stopSpeaking 
  } = useSpeech(language)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 初始化对话
  useEffect(() => {
    const initMessage: Message = {
      id: '1',
      content: themeMode === 'romantic' 
        ? (language === 'zh' 
            ? `你好！我是Linker，你的AI人格分析助手。我会通过一系列问题来深入了解你的性格特征、价值观和偏好，从而为你提供更精准的恋爱匹配建议。

这个过程大约需要10-15分钟，你可以选择用文字回答或者点击麦克风图标进行语音交流。

让我们开始吧！首先请告诉我，你在寻找恋爱伙伴时，最看重对方的哪些特质？`
            : `Hello! I'm Linker, your AI personality analysis assistant. I'll understand your personality traits, values, and preferences through a series of questions to provide you with more accurate romantic matching suggestions.

This process takes about 10-15 minutes. You can choose to respond with text or click the microphone icon for voice communication.

Let's begin! First, please tell me what qualities do you value most when looking for a romantic partner?`)
        : (language === 'zh' 
            ? `你好！我是Linker，你的AI技能分析助手。我会通过一系列问题来深入了解你的专业技能、工作风格和合作偏好，从而为你提供更精准的团队匹配建议。

这个过程大约需要10-15分钟，你可以选择用文字回答或者点击麦克风图标进行语音交流。

让我们开始吧！首先请告诉我，你在寻找合作伙伴时，最看重对方的哪些专业能力？`
            : `Hello! I'm Linker, your AI skills analysis assistant. I'll understand your professional skills, work style, and collaboration preferences through a series of questions to provide you with more accurate team matching suggestions.

This process takes about 10-15 minutes. You can choose to respond with text or click the microphone icon for voice communication.

Let's begin! First, please tell me what professional abilities do you value most when looking for a collaboration partner?`),
      sender: 'ai',
      timestamp: new Date(),
      type: 'text'
    }
    setMessages([initMessage])
    onStageChange('analysis')
  }, [language, user, onStageChange, themeMode])

  // 语音转录完成后自动发送
  useEffect(() => {
    if (transcript && !isRecording) {
      setInputText(transcript)
      handleSendMessage(transcript)
    }
  }, [transcript, isRecording])

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || inputText
    if (!text.trim() || isLoading) return

    const newMessage: Message = {
      id: Date.now().toString(),
      content: text,
      sender: 'user',
      timestamp: new Date(),
      type: messageText ? 'voice' : 'text'
    }

    setMessages(prev => [...prev, newMessage])
    setInputText('')
    setIsLoading(true)

    // 更新对话历史
    const newHistory = [...conversationHistory, `User: ${text}`]
    setConversationHistory(newHistory)

    try {
      // 构建系统提示
      const systemPrompt = themeMode === 'romantic' 
        ? (language === 'zh' 
            ? `你是Linker，一个专业的人格分析师，专门通过对话来了解用户的性格特征。你的目标是：

1. 通过自然对话了解用户的：
   - 性格特征（开放性、尽责性、外向性、宜人性、神经质）
   - 沟通风格和恋爱观
   - 价值观和兴趣爱好
   - 理想恋爱伙伴特质
   - 恋爱偏好和期望

2. 根据对话轮数调整问题深度：
   - 1-3轮：基础信息和初步了解
   - 4-8轮：深入探索性格特征和恋爱价值观
   - 9-12轮：具体情感场景问题和恋爱偏好细节
   - 12轮以上：总结和确认

3. 问题风格：
   - 自然对话，不要像问卷调查
   - 根据用户回答调整后续问题
   - 可以使用恋爱场景假设来了解用户反应
   - 保持友好和专业的语调

4. 当对话进行到足够深度（通常12-15轮）时，提供完整的人格分析报告。

当前对话轮数：${Math.floor(newHistory.length / 2) + 1}

请根据用户的回答继续对话，深入了解他们的恋爱人格特征。`
            : `You are Linker, a professional personality analyst who understands users' personality traits through conversation. Your goals are:

1. Understand the user's:
   - Personality traits (openness, conscientiousness, extraversion, agreeableness, neuroticism)
   - Communication style and romantic views
   - Values and interests
   - Ideal romantic partner traits
   - Romantic preferences and expectations

2. Adjust question depth based on conversation rounds:
   - 1-3 rounds: Basic information and initial understanding
   - 4-8 rounds: Deep exploration of personality traits and romantic values
   - 9-12 rounds: Specific romantic scenario questions and preference details
   - 12+ rounds: Summary and confirmation

3. Question style:
   - Natural conversation, not like a questionnaire
   - Adjust follow-up questions based on user responses
   - Use romantic scenario assumptions to understand user reactions
   - Maintain friendly and professional tone

4. When the conversation reaches sufficient depth (usually 12-15 rounds), provide a complete personality analysis report.

Current conversation round: ${Math.floor(newHistory.length / 2) + 1}

Please continue the conversation based on the user's response, diving deeper into their romantic personality traits.`)
        : (language === 'zh' 
            ? `你是Linker，一个专业的技能分析师，专门通过对话来了解用户的专业能力和合作风格。你的目标是：

1. 通过自然对话了解用户的：
   - 专业技能和经验水平
   - 工作风格和合作方式
   - 职业价值观和目标
   - 理想合作伙伴特质
   - 团队协作偏好

2. 根据对话轮数调整问题深度：
   - 1-3轮：基础信息和专业背景了解
   - 4-8轮：深入探索技能特长和工作风格
   - 9-12轮：具体工作场景问题和合作偏好细节
   - 12轮以上：总结和确认

3. 问题风格：
   - 自然对话，不要像问卷调查
   - 根据用户回答调整后续问题
   - 可以使用工作场景假设来了解用户反应
   - 保持友好和专业的语调

4. 当对话进行到足够深度（通常12-15轮）时，提供完整的技能分析报告。

当前对话轮数：${Math.floor(newHistory.length / 2) + 1}

请根据用户的回答继续对话，深入了解他们的专业技能和合作风格。`
            : `You are Linker, a professional skills analyst who understands users' professional abilities and collaboration style through conversation. Your goals are:

1. Understand the user's:
   - Professional skills and experience level
   - Work style and collaboration methods
   - Career values and goals
   - Ideal collaboration partner traits
   - Team cooperation preferences

2. Adjust question depth based on conversation rounds:
   - 1-3 rounds: Basic information and professional background understanding
   - 4-8 rounds: Deep exploration of skill strengths and work style
   - 9-12 rounds: Specific work scenario questions and collaboration preference details
   - 12+ rounds: Summary and confirmation

3. Question style:
   - Natural conversation, not like a questionnaire
   - Adjust follow-up questions based on user responses
   - Use work scenario assumptions to understand user reactions
   - Maintain friendly and professional tone

4. When the conversation reaches sufficient depth (usually 12-15 rounds), provide a complete skills analysis report.

Current conversation round: ${Math.floor(newHistory.length / 2) + 1}

Please continue the conversation based on the user's response, diving deeper into their professional skills and collaboration style.`)

      const conversationContext = newHistory.join('\n')
      const prompt = `${systemPrompt}\n\n对话历史：\n${conversationContext}\n\nAI:`

      const response = await sendMessage(prompt)
      
      if (response) {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
          type: 'text'
        }
        
        setMessages(prev => [...prev, aiMessage])
        setConversationHistory([...newHistory, `AI: ${response}`])
        
        // 更新进度
        const progress = Math.min((newHistory.length / 2) * 8, 90)
        setAnalysisProgress(progress)
        
        // 语音播放AI回复
        if (language === 'zh') {
          speak(response)
        }

        // 检查是否需要生成最终分析报告
        if (newHistory.length >= 24) { // 12轮对话
          setTimeout(() => generateFinalAnalysis(newHistory), 2000)
        }
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: language === 'zh' 
          ? '抱歉，我遇到了一些技术问题。请稍后再试。'
          : 'Sorry, I encountered some technical issues. Please try again later.',
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const generateFinalAnalysis = async (history: string[]) => {
    setIsLoading(true)
    setAnalysisProgress(95)

    try {
      const analysisPrompt = themeMode === 'romantic' 
        ? (language === 'zh' 
            ? `基于以下对话历史，请生成一个详细的恋爱人格分析报告，格式为JSON：

对话历史：
${history.join('\n')}

请返回以下格式的JSON对象：
{
  "personality_traits": {
    "openness": 数值(1-10),
    "conscientiousness": 数值(1-10),
    "extraversion": 数值(1-10),
    "agreeableness": 数值(1-10),
    "neuroticism": 数值(1-10)
  },
  "communication_style": "简要描述用户的沟通风格",
  "values": ["价值观1", "价值观2", "价值观3"],
  "interests": ["兴趣1", "兴趣2", "兴趣3"],
  "ideal_partner_traits": ["理想恋爱伙伴特质1", "理想恋爱伙伴特质2", "理想恋爱伙伴特质3"],
  "match_preferences": {
    "age_range": "年龄偏好范围",
    "personality_compatibility": "性格兼容性偏好",
    "shared_interests_importance": 数值(1-10)
  },
  "analysis_summary": "详细的恋爱人格分析总结",
  "recommendations": ["恋爱匹配建议1", "恋爱匹配建议2", "恋爱匹配建议3"]
}`
            : `Based on the following conversation history, please generate a detailed romantic personality analysis report in JSON format:

Conversation History:
${history.join('\n')}

Please return a JSON object in the following format:
{
  "personality_traits": {
    "openness": number(1-10),
    "conscientiousness": number(1-10),
    "extraversion": number(1-10),
    "agreeableness": number(1-10),
    "neuroticism": number(1-10)
  },
  "communication_style": "Brief description of user's communication style",
  "values": ["value1", "value2", "value3"],
  "interests": ["interest1", "interest2", "interest3"],
  "ideal_partner_traits": ["ideal romantic partner trait1", "ideal romantic partner trait2", "ideal romantic partner trait3"],
  "match_preferences": {
    "age_range": "preferred age range",
    "personality_compatibility": "personality compatibility preference",
    "shared_interests_importance": number(1-10)
  },
  "analysis_summary": "Detailed romantic personality analysis summary",
  "recommendations": ["romantic matching recommendation1", "romantic matching recommendation2", "romantic matching recommendation3"]
}`)
        : (language === 'zh' 
            ? `基于以下对话历史，请生成一个详细的团队合作技能分析报告，格式为JSON：

对话历史：
${history.join('\n')}

请返回以下格式的JSON对象：
{
  "personality_traits": {
    "openness": 数值(1-10),
    "conscientiousness": 数值(1-10),
    "extraversion": 数值(1-10),
    "agreeableness": 数值(1-10),
    "neuroticism": 数值(1-10)
  },
  "communication_style": "简要描述用户的沟通风格",
  "values": ["价值观1", "价值观2", "价值观3"],
  "interests": ["兴趣1", "兴趣2", "兴趣3"],
  "professional_skills": ["专业技能1", "专业技能2", "专业技能3"],
  "work_experience_level": "工作经验水平描述",
  "ideal_teammate_traits": ["理想队友特质1", "理想队友特质2", "理想队友特质3"],
  "collaboration_preferences": {
    "project_type": "偏好的项目类型",
    "team_size_preference": "偏好的团队规模",
    "leadership_style": "领导风格偏好",
    "communication_preference": "沟通方式偏好"
  },
  "analysis_summary": "详细的团队合作技能分析总结",
  "recommendations": ["团队匹配建议1", "团队匹配建议2", "团队匹配建议3"]
}`
            : `Based on the following conversation history, please generate a detailed team collaboration skills analysis report in JSON format:

Conversation History:
${history.join('\n')}

Please return a JSON object in the following format:
{
  "personality_traits": {
    "openness": number(1-10),
    "conscientiousness": number(1-10),
    "extraversion": number(1-10),
    "agreeableness": number(1-10),
    "neuroticism": number(1-10)
  },
  "communication_style": "Brief description of user's communication style",
  "values": ["value1", "value2", "value3"],
  "interests": ["interest1", "interest2", "interest3"],
  "professional_skills": ["professional skill1", "professional skill2", "professional skill3"],
  "work_experience_level": "Description of work experience level",
  "ideal_teammate_traits": ["ideal teammate trait1", "ideal teammate trait2", "ideal teammate trait3"],
  "collaboration_preferences": {
    "project_type": "preferred project type",
    "team_size_preference": "preferred team size",
    "leadership_style": "leadership style preference",
    "communication_preference": "communication method preference"
  },
  "analysis_summary": "Detailed team collaboration skills analysis summary",
  "recommendations": ["team matching recommendation1", "team matching recommendation2", "team matching recommendation3"]
}`)

      const analysisResponse = await sendMessage(analysisPrompt)
      
      if (analysisResponse) {
        try {
          const analysis = JSON.parse(analysisResponse) as PersonalityAnalysis
          setFinalAnalysis(analysis)
          setAnalysisProgress(100)
          onStageChange('complete')
          
          // 保存分析结果到用户档案
          await saveAnalysisToProfile(analysis)
          
          const completionMessage: Message = {
            id: (Date.now() + 2).toString(),
            content: themeMode === 'romantic' 
              ? (language === 'zh' 
                  ? '太棒了！我已经完成了对你的恋爱人格分析。分析报告已经生成，包含了你的性格特征、理想伙伴特质和恋爱偏好等信息。你可以查看详细结果并下载报告。这些信息将帮助我们为你提供更精准的恋爱匹配建议。'
                  : 'Excellent! I have completed your romantic personality analysis. The analysis report has been generated, including your personality traits, ideal partner qualities, and romantic preferences. You can view the detailed results and download the report. This information will help us provide you with more accurate romantic matching suggestions.')
              : (language === 'zh' 
                  ? '太棒了！我已经完成了对你的团队合作技能分析。分析报告已经生成，包含了你的专业技能、工作风格、理想队友特质和合作偏好等信息。你可以查看详细结果并下载报告。这些信息将帮助我们为你提供更精准的团队匹配建议。'
                  : 'Excellent! I have completed your team collaboration skills analysis. The analysis report has been generated, including your professional skills, work style, ideal teammate traits, and collaboration preferences. You can view the detailed results and download the report. This information will help us provide you with more accurate team matching suggestions.'),
            sender: 'ai',
            timestamp: new Date(),
            type: 'text'
          }
          setMessages(prev => [...prev, completionMessage])
          
        } catch (parseError) {
          console.error('Error parsing analysis:', parseError)
          throw new Error('Failed to parse analysis report')
        }
      }
    } catch (error) {
      console.error('Error generating final analysis:', error)
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: language === 'zh' 
          ? '生成分析报告时遇到问题，请稍后再试。'
          : 'Encountered an issue generating the analysis report. Please try again later.',
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const saveAnalysisToProfile = async (analysis: PersonalityAnalysis) => {
    try {
      await profile.createMetadata({
        section_type: 'personality_analysis',
        section_key: 'ai_analysis',
        content: {
          analysis_data: analysis,
          conversation_history: conversationHistory,
          analysis_date: new Date().toISOString(),
          version: '1.0'
        }
      })
    } catch (error) {
      console.error('Error saving analysis to profile:', error)
    }
  }

  const downloadAnalysisReport = () => {
    if (!finalAnalysis) return

    const reportData = {
      user_info: {
        name: user?.name || 'User',
        analysis_date: new Date().toISOString()
      },
      personality_analysis: finalAnalysis,
      conversation_summary: conversationHistory
    }

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `personality-analysis-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString(language === 'zh' ? 'zh-CN' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="flex flex-col h-[calc(100vh-9rem)] bg-gradient-to-br from-background via-background to-muted/20">
      {/* Enhanced Progress Bar */}
      {currentStage === 'analysis' && (
        <div className={`p-6 border-b bg-gradient-to-r ${
          themeMode === 'romantic' 
            ? 'from-pink-50 to-purple-50 dark:from-pink-900/10 dark:to-purple-900/10 border-pink-200/50' 
            : 'from-blue-50 to-cyan-50 dark:from-blue-900/10 dark:to-cyan-900/10 border-blue-200/50'
        } backdrop-blur-sm`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-full ${
                themeMode === 'romantic' ? 'bg-pink-500/10' : 'bg-blue-500/10'
              }`}>
                <Brain className={`h-5 w-5 ${
                  themeMode === 'romantic' ? 'text-pink-600' : 'text-blue-600'
                }`} />
              </div>
              <div>
                <h3 className="font-semibold text-lg">
                  {language === 'zh' ? '分析进度' : 'Analysis Progress'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {language === 'zh' ? 'AI正在深入了解你的个性特征' : 'AI is getting to know your personality traits'}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{Math.round(analysisProgress)}%</div>
              <div className="text-xs text-muted-foreground">
                {language === 'zh' ? '已完成' : 'Completed'}
              </div>
            </div>
          </div>
          <div className="relative">
            <div className="w-full bg-muted/50 rounded-full h-3 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-1000 ease-out ${
                  themeMode === 'romantic' 
                    ? 'bg-gradient-to-r from-pink-500 to-purple-500' 
                    : 'bg-gradient-to-r from-blue-500 to-cyan-500'
                } shadow-sm`}
                style={{ width: `${analysisProgress}%` }}
              />
            </div>
            <Sparkles className={`absolute top-1/2 -translate-y-1/2 h-4 w-4 ${
              themeMode === 'romantic' ? 'text-pink-500' : 'text-blue-500'
            } animate-pulse`} style={{ left: `${Math.max(analysisProgress - 5, 0)}%` }} />
          </div>
        </div>
      )}

      {/* Enhanced Analysis Complete Banner */}
      {finalAnalysis && currentStage === 'complete' && (
        <div className="p-6 border-b bg-gradient-to-r from-green-50 via-emerald-50 to-teal-50 dark:from-green-900/20 dark:via-emerald-900/20 dark:to-teal-900/20 border-green-200/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-green-500/10 rounded-full">
                <Brain className="h-8 w-8 text-green-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-green-800 dark:text-green-200 flex items-center space-x-2">
                  <span>
                    {language === 'zh' ? '人格分析完成！' : 'Personality Analysis Complete!'}
                  </span>
                  <Sparkles className="h-5 w-5 text-green-600" />
                </h3>
                <p className="text-green-700 dark:text-green-300 text-sm">
                  {language === 'zh' 
                    ? '你的个性档案已生成，匹配精度将大幅提升' 
                    : 'Your personality profile has been generated, matching accuracy will be greatly improved'
                  }
                </p>
              </div>
            </div>
            <Button
              onClick={downloadAnalysisReport}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg"
            >
              <Download className="h-4 w-4 mr-2" />
              {language === 'zh' ? '下载报告' : 'Download Report'}
            </Button>
          </div>
        </div>
      )}

      {/* Messages Area with Enhanced Design */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex items-start ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className={`flex items-start space-x-3 max-w-[85%] ${
              message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}>
              {/* Enhanced Avatar */}
              <div className="flex-shrink-0">
                {message.sender === 'ai' ? (
                  <div className={`p-3 rounded-2xl shadow-lg ${
                    themeMode === 'romantic' 
                      ? 'bg-gradient-to-br from-pink-500 to-purple-600' 
                      : 'bg-gradient-to-br from-blue-500 to-cyan-600'
                  }`}>
                    <Bot className="h-6 w-6 text-white" />
                  </div>
                ) : (
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-slate-600 to-slate-700 shadow-lg">
                    <User className="h-6 w-6 text-white" />
                  </div>
                )}
              </div>

              {/* Enhanced Message Bubble */}
              <Card className={`shadow-xl border-0 ${
                message.sender === 'user'
                  ? 'bg-gradient-to-br from-primary to-primary/90 text-primary-foreground'
                  : 'bg-gradient-to-br from-card to-card/90 border border-border/50'
              } backdrop-blur-sm`}>
                <CardContent className="p-4">
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </p>
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-current/10">
                    <div className="text-xs opacity-70 flex items-center space-x-2">
                      <span>{formatTime(message.timestamp)}</span>
                      {message.type === 'voice' && (
                        <div className="flex items-center space-x-1">
                          <Volume2 className="h-3 w-3" />
                          <span>{language === 'zh' ? '语音' : 'Voice'}</span>
                        </div>
                      )}
                    </div>
                    {message.sender === 'ai' && (
                      <div className="flex items-center space-x-1 text-xs opacity-70">
                        <Brain className="h-3 w-3" />
                        <span>AI</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ))}
        
        {/* Enhanced Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="flex items-start space-x-3 max-w-[85%]">
              <div className={`p-3 rounded-2xl shadow-lg ${
                themeMode === 'romantic' 
                  ? 'bg-gradient-to-br from-pink-500 to-purple-600' 
                  : 'bg-gradient-to-br from-blue-500 to-cyan-600'
              }`}>
                <Bot className="h-6 w-6 text-white" />
              </div>
              <Card className="shadow-xl border-0 bg-gradient-to-br from-card to-card/90 border border-border/50 backdrop-blur-sm">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {language === 'zh' ? 'Linker正在思考...' : 'Linker is thinking...'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Enhanced Input Area */}
      {currentStage !== 'complete' && (
        <div className={`border-t p-6 bg-gradient-to-r ${
          themeMode === 'romantic' 
            ? 'from-background via-pink-50/30 to-background' 
            : 'from-background via-blue-50/30 to-background'
        } backdrop-blur-sm`}>
          <div className="flex items-center space-x-3">
            {/* Voice Recording Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={isRecording ? stopRecording : startRecording}
              className={`relative h-12 w-12 rounded-full transition-all duration-200 ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg scale-110' 
                  : 'hover:bg-muted/50'
              }`}
              disabled={isLoading}
            >
              {isRecording ? (
                <>
                  <MicOff className="h-5 w-5" />
                  <div className="absolute inset-0 rounded-full border-2 border-red-300 animate-ping" />
                </>
              ) : (
                <Mic className="h-5 w-5" />
              )}
            </Button>
            
            {/* Message Input */}
            <div className="flex-1 relative">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={language === 'zh' ? '输入你的回答，或点击麦克风语音回复...' : 'Type your response, or click mic for voice...'}
                disabled={isLoading || isRecording}
                className="h-12 pr-4 bg-background/50 backdrop-blur-sm border-2 focus:border-primary/50 rounded-xl shadow-sm"
              />
              {isRecording && (
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-sm text-red-500 font-medium">
                    {language === 'zh' ? '录音中...' : 'Recording...'}
                  </span>
                </div>
              )}
            </div>
            
            {/* Voice Control Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={isPlaying ? stopSpeaking : undefined}
              disabled={!isPlaying}
              className="h-12 w-12 rounded-full hover:bg-muted/50"
            >
              {isPlaying ? (
                <VolumeX className="h-5 w-5 text-primary" />
              ) : (
                <Volume2 className="h-5 w-5" />
              )}
            </Button>
            
            {/* Send Button */}
            <Button
              onClick={() => handleSendMessage()}
              disabled={!inputText.trim() || isLoading || isRecording}
              className={`h-12 w-12 rounded-full shadow-lg transition-all duration-200 ${
                inputText.trim() && !isLoading && !isRecording
                  ? 'scale-110 shadow-xl'
                  : ''
              } ${
                themeMode === 'romantic' 
                  ? 'bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600' 
                  : 'bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600'
              }`}
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>

        </div>
      )}
    </div>
  )
} 