// API Client for Comprehensive Matching System
import { supabase } from './supabase'
import { MatchUser } from './types'

// Base URL for the backend API (only for AI operations like tag generation and matching)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5003'

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
    token: string
  }
}

export interface UserInfo {
  user_id: string
  email: string
  display_name: string
  avatar_url?: string
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
  data: MatchUser[]
  total: number
  query: MatchSearchRequest
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

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    console.log('API Client initialized with base URL:', this.baseUrl)
    // Try to get token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token')
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
    
    // 从Supabase获取当前session的token
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`
    }
    
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
      
      throw new Error(errorMessage)
    }
    
    return response.json()
  }

  public setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
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
    const response = await fetch(`${this.baseUrl}/api/auth/register`, {
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
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
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

  async getCurrentUser(): Promise<ApiResponse<UserInfo>> {
    const response = await fetch(`${this.baseUrl}/api/auth/user`, {
      method: 'GET',
      headers: await this.getSupabaseHeaders(),
    })
    
    return this.handleResponse<ApiResponse<UserInfo>>(response)
  }

  // Metadata APIs - 直接使用Supabase
  async createMetadata(data: MetadataEntry): Promise<ApiResponse<any>> {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      // 获取用户的user_id
      const { data: profile } = await supabase
        .from('user_profile')
        .select('user_id')
        .eq('auth_user_id', user.id)
        .single()

      if (!profile) throw new Error('User profile not found')

      // 检查是否已存在相同的metadata
      const { data: existing } = await supabase
        .from('user_metadata')
        .select('id')
        .eq('user_id', profile.user_id)
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
            user_id: profile.user_id,
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

      // 获取用户的user_id
      const { data: profile } = await supabase
        .from('user_profile')
        .select('user_id')
        .eq('auth_user_id', user.id)
        .single()

      if (!profile) throw new Error('User profile not found')

      // 获取所有metadata
      const { data: metadata, error } = await supabase
        .from('user_metadata')
        .select('*')
        .eq('user_id', profile.user_id)
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
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      // 获取用户的user_id
      const { data: profile } = await supabase
        .from('user_profile')
        .select('user_id')
        .eq('auth_user_id', user.id)
        .single()

      if (!profile) throw new Error('User profile not found')

      const results = []
      const errors = []

      for (const entry of data.metadata_entries) {
        try {
          const result = await this.createMetadata(entry)
          if (result.success) {
            results.push(result.data)
          } else {
            errors.push({ entry, error: result.error })
          }
        } catch (error: any) {
          errors.push({ entry, error: error.message })
        }
      }

      return {
        success: true,
        message: `Successfully processed ${results.length} entries`,
        data: {
          success_count: results.length,
          error_count: errors.length,
          results,
          errors
        }
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  // Tags APIs - 生成标签使用后端API，获取标签使用Supabase
  async generateTags(data: GenerateTagsRequest): Promise<GenerateTagsResponse> {
    const response = await fetch(`${this.baseUrl}/api/tags/generate`, {
      method: 'POST',
      headers: await this.getSupabaseHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<GenerateTagsResponse>(response)
  }

  async addManualTags(data: ManualTagsRequest): Promise<ApiResponse<UserTag[]>> {
    const response = await fetch(`${this.baseUrl}/api/tags/manual`, {
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

      // 获取用户的user_id
      const { data: profile } = await supabase
        .from('user_profile')
        .select('user_id')
        .eq('auth_user_id', user.id)
        .single()

      if (!profile) throw new Error('User profile not found')

      // 获取用户标签
      const { data: tags, error } = await supabase
        .from('user_tags')
        .select('*')
        .eq('user_id', profile.user_id)
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
    const response = await fetch(`${this.baseUrl}/api/match/search`, {
      method: 'POST',
      headers: await this.getSupabaseHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<MatchSearchResponse>(response)
  }

  async analyzeCompatibility(data: CompatibilityAnalysisRequest): Promise<CompatibilityAnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/api/match/analyze`, {
      method: 'POST',
      headers: await this.getSupabaseHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<CompatibilityAnalysisResponse>(response)
  }

  // System APIs
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/system/health`, {
      method: 'GET',
      headers: this.getHeaders(),
    })
    
    return this.handleResponse<any>(response)
  }

  async getSystemStats(): Promise<ApiResponse<any>> {
    const response = await fetch(`${this.baseUrl}/api/system/stats`, {
      method: 'GET',
      headers: await this.getSupabaseHeaders(),
    })
    
    return this.handleResponse<ApiResponse<any>>(response)
  }
}

// Create a singleton instance
export const apiClient = new ApiClient()

// 新的基于Supabase Auth的认证工具函数
export const auth = {
  login: async (email: string, password: string) => {
    try {
      // 添加超时控制
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('登录请求超时，请检查网络连接')), 30000)
      })

      const signInPromise = supabase.auth.signInWithPassword({
        email,
        password,
      })

      const { data, error } = await Promise.race([signInPromise, timeoutPromise]) as any
      
      if (error) {
        let errorMessage = '登录失败';
        
        if (error.message.includes('Invalid login credentials')) {
          errorMessage = '邮箱或密码错误';
        } else if (error.message.includes('Email not confirmed')) {
          errorMessage = '请先确认邮箱，检查收件箱并点击确认链接';
        } else if (error.message.includes('rate limit') || error.message.includes('429')) {
          errorMessage = '登录请求过于频繁，请稍后再试';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        throw new Error(errorMessage);
      }
      
      if (data.user && data.session) {
        // 获取用户档案信息
        try {
          const { data: profile, error: profileError } = await supabase
            .from('user_profile')
            .select('*')
            .eq('auth_user_id', data.user.id)
            .single()
          
          return {
            success: true,
            message: '登录成功',
            data: {
              user_id: profile?.user_id || data.user.id,
              email: data.user.email!,
              display_name: profile?.display_name || data.user.user_metadata?.display_name,
              avatar_url: profile?.avatar_url || data.user.user_metadata?.avatar_url,
              subscription_type: profile?.subscription_type || 'free',
              token: data.session.access_token
            }
          }
        } catch (profileError: any) {
          console.error('Error fetching user profile:', profileError)
          // 即使获取档案失败，也返回基本的登录信息
          return {
            success: true,
            message: '登录成功',
            data: {
              user_id: data.user.id,
              email: data.user.email!,
              display_name: data.user.user_metadata?.display_name || '用户',
              avatar_url: data.user.user_metadata?.avatar_url,
              subscription_type: 'free',
              token: data.session.access_token
            }
          }
        }
      }
      
      throw new Error('登录失败')
    } catch (error: any) {
      console.error('Login error:', error)
      return {
        success: false,
        message: error.message || '登录失败',
        data: null
      }
    }
  },
  
  register: async (email: string, password: string, displayName: string, avatarUrl?: string) => {
    try {
      // 添加超时控制
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('注册请求超时，请检查网络连接')), 30000)
      })

      const signUpPromise = supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            display_name: displayName,
            avatar_url: avatarUrl
          }
        }
      })

      const { data, error } = await Promise.race([signUpPromise, timeoutPromise]) as any
      
      if (error) {
        // Handle specific error cases with better Chinese messages
        let errorMessage = '注册失败';
        
        if (error.message.includes('rate limit') || error.message.includes('429')) {
          errorMessage = '注册请求过于频繁，请稍后再试';
        } else if (error.message.includes('User already registered')) {
          errorMessage = '该邮箱已被注册，请使用其他邮箱或登录';
        } else if (error.message.includes('Password should')) {
          errorMessage = '密码至少需要6个字符';
        } else if (error.message.includes('Invalid email')) {
          errorMessage = '邮箱格式不正确';
        } else if (error.message.includes('confirmation')) {
          errorMessage = '注册成功！请检查邮箱并点击确认链接完成注册';
        } else if (error.message.includes('Error sending confirmation email')) {
          errorMessage = '注册成功！但由于邮件服务暂时不可用，请稍后检查邮箱或联系管理员';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        throw new Error(errorMessage);
      }
      
      if (data.user) {
        // 创建用户档案记录
        try {
          const userId = `user_${Date.now()}`
          const { data: profile, error: profileError } = await supabase
            .from('user_profile')
            .insert({
              user_id: userId,
              auth_user_id: data.user.id,
              email: data.user.email!,
              display_name: displayName,
              avatar_url: avatarUrl,
              status: 'active',
              subscription_type: 'free'
            })
            .select()
            .single()

          if (profileError) {
            console.error('Error creating user profile:', profileError)
            // 不阻塞注册，但记录错误
          }

          // 检查是否需要邮箱确认
          const needsConfirmation = !data.user.email_confirmed_at
          const message = needsConfirmation 
            ? '注册成功！请检查邮箱并点击确认链接完成注册。如果未收到邮件，请检查垃圾邮件文件夹。'
            : '注册成功！'

          return {
            success: true,
            message: message,
            data: {
              user_id: userId,
              email: data.user.email!,
              display_name: displayName,
              avatar_url: avatarUrl,
              token: data.session?.access_token || null,
              needs_confirmation: needsConfirmation
            }
          }
        } catch (profileError: any) {
          console.error('Error creating user profile:', profileError)
          // 返回基本的注册成功信息，即使profile创建失败
          const needsConfirmation = !data.user.email_confirmed_at
          const message = needsConfirmation 
            ? '注册成功！请检查邮箱并点击确认链接完成注册。如果未收到邮件，请检查垃圾邮件文件夹。'
            : '注册成功！'

          return {
            success: true,
            message: message,
            data: {
              user_id: data.user.id,
              email: data.user.email!,
              display_name: displayName,
              avatar_url: avatarUrl,
              token: data.session?.access_token || null,
              needs_confirmation: needsConfirmation
            }
          }
        }
      }
      
      throw new Error('注册失败')
    } catch (error: any) {
      console.error('Registration error:', error)
      return {
        success: false,
        message: error.message || '注册失败',
        data: null
      }
    }
  },
  
  logout: async () => {
    try {
      await supabase.auth.signOut()
      // 清除本地存储的token
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
      }
      return { success: true, message: '登出成功' }
    } catch (error: any) {
      return { success: false, message: error.message || '登出失败' }
    }
  },
  
  getCurrentUser: async () => {
    try {
      const { data: { user }, error } = await supabase.auth.getUser()
      
      if (error) throw error
      if (!user) throw new Error('用户未登录')
      
      // 获取用户档案信息
      const { data: profile, error: profileError } = await supabase
        .from('user_profile')
        .select('*')
        .eq('auth_user_id', user.id)
        .single()
      
      if (profileError) throw profileError
      
      return {
        success: true,
        data: {
          user_id: profile.user_id,
          email: user.email!,
          display_name: profile.display_name,
          avatar_url: profile.avatar_url,
          subscription_type: profile.subscription_type,
          created_at: profile.created_at,
          updated_at: profile.updated_at,
          is_active: profile.is_active
        }
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '获取用户信息失败',
        data: null
      }
    }
  }
}

export const profile = {
  updateMetadata: (sectionType: string, sectionKey: string, content: any) => {
    return apiClient.createMetadata({ section_type: sectionType, section_key: sectionKey, content })
  },
  
  getMetadata: () => {
    return apiClient.getUserMetadata()
  },
  
  batchUpdateMetadata: (entries: MetadataEntry[]) => {
    return apiClient.batchUpdateMetadata({ metadata_entries: entries })
  }
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