// API Client for Comprehensive Matching System
import { supabase } from './supabase'
import { MatchUser } from './types'

// Base URL for the backend API (only for AI operations like tag generation and matching)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types based on backend API documentation
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  display_name: string
  avatar_url?: string
}

export interface AuthResponse {
  success: boolean
  message: string
  data: {
    user_id: string
    email: string
    display_name: string
    avatar_url?: string
    subscription_type: string
    created_at: string
    updated_at: string
    last_login_at?: string
    is_active: boolean
    token: string
  }
}

export interface UserInfo {
  user_id: string
  email: string
  display_name: string
  avatar_url?: string
  subscription_type: string
  created_at: string
  updated_at: string
  last_login_at: string
  is_active: boolean
}

export interface MetadataEntry {
  section_type: string
  section_key: string
  content: any
  data_type?: string
  display_order?: number
}

export interface MetadataResponse {
  success: boolean
  message?: string
  data: {
    [section_type: string]: {
      [section_key: string]: {
        content: any
        data_type: string
        display_order: number
        created_at: string
        updated_at: string
      }
    }
  }
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

export interface GenerateTagsRequest {
  request_type: '找队友' | '找对象'
}

export interface GenerateTagsResponse {
  success: boolean
  message: string
  data: {
    generated_tags: UserTag[]
    topics: number[][]
    user_text_length: number
    request_type: string
  }
}

export interface ManualTagsRequest {
  tags: (string | { name: string; category?: string; confidence?: number })[]
}



export interface MatchSearchRequest {
  description: string
  tags: string[]
  match_type: '找队友' | '找对象'
  limit?: number
}

export interface MatchSearchResponse {
  success: boolean
  message: string
  data: {
    matched_users: MatchUser[]
    total: number
    query: MatchSearchRequest
  }
}

export interface CompatibilityAnalysisRequest {
  target_user_id: string
}

export interface CompatibilityAnalysisResponse {
  success: boolean
  data: {
    user_a: string
    user_b: string
    overall_score: number
    tag_similarity: number
    text_similarity: number
    common_tags: string[]
    total_tags_a: number
    total_tags_b: number
    recommendation: string
  }
}

export interface ApiResponse<T> {
  success: boolean
  message?: string
  data?: T
  error?: string
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null
  private defaultTimeout = 10000 // 10秒超时

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    console.log('🚀 [ApiClient] Initialized with base URL:', this.baseUrl)
    // Try to get token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token')
      console.log('🔑 [ApiClient] Loaded token from localStorage:', this.token ? 'TOKEN_EXISTS' : 'NO_TOKEN')
    }
  }

  // 添加超时包装函数
  private async fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.defaultTimeout)
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      return response
    } catch (error: any) {
      clearTimeout(timeoutId)
      if (error.name === 'AbortError') {
        throw new Error('网络请求超时，请检查网络连接')
      }
      throw error
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }
    
    // 从localStorage获取token（兼容旧方式）
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }
    
    return headers
  }

  // 新的方法：从Supabase获取认证header
  private async getSupabaseHeaders(): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }
    
    console.log('🔑 [getSupabaseHeaders] Getting authentication headers...')
    
    // 优先使用后端JWT token（从store获取）
    if (typeof window !== 'undefined') {
      try {
        const store = await import('@/lib/store')
        const authToken = store.useAppStore.getState().authToken
        console.log('🏪 [getSupabaseHeaders] Store authToken:', authToken ? 'EXISTS' : 'NULL')
        
        if (authToken) {
          headers['Authorization'] = `Bearer ${authToken}`
          console.log('✅ [getSupabaseHeaders] Using store authToken')
          return headers
        }
      } catch (error) {
        console.error('❌ [getSupabaseHeaders] Error accessing store:', error)
      }
    }
    
    // 如果没有后端token，尝试使用旧的localStorage token
    console.log('🔑 [getSupabaseHeaders] Checking localStorage token:', this.token ? 'EXISTS' : 'NULL')
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
      console.log('✅ [getSupabaseHeaders] Using localStorage token')
      return headers
    }
    
    // 最后才尝试使用Supabase token（通常只用于直接访问Supabase的操作）
    try {
      const { data: { session } } = await supabase.auth.getSession()
      console.log('🔑 [getSupabaseHeaders] Supabase session:', session ? 'EXISTS' : 'NULL')
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`
        console.log('✅ [getSupabaseHeaders] Using Supabase session token')
        return headers
      }
    } catch (error) {
      console.error('❌ [getSupabaseHeaders] Error getting Supabase session:', error)
    }
    
    console.log('⚠️ [getSupabaseHeaders] No valid token found!')
    console.log('📋 [getSupabaseHeaders] Final headers:', headers)
    return headers
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorText = await response.text()
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      
      try {
        const errorData = JSON.parse(errorText)
        errorMessage = errorData.message || errorData.error || errorMessage
      } catch {
        // If parsing fails, use the raw text
        errorMessage = errorText || errorMessage
      }
      
      // 为常见的HTTP状态码提供更友好的错误信息
      if (response.status === 401) {
        errorMessage = 'HTTP 401: Unauthorized'
      } else if (response.status === 403) {
        errorMessage = 'HTTP 403: 权限不足'
      } else if (response.status === 404) {
        errorMessage = 'HTTP 404: 请求的资源不存在'
      } else if (response.status === 500) {
        errorMessage = 'HTTP 500: 服务器内部错误'
      } else if (response.status === 503) {
        errorMessage = 'HTTP 503: 服务暂时不可用'
      }
      
      throw new Error(errorMessage)
    }
    
    return response.json()
  }

  public setToken(token: string) {
    console.log('🔑 [ApiClient.setToken] Setting token:', token ? 'TOKEN_PROVIDED' : 'NULL_TOKEN')
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
      console.log('💾 [ApiClient.setToken] Token saved to localStorage')
    }
  }

  public clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  // Authentication APIs
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    
    const result = await this.handleResponse<AuthResponse>(response)
    if (result.success && result.data.token) {
      this.setToken(result.data.token)
    }
    return result
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    console.log('🔐 [ApiClient.login] Attempting login for:', data.email)
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    
    const result = await this.handleResponse<AuthResponse>(response)
    if (result.success && result.data.token) {
      console.log('✅ [ApiClient.login] Login successful, setting token')
      
      // 优先设置store中的token
      if (typeof window !== 'undefined') {
        try {
          const store = await import('@/lib/store')
          store.useAppStore.getState().setAuthToken(result.data.token)
          
          // 确保 last_login_at 字段存在
          const userData = {
            ...result.data,
            last_login_at: result.data.last_login_at || new Date().toISOString()
          }
          store.useAppStore.getState().setBackendUser(userData)
          console.log('✅ [ApiClient.login] Token and user data set in store')
        } catch (error) {
          console.error('❌ [ApiClient.login] Failed to set auth data in store:', error)
        }
      }
      
      // 同时设置到localStorage（向后兼容）
      this.setToken(result.data.token)
    } else {
      console.log('❌ [ApiClient.login] Login failed:', result.message)
    }
    return result
  }

  async getCurrentUser(): Promise<ApiResponse<UserInfo>> {
    console.log('🔗 [ApiClient.getCurrentUser] Starting HTTP request...')
    console.log('🔗 [ApiClient.getCurrentUser] URL:', `${this.baseUrl}/api/auth/user`)
    console.log('🔗 [ApiClient.getCurrentUser] Headers:', this.getHeaders())
    
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/auth/user`, {
      method: 'GET',
      headers: this.getHeaders(),
    })
    
    console.log('📡 [ApiClient.getCurrentUser] HTTP response status:', response.status)
    console.log('📡 [ApiClient.getCurrentUser] HTTP response ok:', response.ok)
    
    const result = await this.handleResponse<ApiResponse<UserInfo>>(response)
    console.log('📊 [ApiClient.getCurrentUser] Parsed response:', result)
    
    return result
  }

  async verifyTokenFast(): Promise<{ valid: boolean; user_id?: string; email?: string }> {
    console.log('⚡ [ApiClient.verifyTokenFast] Starting fast token verification...')
    
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/auth/verify-fast`, {
      method: 'GET',
      headers: this.getHeaders(),
    })
    
    console.log('📡 [ApiClient.verifyTokenFast] Response status:', response.status)
    return this.handleResponse<{ valid: boolean; user_id?: string; email?: string }>(response)
  }

  // Metadata APIs - 直接使用Supabase
  async createMetadata(data: MetadataEntry): Promise<ApiResponse<any>> {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      // 获取用户的profile_id
      const { data: profile } = await supabase
        .from('user_profile')
        .select('id')
        .eq('auth_user_id', user.id)
        .single()

      if (!profile) throw new Error('User profile not found')

      // 检查是否已存在相同的metadata
      const { data: existing } = await supabase
        .from('user_metadata')
        .select('id')
        .eq('user_id', profile.id)
        .eq('section_type', data.section_type)
        .eq('section_key', data.section_key)
        .single()

      if (existing) {
        // 更新现有记录
        const { data: updated, error } = await supabase
          .from('user_metadata')
          .update({
            content: data.content,
            data_type: data.data_type || 'nested_object',
            display_order: data.display_order || 1,
            updated_at: new Date().toISOString()
          })
          .eq('id', existing.id)
          .select()
          .single()

        if (error) throw error

        return {
          success: true,
          message: 'Metadata updated successfully',
          data: updated
        }
      } else {
        // 创建新记录
        const { data: created, error } = await supabase
          .from('user_metadata')
          .insert({
            user_id: profile.id,
            section_type: data.section_type,
            section_key: data.section_key,
            content: data.content,
            data_type: data.data_type || 'nested_object',
            display_order: data.display_order || 1
          })
          .select()
          .single()

        if (error) throw error

        return {
          success: true,
          message: 'Metadata created successfully',
          data: created
        }
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  async getUserMetadata(): Promise<MetadataResponse> {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      // 获取用户的profile_id
      const { data: profile } = await supabase
        .from('user_profile')
        .select('id')
        .eq('auth_user_id', user.id)
        .single()

      if (!profile) throw new Error('User profile not found')

      // 获取所有metadata
      const { data: metadata, error } = await supabase
        .from('user_metadata')
        .select('*')
        .eq('user_id', profile.id)
        .eq('is_active', true)
        .order('section_type')
        .order('display_order')

      if (error) throw error

      // 组织数据结构
      const organizedData: any = {}
      
      if (metadata) {
        metadata.forEach((item: any) => {
          if (!organizedData[item.section_type]) {
            organizedData[item.section_type] = {}
          }
          
          organizedData[item.section_type][item.section_key] = {
            content: item.content,
            data_type: item.data_type,
            display_order: item.display_order,
            created_at: item.created_at,
            updated_at: item.updated_at
          }
        })
      }

      return {
        success: true,
        data: organizedData
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message,
        data: {}
      }
    }
  }

  async batchUpdateMetadata(data: { metadata_entries: MetadataEntry[] }): Promise<ApiResponse<any>> {
    console.log('🔄 [ApiClient.batchUpdateMetadata] Starting batch metadata update...')
    console.log('📝 [ApiClient.batchUpdateMetadata] Entries count:', data.metadata_entries.length)
    
    const headers = await this.getSupabaseHeaders()
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/metadata/batch`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(data),
    })
    
    console.log('📡 [ApiClient.batchUpdateMetadata] Response status:', response.status)
    console.log('📡 [ApiClient.batchUpdateMetadata] Response ok:', response.ok)
    
    return this.handleResponse<ApiResponse<any>>(response)
  }

  async updateProfile(profileData: any): Promise<ApiResponse<any>> {
    console.log('🔄 [ApiClient.updateProfile] Starting profile update...')
    console.log('📝 [ApiClient.updateProfile] Profile data:', profileData)
    
    const headers = await this.getSupabaseHeaders()
    console.log('📋 [ApiClient.updateProfile] Request headers:', headers)
    
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/users/me/profile`, {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(profileData),
    })
    
    console.log('📡 [ApiClient.updateProfile] Response status:', response.status)
    console.log('📡 [ApiClient.updateProfile] Response ok:', response.ok)
    
    return this.handleResponse<ApiResponse<any>>(response)
  }

  async getBackendUserMetadata(): Promise<MetadataResponse> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/users/me/profile`, {
      method: 'GET',
      headers: await this.getSupabaseHeaders(),
    })
    
    return this.handleResponse<MetadataResponse>(response)
  }

  // Tags APIs - 生成标签使用后端API，获取标签使用Supabase
  async generateTags(data: GenerateTagsRequest): Promise<GenerateTagsResponse> {
    console.log('🚀 [ApiClient.generateTags] Starting tag generation request...')
    console.log('📝 [ApiClient.generateTags] Request data:', data)
    
    const headers = await this.getSupabaseHeaders()
    const headerObj = headers as Record<string, string>
    console.log('🔑 [ApiClient.generateTags] Request headers:', {
      hasAuth: !!headerObj['Authorization'],
      authType: headerObj['Authorization']?.substring(0, 20) + '...',
      contentType: headerObj['Content-Type']
    })
    
    console.log('🌐 [ApiClient.generateTags] Making request to:', `${this.baseUrl}/api/tags/generate`)
    
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/tags/generate`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(data),
    })
    
    console.log('📡 [ApiClient.generateTags] Response status:', response.status)
    console.log('📡 [ApiClient.generateTags] Response ok:', response.ok)
    
    const result = await this.handleResponse<GenerateTagsResponse>(response)
    console.log('📊 [ApiClient.generateTags] Parsed result:', {
      success: result.success,
      message: result.message,
      dataExists: !!result.data,
      tagsCount: result.data?.generated_tags?.length || 0
    })
    
    return result
  }

  async addManualTags(data: ManualTagsRequest): Promise<ApiResponse<UserTag[]>> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/tags/manual`, {
      method: 'POST',
      headers: await this.getSupabaseHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<ApiResponse<UserTag[]>>(response)
  }

  async getUserTags(): Promise<ApiResponse<UserTag[]>> {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      // 获取用户的profile_id
      const { data: profile } = await supabase
        .from('user_profile')
        .select('id')
        .eq('auth_user_id', user.id)
        .single()

      if (!profile) throw new Error('User profile not found')

      // 获取用户标签
      const { data: tags, error } = await supabase
        .from('user_tags')
        .select('*')
        .eq('user_id', profile.id)
        .eq('is_active', true)
        .order('confidence_score', { ascending: false })

      if (error) throw error

      // 转换为前端需要的格式
      const formattedTags: UserTag[] = (tags || []).map((tag: any) => ({
        id: tag.id,
        user_id: tag.user_id,
        tag_name: tag.tag_name,
        tag_category: tag.tag_category || 'generated',
        confidence_score: parseFloat(tag.confidence_score || 0),
        tag_source: tag.tag_source,
        created_at: tag.created_at,
        is_active: tag.is_active
      }))

      return {
        success: true,
        data: formattedTags
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message,
        data: []
      }
    }
  }

  // Matching APIs - 使用后端API进行AI匹配
  async searchMatches(data: MatchSearchRequest): Promise<MatchSearchResponse> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/match/search`, {
      method: 'POST',
      headers: await this.getSupabaseHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<MatchSearchResponse>(response)
  }

  async analyzeCompatibility(data: CompatibilityAnalysisRequest): Promise<CompatibilityAnalysisResponse> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/match/analyze`, {
      method: 'POST',
      headers: await this.getSupabaseHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<CompatibilityAnalysisResponse>(response)
  }

  // System APIs
  async healthCheck(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/system/health`, {
      method: 'GET',
      headers: this.getHeaders(),
    })
    
    return this.handleResponse<any>(response)
  }

  async getSystemStats(): Promise<ApiResponse<any>> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/system/stats`, {
      method: 'GET',
      headers: await this.getSupabaseHeaders(),
    })
    
    return this.handleResponse<ApiResponse<any>>(response)
  }
}

// Create a singleton instance
export const apiClient = new ApiClient()
  
  // 新的基于后端API的认证工具函数
export const auth = {
  login: async (email: string, password: string) => {
    try {
      const response = await apiClient.login({
        email: email.trim(),
        password
      })
      
      if (response.success && response.data) {
        return {
          success: true,
          message: response.message,
          data: {
            user_id: response.data.user_id,
            email: response.data.email,
            display_name: response.data.display_name,
            avatar_url: response.data.avatar_url,
            subscription_type: response.data.subscription_type,
            created_at: response.data.created_at,
            updated_at: response.data.updated_at,
            last_login_at: response.data.last_login_at,
            is_active: response.data.is_active,
            token: response.data.token
          }
        }
      }
      
      return {
        success: false,
        message: response.message || '登录失败',
        data: null
      }
    } catch (error: any) {
      console.error('Login error:', error)
      
      let errorMessage = error.message || '登录失败'
      
      // 处理网络错误
      if (error.message && error.message.includes('NetworkError')) {
        errorMessage = '网络错误，请检查网络连接'
      } else if (error.message && error.message.includes('timeout')) {
        errorMessage = '连接超时，请检查网络设置'
      } else if (error.message && error.message.includes('fetch')) {
        errorMessage = '无法连接到服务器，请检查后端服务是否启动'
      }
      
      return {
        success: false,
        message: errorMessage,
        data: null
      }
    }
  },
  
  register: async (email: string, password: string, displayName: string, avatarUrl?: string) => {
    try {
      const response = await apiClient.register({
        email: email.trim(),
        password,
        display_name: displayName.trim(),
        avatar_url: avatarUrl
      })
      
      if (response.success && response.data) {
        return {
          success: true,
          message: response.message,
          data: {
            user_id: response.data.user_id,
            email: response.data.email,
            display_name: response.data.display_name,
            avatar_url: response.data.avatar_url,
            subscription_type: response.data.subscription_type,
            created_at: response.data.created_at,
            updated_at: response.data.updated_at,
            last_login_at: response.data.last_login_at,
            is_active: response.data.is_active,
            token: response.data.token
          }
        }
      }
      
      return {
        success: false,
        message: response.message || '注册失败',
        data: null
      }
    } catch (error: any) {
      console.error('Registration error:', error)
      
      let errorMessage = error.message || '注册失败'
      
      // 处理网络错误
      if (error.message && error.message.includes('NetworkError')) {
        errorMessage = '网络错误，请检查网络连接'
      } else if (error.message && error.message.includes('timeout')) {
        errorMessage = '连接超时，请检查网络设置'
      } else if (error.message && error.message.includes('fetch')) {
        errorMessage = '无法连接到服务器，请检查后端服务是否启动'
      }
      
      return {
        success: false,
        message: errorMessage,
        data: null
      }
    }
  },
  
  logout: async () => {
    try {
      // 清除本地存储的token
      apiClient.clearToken()
      return { success: true, message: '登出成功' }
    } catch (error: any) {
      return { success: false, message: error.message || '登出失败' }
    }
  },
  
  // 快速验证token - 只检查有效性，不返回完整用户数据
  verifyTokenFast: async () => {
    console.log('⚡ [auth.verifyTokenFast] Starting fast verification...')
    try {
      const response = await apiClient.verifyTokenFast()
      console.log('📥 [auth.verifyTokenFast] Fast verification response:', response)
      
      return {
        success: response.valid,
        data: response.valid ? {
          user_id: response.user_id,
          email: response.email
        } : null
      }
    } catch (error: any) {
      console.error('💥 [auth.verifyTokenFast] Fast verification failed:', error)
      
      // 如果是401错误，自动清除认证状态
      if (error.message && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
        console.log('🧹 [auth.verifyTokenFast] Auto-clearing auth state due to 401 error')
        apiClient.clearToken()
        
        if (typeof window !== 'undefined') {
          try {
            const { useAppStore } = await import('@/lib/store')
            useAppStore.getState().logout()
          } catch (storeError) {
            console.error('❌ [auth.verifyTokenFast] Failed to clear store state:', storeError)
          }
        }
      }
      
      return {
        success: false,
        message: error.message || '快速验证失败'
      }
    }
  },
  
  getCurrentUser: async () => {
    console.log('🌐 [auth.getCurrentUser] Starting API call...')
    try {
      console.log('🔄 [auth.getCurrentUser] Calling backend API...')
      const response = await apiClient.getCurrentUser()
      console.log('📥 [auth.getCurrentUser] Raw API response:', response)
      
      if (response.success && response.data) {
        console.log('✅ [auth.getCurrentUser] API call successful')
        console.log('📋 [auth.getCurrentUser] User data:', response.data)
        return {
          success: true,
          data: {
            user_id: response.data.user_id,
            email: response.data.email,
            display_name: response.data.display_name,
            avatar_url: response.data.avatar_url,
            subscription_type: response.data.subscription_type,
            created_at: response.data.created_at,
            updated_at: response.data.updated_at,
            last_login_at: response.data.last_login_at || new Date().toISOString(),
            is_active: response.data.is_active
          }
        }
      }
      
      console.log('❌ [auth.getCurrentUser] API call failed:', response.message)
      return {
        success: false,
        message: response.message || '获取用户信息失败',
        data: null
      }
    } catch (error: any) {
      console.error('💥 [auth.getCurrentUser] Exception occurred:', error)
      console.error('💥 [auth.getCurrentUser] Error stack:', error.stack)
      
      let errorMessage = error.message || '获取用户信息失败'
      
      // 处理网络错误
      if (error.message && error.message.includes('NetworkError')) {
        errorMessage = '网络错误，请检查网络连接'
        console.log('🌐 [auth.getCurrentUser] Network error detected')
      } else if (error.message && error.message.includes('timeout')) {
        errorMessage = '连接超时，请检查网络设置'
        console.log('⏰ [auth.getCurrentUser] Timeout error detected')
      } else if (error.message && error.message.includes('fetch')) {
        errorMessage = '无法连接到服务器，请检查后端服务是否启动'
        console.log('🔌 [auth.getCurrentUser] Fetch error detected')
      } else if (error.message && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
        errorMessage = '登录已过期，请重新登录'
        console.log('🔐 [auth.getCurrentUser] Authorization error detected')
        
        // 自动清除认证状态
        console.log('🧹 [auth.getCurrentUser] Auto-clearing auth state due to 401 error')
        apiClient.clearToken()
        
        // 清除store中的认证状态
        if (typeof window !== 'undefined') {
          try {
            const { useAppStore } = await import('@/lib/store')
            useAppStore.getState().logout()
            console.log('✅ [auth.getCurrentUser] Store auth state cleared')
          } catch (storeError) {
            console.error('❌ [auth.getCurrentUser] Failed to clear store state:', storeError)
          }
        }
      }
      
      console.log('❌ [auth.getCurrentUser] Final error message:', errorMessage)
      return {
        success: false,
        message: errorMessage,
        data: null
      }
    }
  }
}

// Profile API object
export const profile = {
  getMetadata: () => apiClient.getUserMetadata(), // 直接从Supabase获取
  getBackendMetadata: () => apiClient.getBackendUserMetadata(), // 从后端API获取
  createMetadata: (data: MetadataEntry) => apiClient.createMetadata(data),
  batchUpdateMetadata: (entries: MetadataEntry[]) => apiClient.batchUpdateMetadata({ metadata_entries: entries }),
  updateProfile: (profileData: any) => apiClient.updateProfile(profileData),
}

export const tags = {
  generate: (requestType: '找队友' | '找对象') => {
    return apiClient.generateTags({ request_type: requestType })
  },
  
  addManual: (tagList: string[]) => {
    return apiClient.addManualTags({ tags: tagList })
  },
  
  getUserTags: () => {
    return apiClient.getUserTags()
  }
}

export const matching = {
  search: (description: string, tags: string[], matchType: '找队友' | '找对象', limit = 10) => {
    return apiClient.searchMatches({ description, tags, match_type: matchType, limit })
  },
  
  analyze: (targetUserId: string) => {
    return apiClient.analyzeCompatibility({ target_user_id: targetUserId })
  }
}

export default apiClient