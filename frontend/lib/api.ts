// API Client for Comprehensive Matching System
// Base URL for the backend API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5003'

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

export interface MatchUser {
  user_id: string
  display_name: string
  email: string
  avatar_url?: string
  match_score: number
  user_tags: string[]
  metadata_summary: any
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
    // Try to get token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token')
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
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
    const response = await fetch(`${this.baseUrl}/api/auth/me`, {
      method: 'GET',
      headers: this.getHeaders(),
    })
    
    return this.handleResponse<ApiResponse<UserInfo>>(response)
  }

  // Metadata APIs
  async createMetadata(data: MetadataEntry): Promise<ApiResponse<any>> {
    const response = await fetch(`${this.baseUrl}/api/profile/metadata`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<ApiResponse<any>>(response)
  }

  async getUserMetadata(): Promise<MetadataResponse> {
    const response = await fetch(`${this.baseUrl}/api/profile/metadata`, {
      method: 'GET',
      headers: this.getHeaders(),
    })
    
    return this.handleResponse<MetadataResponse>(response)
  }

  async batchUpdateMetadata(data: { metadata_entries: MetadataEntry[] }): Promise<ApiResponse<any>> {
    const response = await fetch(`${this.baseUrl}/api/profile/metadata/batch`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<ApiResponse<any>>(response)
  }

  // Tags APIs
  async generateTags(data: GenerateTagsRequest): Promise<GenerateTagsResponse> {
    const response = await fetch(`${this.baseUrl}/api/tags/generate`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<GenerateTagsResponse>(response)
  }

  async addManualTags(data: ManualTagsRequest): Promise<ApiResponse<UserTag[]>> {
    const response = await fetch(`${this.baseUrl}/api/tags/manual`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<ApiResponse<UserTag[]>>(response)
  }

  async getUserTags(): Promise<ApiResponse<UserTag[]>> {
    const response = await fetch(`${this.baseUrl}/api/tags/user`, {
      method: 'GET',
      headers: this.getHeaders(),
    })
    
    return this.handleResponse<ApiResponse<UserTag[]>>(response)
  }

  // Matching APIs
  async searchMatches(data: MatchSearchRequest): Promise<MatchSearchResponse> {
    const response = await fetch(`${this.baseUrl}/api/match/search`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    
    return this.handleResponse<MatchSearchResponse>(response)
  }

  async analyzeCompatibility(data: CompatibilityAnalysisRequest): Promise<CompatibilityAnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/api/match/analyze`, {
      method: 'POST',
      headers: this.getHeaders(),
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
      headers: this.getHeaders(),
    })
    
    return this.handleResponse<ApiResponse<any>>(response)
  }
}

// Create a singleton instance
export const apiClient = new ApiClient()

// Utility functions for common operations
export const auth = {
  login: async (email: string, password: string) => {
    return apiClient.login({ email, password })
  },
  
  register: async (email: string, password: string, displayName: string, avatarUrl?: string) => {
    return apiClient.register({ 
      email, 
      password, 
      display_name: displayName, 
      avatar_url: avatarUrl 
    })
  },
  
  logout: () => {
    apiClient.clearToken()
  },
  
  getCurrentUser: () => {
    return apiClient.getCurrentUser()
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