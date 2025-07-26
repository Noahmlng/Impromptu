import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'
import { auth } from '@/lib/api'

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
  const [isHydrated, setIsHydrated] = useState(false)

  // 等待 zustand persist 状态恢复
  useEffect(() => {
    console.log('💧 [useAuth] Checking hydration status...')
    
    // 检查是否已经从 localStorage 恢复状态
    const checkHydration = () => {
      // 检查是否在客户端环境
      if (typeof window === 'undefined') {
        console.log('💧 [useAuth] Server side, not hydrated yet')
        return
      }
      
      // 简单检查：直接检查 localStorage 中的存储
      const hasTokenInStorage = localStorage.getItem('linker-auth-storage')
      console.log('💧 [useAuth] hasTokenInStorage:', !!hasTokenInStorage)
      
      // 检查当前store状态是否有数据
      const currentState = useAppStore.getState()
      const hasStateData = currentState.authToken || currentState.backendUser
      console.log('💧 [useAuth] hasStateData:', !!hasStateData)
      
      // 如果localStorage有数据但store没有，说明还在恢复中
      if (hasTokenInStorage && !hasStateData) {
        console.log('💧 [useAuth] Store not hydrated yet, waiting...')
        return
      }
      
      console.log('💧 [useAuth] Setting hydrated to: true')
      setIsHydrated(true)
    }

    // 立即检查一次
    checkHydration()
    
    // 如果还没有恢复，等待一小段时间再检查
    if (!isHydrated) {
      const timeout = setTimeout(checkHydration, 100)
      return () => clearTimeout(timeout)
    }
  }, [isHydrated])

  useEffect(() => {
    // 只有在 hydration 完成后才进行认证检查
    if (!isHydrated) {
      console.log('💧 [useAuth] Waiting for hydration to complete...')
      return
    }

    const checkAuth = async () => {
      console.log('🔍 [useAuth] Starting auth check...')
      console.log('🔍 [useAuth] requireAuth:', requireAuth)
      console.log('🔍 [useAuth] authToken exists:', !!authToken)
      console.log('🔍 [useAuth] backendUser exists:', !!backendUser)
      console.log('🔍 [useAuth] backendUser data:', backendUser)
      console.log('🔍 [useAuth] isInitialized:', isInitialized.current)
      
      setIsAuthLoading(true)
      
      try {
        // 检查store中的持久化状态
        if (authToken && backendUser) {
          console.log('✅ [useAuth] Found persisted auth state for:', backendUser.email)
          
          // 验证token是否仍然有效
          try {
            console.log('🔄 [useAuth] Validating token with backend...')
            const response = await auth.getCurrentUser()
            console.log('📥 [useAuth] Backend response:', response)
            
            if (response.success && response.data) {
              // Token仍然有效，更新用户信息
              console.log('✅ [useAuth] Token valid, updating user info')
              setBackendUser(response.data)
              console.log('✅ [useAuth] Token verified and user info updated')
            } else {
              // Token无效，检查是否已经被getCurrentUser自动清除
              const currentState = useAppStore.getState()
              if (currentState.authToken || currentState.backendUser) {
                console.log('❌ [useAuth] Token invalid, clearing remaining auth state')
                console.log('❌ [useAuth] Response message:', response.message)
                logout()
              } else {
                console.log('ℹ️ [useAuth] Auth state already cleared by getCurrentUser')
              }
              
              if (requireAuth) {
                console.log('🔄 [useAuth] Redirecting to login (token invalid)')
                router.push('/login')
              }
            }
          } catch (error: any) {
            console.error('❌ [useAuth] Token validation failed:', error)
            
            // 检查是否是401错误，如果是，认证状态可能已经被getCurrentUser清除
            if (error?.message && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
              console.log('🔐 [useAuth] 401 error detected, checking if auth state was auto-cleared')
              const currentState = useAppStore.getState()
              if (currentState.authToken || currentState.backendUser) {
                console.log('🧹 [useAuth] Clearing remaining auth state after 401 error')
                logout()
              } else {
                console.log('✅ [useAuth] Auth state already cleared by error handler')
              }
            } else {
              // 其他错误，正常清除状态
              logout()
            }
            
            if (requireAuth) {
              console.log('🔄 [useAuth] Redirecting to login (validation error)')
              router.push('/login')
            }
          }
        } else if (requireAuth) {
          console.log('❌ [useAuth] No auth state found, requireAuth=true')
          console.log('🔄 [useAuth] Redirecting to login (no auth state)')
          router.push('/login')
        } else {
          console.log('ℹ️ [useAuth] No auth state found, but auth not required')
        }
      } catch (error: any) {
        console.error('❌ [useAuth] Auth check failed:', error)
        
        // 提供更具体的错误信息
        let errorMessage = '认证检查失败'
        if (error?.message) {
          if (error.message.includes('Network')) {
            errorMessage = '网络连接失败，请检查网络设置'
          } else if (error.message.includes('timeout')) {
            errorMessage = '连接超时，请稍后重试'
          } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            errorMessage = '登录已过期，正在跳转到登录页面'
          } else if (error.message.includes('500')) {
            errorMessage = '服务器错误，请稍后重试'
          }
        }
        
        setError(errorMessage)
        
        if (requireAuth) {
          console.log('🔄 [useAuth] Redirecting to login (auth check error)')
          // 对于401错误，立即跳转；其他错误延迟跳转给用户时间看到错误信息
          const delay = (error?.message && (error.message.includes('401') || error.message.includes('Unauthorized'))) ? 100 : 2000
          setTimeout(() => {
            router.push('/login')
          }, delay)
        }
      } finally {
        setIsAuthLoading(false)
        isInitialized.current = true
        console.log('🏁 [useAuth] Auth check completed')
      }
    }

    // 只在未初始化时执行检查
    if (!isInitialized.current) {
      checkAuth()
    } else {
      console.log('⏭️ [useAuth] Already initialized, skipping auth check')
    }
  }, [requireAuth, authToken, backendUser, isHydrated]) // 添加 isHydrated 依赖

  const handleLogout = async () => {
    console.log('🚪 [useAuth] Logout initiated')
    try {
      await auth.logout()
    } catch (error) {
      console.error('❌ [useAuth] Logout error:', error)
    } finally {
      logout() // 清除store状态
      isInitialized.current = false
      console.log('🔄 [useAuth] Redirecting to login (logout)')
      router.push('/login')
    }
  }

  console.log('🔍 [useAuth] Current state:', {
    isAuthenticated: !!(authToken && backendUser),
    hasUser: !!backendUser,
    isLoading: useAppStore.getState().isAuthLoading,
    isHydrated
  })

  return {
    isAuthenticated: !!(authToken && backendUser), // 明确基于store状态判断
    user: backendUser,
    logout: handleLogout,
    isLoading: useAppStore(state => state.isAuthLoading) || !isHydrated // 在hydration完成前也显示loading
  }
}

export function useRequireAuth() {
  console.log('🔐 [useRequireAuth] Called')
  return useAuth(true)
}

export function useOptionalAuth() {
  console.log('🔓 [useOptionalAuth] Called')
  return useAuth(false)
}