// Database Types
export interface Profile {
  id: string
  username: string
  created_at: string
  updated_at: string
}

export interface UserMetadata {
  id: string
  age?: number
  gender?: 'male' | 'female' | 'non-binary' | 'other' | 'prefer-not-to-say'
  location_city?: string
  location_state?: string
  location_country?: string
  latitude?: number
  longitude?: number
  bio?: string
  occupation?: string
  education?: string
  height_cm?: number
  looking_for?: string[]
  age_min?: number
  age_max?: number
  max_distance_km?: number
  profile_photo_url?: string
  additional_photos?: string[]
  social_links?: Record<string, any>
  preferences?: Record<string, any>
  is_profile_complete?: boolean
  is_verified?: boolean
  visibility?: 'public' | 'private' | 'friends_only'
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

export interface UserTag {
  id: string
  user_id: string
  tag_id: number
  weight?: number
  added_at: string
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
  metadata?: UserMetadata
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