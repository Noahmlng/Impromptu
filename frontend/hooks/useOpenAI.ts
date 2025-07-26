'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'

const BACKEND_API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'

interface OpenAIMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function useOpenAI() {
  const { themeMode, language } = useAppStore();
  const [isConnected, setIsConnected] = useState(true);

  const sendMessage = async (
    message: string, 
    history: OpenAIMessage[] = [], 
    isAnalysis: boolean = false
  ): Promise<string | null> => {
    
    const payload = {
      message,
      history,
      isAnalysis,
      themeMode,
      language,
    };

    try {
      const response = await fetch(`${BACKEND_API_URL}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error from backend chat API:', errorData.detail);
        return `Error: ${errorData.detail}`;
      }

      const data = await response.json();
      return data.response;
    } catch (error: any) {
      console.error('Error sending message to backend:', error)
      return "Failed to connect to the backend. Please check if the server is running."
    }
  }

  // Streaming is not implemented via Python backend in this refactor
  const sendStreamMessage = async (
    message: string, 
    onChunk: (chunk: string) => void,
    history: OpenAIMessage[] = [],
    isAnalysis: boolean = false
  ): Promise<void> => {
    console.warn('Streaming not yet implemented for Python backend. Using regular fetch.')
    const response = await sendMessage(message, history, isAnalysis);
    if (response) {
      onChunk(response);
    }
  }

  return {
    sendMessage,
    sendStreamMessage,
    isConnected
  }
} 