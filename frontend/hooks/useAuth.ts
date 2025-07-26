import { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'
import { auth } from '@/lib/api'
import { supabase } from '@/lib/supabase'

export function useAuth(requireAuth: boolean = true) {
  const router = useRouter()
  const {
    authToken,
    backendUser,
    setBackendUser,
    setUser,
    setAuthToken,
    setIsAuthLoading,
    setError,
    logout
  } = useAppStore()
  
  const isInitialized = useRef(false)

  useEffect(() => {
    const checkAuth = async () => {
      // 避免重复初始化
      if (isInitialized.current) return
      
      setIsAuthLoading(true)
      
      try {
        // 优先检查store中的持久化状态
        if (authToken && backendUser) {
          console.log('Using persisted auth state:', backendUser.email)
          setIsAuthLoading(false)
          isInitialized.current = true
          return
        }

        console.log('No persisted auth state, checking Supabase session...')
        
        // 检查Supabase session作为备用
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Session check error:', error)
          if (requireAuth) {
            router.push('/login')
          }
          setIsAuthLoading(false)
          isInitialized.current = true
          return
        }
        
        if (session?.user) {
          console.log('Found Supabase session, fetching user profile...')
          // 有有效session但store中没有用户信息，尝试获取用户档案
          try {
            const response = await auth.getCurrentUser()
            
            if (response.success && response.data) {
              console.log('Successfully fetched user profile:', response.data.email)
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
              console.error('Failed to fetch user profile:', response.message)
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
          console.log('No session and no stored auth, redirecting to login...')
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
        isInitialized.current = true
      }
    }

    // 监听认证状态变化（主要处理登出事件）
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        
        if (event === 'SIGNED_OUT') {
          // 用户登出，清除所有状态
          logout()
          isInitialized.current = false
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
  }, [requireAuth]) // 移除authToken和backendUser的依赖，避免循环

  const handleLogout = async () => {
    try {
      await auth.logout()
      await supabase.auth.signOut()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      logout() // 清除store状态
      isInitialized.current = false
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