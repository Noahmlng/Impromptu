import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'
import { auth } from '@/lib/api'
import { supabase } from '@/lib/supabase'

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
      setIsAuthLoading(true)
      
      try {
        // 首先检查store中是否已有认证信息（来自登录页面）
        if (authToken && backendUser) {
          setIsAuthLoading(false)
          return
        }

        // 然后检查Supabase session
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Session check error:', error)
          if (requireAuth) {
            router.push('/login')
          }
          return
        }
        
        if (session?.user) {
          // 有有效session，获取用户档案信息
          const response = await auth.getCurrentUser()
          
          if (response.success && response.data) {
            // 更新state
            setAuthToken(session.access_token)
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
            // 用户档案获取失败，清除session
            await supabase.auth.signOut()
            logout()
            if (requireAuth) {
              router.push('/login')
            }
          }
        } else if (requireAuth) {
          // 没有session也没有后端token，但需要认证
          router.push('/login')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        if (requireAuth) {
          router.push('/login')
        }
      } finally {
        setIsAuthLoading(false)
      }
    }

    // 监听认证状态变化
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        
        if (event === 'SIGNED_IN' && session?.user) {
          // 用户登录
          const response = await auth.getCurrentUser()
          if (response.success && response.data) {
            setAuthToken(session.access_token)
            setBackendUser(response.data)
            setUser({
              id: response.data.user_id,
              name: response.data.display_name,
              email: response.data.email,
              avatar: response.data.avatar_url,
              credits: 0,
              subscription: 'free'
            })
          }
        } else if (event === 'SIGNED_OUT') {
          // 用户登出
          logout()
          if (requireAuth) {
            router.push('/login')
          }
        }
      }
    )

    checkAuth()

    // 清理订阅
    return () => {
      subscription.unsubscribe()
    }
  }, [requireAuth, router, setAuthToken, setBackendUser, setUser, setIsAuthLoading, logout, authToken, backendUser])

  const handleLogout = async () => {
    await auth.logout()
    logout()
    router.push('/login')
  }

  return {
    isAuthenticated: isAuthenticated || !!(authToken && backendUser),
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