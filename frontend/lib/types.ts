// Backend API Types - Based on Comprehensive Matching System
export interface BackendUserInfo {
  user_id: string
  email: string
  display_name: string
  avatar_url?: string
  created_at: string
  updated_at: string
  last_login_at: string
  is_active: boolean
}

export interface UserMetadata {
  id?: string
  section_type: string
  section_key: string
  content: any
  data_type: string
  display_order: number
  created_at: string
  updated_at: string
}

export interface UserTag {
  id: number
  user_id: string
  tag_name: string
  tag_category: string
  confidence_score: number
  tag_source: string
  created_at: string
  is_active: boolean
}

// Legacy types for compatibility
export interface Profile {
  id: string
  username: string
  created_at: string
  updated_at: string
}

export interface Tag {
  id: number
  name: string
  category: 'interests' | 'personality' | 'skills' | 'lifestyle' | 'values' | 'hobbies'
  description?: string
  color?: string
  is_active?: boolean
  created_at: string
}

export interface Conversation {
  id: string
  user_id: string
  title?: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

// Application Types
export interface User {
  id: string
  name: string
  username?: string
  email?: string
  avatar?: string
  credits: number
  subscription?: string
  profile?: Profile
  metadata?: Record<string, any>  // Backend metadata structure
  backendInfo?: BackendUserInfo   // Direct backend user info
  tags?: UserTag[]               // User tags from backend
}

export interface SubscriptionPlan {
  id: string
  name: string
  originalPrice: number
  price: number
  coins: string
  isPopular: boolean
  isEarlyBird: boolean
  features: string[]
}

export interface SubscribeModalProps {
  show: boolean
  onClose: () => void
  subscriptionPlans: SubscriptionPlan[]
  onSubscribe: (planId: string) => void
  isPending: boolean
  t: TranslationObject
  user?: User
}

export interface TranslationObject {
  subscription: {
    title: string
    plan: string
    addon: string
    earlyBird: string
    bestValue: string
    currentPlan: string
    subscribe: string
    newUserGift: string
    validForMonth: string
  }
}

// Theme and Language Types
export type ThemeMode = 'romantic' | 'team'
export type Language = 'en' | 'zh'

// Store State
export interface AppState {
  themeMode: ThemeMode
  isDarkMode: boolean
  language: Language
  user: User | null
  setThemeMode: (mode: ThemeMode) => void
  setIsDarkMode: (isDark: boolean) => void
  setLanguage: (lang: Language) => void
  setUser: (user: User | null) => void
} 