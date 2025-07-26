'use client'

import { useState, useEffect, useRef } from 'react'

export function useSpeech(language: 'zh' | 'en') {
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [isSupported, setIsSupported] = useState(false)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const speechSynthesisRef = useRef<SpeechSynthesis | null>(null)
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  useEffect(() => {
    // 检查浏览器支持
    const checkSupport = () => {
      const hasSpeechRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
      const hasSpeechSynthesis = 'speechSynthesis' in window
      setIsSupported(hasSpeechRecognition && hasSpeechSynthesis)
      return hasSpeechRecognition && hasSpeechSynthesis
    }

    if (checkSupport()) {
      initializeSpeechRecognition()
      initializeSpeechSynthesis()
    }
  }, [language])

  const initializeSpeechRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('Speech recognition not supported')
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = language === 'zh' ? 'zh-CN' : 'en-US'

    recognition.onstart = () => {
      setIsRecording(true)
      setTranscript('')
    }

    recognition.onresult = (event) => {
      const result = event.results[0][0].transcript
      setTranscript(result)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsRecording(false)
    }

    recognition.onend = () => {
      setIsRecording(false)
    }

    recognitionRef.current = recognition
  }

  const initializeSpeechSynthesis = () => {
    if (!('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported')
      return
    }

    speechSynthesisRef.current = window.speechSynthesis
  }

  const startRecording = async () => {
    if (!recognitionRef.current || isRecording) return

    try {
      // 请求麦克风权限
      await navigator.mediaDevices.getUserMedia({ audio: true })
      recognitionRef.current.start()
    } catch (error) {
      console.error('Error accessing microphone:', error)
    }
  }

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop()
    }
  }

  const speak = (text: string) => {
    if (!speechSynthesisRef.current || !text.trim()) return

    // 停止当前播放
    if (isPlaying) {
      stopSpeaking()
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = language === 'zh' ? 'zh-CN' : 'en-US'
    utterance.rate = 1.0
    utterance.pitch = 1.0
    utterance.volume = 1.0

    utterance.onstart = () => {
      setIsPlaying(true)
    }

    utterance.onend = () => {
      setIsPlaying(false)
    }

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error)
      setIsPlaying(false)
    }

    utteranceRef.current = utterance
    speechSynthesisRef.current.speak(utterance)
  }

  const stopSpeaking = () => {
    if (speechSynthesisRef.current && isPlaying) {
      speechSynthesisRef.current.cancel()
      setIsPlaying(false)
    }
  }

  // 清理函数
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
      if (speechSynthesisRef.current) {
        speechSynthesisRef.current.cancel()
      }
    }
  }, [])

  return {
    isRecording,
    isPlaying,
    transcript,
    isSupported,
    startRecording,
    stopRecording,
    speak,
    stopSpeaking
  }
}

// 扩展Window接口以包含WebKit前缀的API
declare global {
  interface Window {
    webkitSpeechRecognition: typeof SpeechRecognition
    SpeechRecognition: typeof SpeechRecognition
  }
} 