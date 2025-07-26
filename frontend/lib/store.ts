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
      language: 'zh',
      user: null,
      
      // Auth state
      isAuthenticated: false,
      authToken: null,
      backendUser: null,
      
      // User data
      userTags: [],
      userMetadata: {},
      
      // Loading states (not persisted)
      isLoading: false,
      isAuthLoading: false,
      
      // Error handling (not persisted)
      error: null,
      
      // Basic actions
      setThemeMode: (mode) => set({ themeMode: mode }),
      setIsDarkMode: (isDark) => set({ isDarkMode: isDark }),
      setLanguage: (lang) => set({ language: lang }),
      setUser: (user) => set({ user }),
      
      // Auth actions
      setAuthToken: (token) => set({ 
        authToken: token, 
        isAuthenticated: !!token 
      }),
      setBackendUser: (user) => set({ 
        backendUser: user, 
        isAuthenticated: !!user 
      }),
      setIsAuthenticated: (authenticated) => set({ isAuthenticated: authenticated }),
      
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
      logout: () => set({
        user: null,
        isAuthenticated: false,
        authToken: null,
        backendUser: null,
        userTags: [],
        userMetadata: {},
        error: null
      }),
    }),
    {
      name: 'linker-app-storage',
      partialize: (state) => ({
        // Only persist these fields
        themeMode: state.themeMode,
        isDarkMode: state.isDarkMode,
        language: state.language,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        authToken: state.authToken,
        backendUser: state.backendUser,
        userTags: state.userTags,
        userMetadata: state.userMetadata,
      }),
    }
  )
) 