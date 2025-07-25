import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'
import { auth } from '@/lib/api'

export function useAuth(requireAuth: boolean = true) {
  const router = useRouter()
  const {
    isAuthenticated,
    authToken,
    backendUser,
    setBackendUser,
    setUser,
    setAuthToken,
    setIsAuthLoading,
    setError,
    logout
  } = useAppStore()

  useEffect(() => {
    const checkAuth = async () => {
      // Check if we have a token in localStorage
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      
      if (token && !isAuthenticated) {
        // We have a token but not authenticated, verify it
        setIsAuthLoading(true)
        try {
          const response = await auth.getCurrentUser()
          if (response.success && response.data) {
            // Token is valid, update state
            setAuthToken(token)
            setBackendUser(response.data)
            setUser({
              id: response.data.user_id,
              name: response.data.display_name,
              email: response.data.email,
              avatar: response.data.avatar_url,
              credits: 0,
              subscription: 'free'
            })
          } else {
            // Token is invalid, clear it
            logout()
            auth.logout()
          }
        } catch (error) {
          console.error('Auth check failed:', error)
          logout()
          auth.logout()
        } finally {
          setIsAuthLoading(false)
        }
      } else if (!token && requireAuth) {
        // No token and auth is required, redirect to login
        router.push('/login')
      }
    }

    checkAuth()
  }, [isAuthenticated, authToken, requireAuth, router, setAuthToken, setBackendUser, setUser, setIsAuthLoading, logout])

  const handleLogout = () => {
    logout()
    auth.logout()
    router.push('/login')
  }

  return {
    isAuthenticated,
    user: backendUser,
    logout: handleLogout,
    isLoading: useAppStore(state => state.isAuthLoading)
  }
}

export function useRequireAuth() {
  return useAuth(true)
}

export function useOptionalAuth() {
  return useAuth(false)
}