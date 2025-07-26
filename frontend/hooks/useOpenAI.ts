'use client'

import { useState, useEffect } from 'react'
import OpenAI from 'openai'

export function useOpenAI() {
  const [isConnected, setIsConnected] = useState(false)
  const [openai, setOpenai] = useState<OpenAI | null>(null)

  useEffect(() => {
    // 初始化OpenAI客户端
    const initOpenAI = () => {
      try {
        const client = new OpenAI({
          apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
          dangerouslyAllowBrowser: true // 注意：生产环境应该通过后端API调用
        })
        setOpenai(client)
        setIsConnected(true)
      } catch (error) {
        console.error('Failed to initialize OpenAI:', error)
        setIsConnected(false)
      }
    }

    initOpenAI()
  }, [])

  const sendMessage = async (message: string): Promise<string | null> => {
    if (!openai || !isConnected) {
      console.error('OpenAI not initialized')
      return null
    }

    try {
      const completion = await openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "user",
            content: message
          }
        ],
        max_tokens: 1000,
        temperature: 0.7,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
      })

      return completion.choices[0]?.message?.content || null
    } catch (error: any) {
      console.error('Error sending message to OpenAI:', error)
      
      // 处理常见错误
      if (error.status === 401) {
        console.error('Invalid API key')
      } else if (error.status === 429) {
        console.error('Rate limit exceeded')
      } else if (error.status === 500) {
        console.error('OpenAI server error')
      }
      
      return null
    }
  }

  const sendStreamMessage = async (
    message: string, 
    onChunk: (chunk: string) => void
  ): Promise<void> => {
    if (!openai || !isConnected) {
      console.error('OpenAI not initialized')
      return
    }

    try {
      const stream = await openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "user",
            content: message
          }
        ],
        max_tokens: 1000,
        temperature: 0.7,
        stream: true
      })

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content
        if (content) {
          onChunk(content)
        }
      }
    } catch (error: any) {
      console.error('Error streaming message from OpenAI:', error)
    }
  }

  return {
    sendMessage,
    sendStreamMessage,
    isConnected
  }
} 