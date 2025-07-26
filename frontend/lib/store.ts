import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AppState, User, ThemeMode, Language, BackendUserInfo, UserTag, UserMetadata } from './types'

interface ExtendedAppState extends AppState {
  // Auth state
  isAuthenticated: boolean
  authToken: string | null
  backendUser: BackendUserInfo | null
  
  // User data
  userTags: UserTag[]
  userMetadata: Record<string, any>
  
  // Loading states
  isLoading: boolean
  isAuthLoading: boolean
  
  // Error handling
  error: string | null
  
  // Auth actions
  setAuthToken: (token: string | null) => void
  setBackendUser: (user: BackendUserInfo | null) => void
  setIsAuthenticated: (authenticated: boolean) => void
  
  // User data actions
  setUserTags: (tags: UserTag[]) => void
  setUserMetadata: (metadata: Record<string, any>) => void
  
  // Loading actions
  setIsLoading: (loading: boolean) => void
  setIsAuthLoading: (loading: boolean) => void
  
  // Error actions
  setError: (error: string | null) => void
  clearError: () => void
  
  // Combined actions
  logout: () => void
}

export const useAppStore = create<ExtendedAppState>()(
  persist(
    (set, get) => ({
      // Basic app state
      themeMode: 'romantic',
      isDarkMode: false,
      language: 'en',
      user: null,
      
      // Auth state
      isAuthenticated: false,
      authToken: null,
      backendUser: null,
      
      // User data
      userTags: [],
      userMetadata: {},
      
      // Loading states (不持久化)
      isLoading: false,
      isAuthLoading: false,
      
      // Error handling (不持久化)
      error: null,
      
      // Basic actions
      setThemeMode: (mode) => set({ themeMode: mode }),
      setIsDarkMode: (isDark) => set({ isDarkMode: isDark }),
      setLanguage: (lang) => set({ language: lang }),
      setUser: (user) => set({ user }),
      
      // Auth actions
      setAuthToken: (token) => {
        console.log('🏪 [Store] setAuthToken called with:', token ? 'TOKEN_SET' : 'TOKEN_CLEARED')
        set({ 
          authToken: token, 
          isAuthenticated: !!token 
        })
      },
      setBackendUser: (user) => {
        console.log('🏪 [Store] setBackendUser called with:', user ? user.email : 'USER_CLEARED')
        console.log('🏪 [Store] User data:', user)
        set({ 
          backendUser: user, 
          isAuthenticated: !!user 
        })
      },
      setIsAuthenticated: (authenticated) => {
        console.log('🏪 [Store] setIsAuthenticated called with:', authenticated)
        set({ isAuthenticated: authenticated })
      },
      
      // User data actions
      setUserTags: (tags) => set({ userTags: tags }),
      setUserMetadata: (metadata) => set({ userMetadata: metadata }),
      
      // Loading actions
      setIsLoading: (loading) => set({ isLoading: loading }),
      setIsAuthLoading: (loading) => set({ isAuthLoading: loading }),
      
      // Error actions
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
      
      // Combined actions
      logout: () => {
        console.log('🚪 [Store] logout called - clearing all auth state')
        set({
          user: null,
          isAuthenticated: false,
          authToken: null,
          backendUser: null,
          userTags: [],
          userMetadata: {},
          error: null
        })
        console.log('🚪 [Store] Auth state cleared')
      }
    }),
    {
      name: 'linker-auth-storage', // 存储key
      partialize: (state) => ({
        // 只持久化认证相关和用户数据，不持久化loading和error状态
        authToken: state.authToken,
        backendUser: state.backendUser,
        isAuthenticated: state.isAuthenticated,
        userTags: state.userTags,
        userMetadata: state.userMetadata,
        themeMode: state.themeMode,
        isDarkMode: state.isDarkMode,
        language: state.language,
        user: state.user
      })
    }
  )
) 