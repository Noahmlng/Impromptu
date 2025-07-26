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
        // 优先检查store中是否已有认证信息（来自登录页面设置）
        if (authToken && backendUser) {
          // Store中有完整的用户信息，直接使用
          setIsAuthLoading(false)
          return
        }

        // 如果store中没有信息，检查Supabase session作为备用
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Session check error:', error)
          if (requireAuth) {
            router.push('/login')
          }
          setIsAuthLoading(false)
          return
        }
        
        if (session?.user) {
          // 有有效session但store中没有用户信息，尝试获取用户档案
          try {
            const response = await auth.getCurrentUser()
            
            if (response.success && response.data) {
              // 更新store state，确保与登录时的逻辑一致
              setAuthToken(session.access_token)
              setBackendUser(response.data)
              setUser({
                id: response.data.user_id,
                name: response.data.display_name,
                email: response.data.email,
                avatar: response.data.avatar_url,
                credits: 0,
                subscription: response.data.subscription_type || 'free'
              })
            } else {
              // 用户档案获取失败，清除session
              await supabase.auth.signOut()
              logout()
              if (requireAuth) {
                router.push('/login')
              }
            }
          } catch (error) {
            console.error('Failed to get user profile:', error)
            await supabase.auth.signOut()
            logout()
            if (requireAuth) {
              router.push('/login')
            }
          }
        } else if (requireAuth) {
          // 没有session也没有store中的认证信息，但需要认证
          router.push('/login')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        setError('认证检查失败')
        if (requireAuth) {
          router.push('/login')
        }
      } finally {
        setIsAuthLoading(false)
      }
    }

    // 监听认证状态变化（主要处理登出事件）
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        
        if (event === 'SIGNED_OUT') {
          // 用户登出，清除所有状态
          logout()
          if (requireAuth) {
            router.push('/login')
          }
        }
        // 注意：不在这里处理SIGNED_IN事件，因为我们优先使用store中的状态
      }
    )

    checkAuth()

    // 清理订阅
    return () => {
      subscription.unsubscribe()
    }
  }, [requireAuth, router, setAuthToken, setBackendUser, setUser, setIsAuthLoading, logout, authToken, backendUser])

  const handleLogout = async () => {
    try {
      await auth.logout()
      await supabase.auth.signOut()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      logout() // 清除store状态
      router.push('/login')
    }
  }

  return {
    isAuthenticated: !!(authToken && backendUser), // 明确基于store状态判断
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