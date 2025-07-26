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
  const hydrationAttempts = useRef(0)
  const maxHydrationAttempts = 20 // 最多等待2秒 (20 * 100ms)

  // 等待 zustand persist 状态恢复，添加超时机制
  useEffect(() => {
    console.log('💧 [useAuth] Checking hydration status...')
    
    // 检查是否已经从 localStorage 恢复状态
    const checkHydration = () => {
      hydrationAttempts.current++
      
      // 检查是否在客户端环境
      if (typeof window === 'undefined') {
        console.log('💧 [useAuth] Server side, not hydrated yet')
        return
      }
      
      // 检查是否已经超过最大尝试次数
      if (hydrationAttempts.current > maxHydrationAttempts) {
        console.log('⏰ [useAuth] Hydration timeout, proceeding anyway')
        setIsHydrated(true)
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
      if (hasTokenInStorage && !hasStateData && hydrationAttempts.current <= maxHydrationAttempts) {
        console.log(`💧 [useAuth] Store not hydrated yet, waiting... (attempt ${hydrationAttempts.current}/${maxHydrationAttempts})`)
        return
      }
      
      console.log('💧 [useAuth] Setting hydrated to: true')
      setIsHydrated(true)
    }

    // 立即检查一次
    checkHydration()
    
    // 如果还没有恢复，等待一小段时间再检查
    if (!isHydrated && hydrationAttempts.current <= maxHydrationAttempts) {
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
      
      // 对于可选认证模式，如果没有token，直接结束loading状态
      if (!requireAuth && !authToken && !backendUser) {
        console.log('ℹ️ [useAuth] Optional auth mode and no auth state found, skipping verification')
        setIsAuthLoading(false)
        isInitialized.current = true
        return
      }
      
      setIsAuthLoading(true)
      
      try {
        // 检查store中的持久化状态
        if (authToken && backendUser) {
          console.log('✅ [useAuth] Found persisted auth state for:', backendUser.email)
          
          // 先使用快速验证检查token是否仍然有效（不查询数据库，速度更快）
          try {
            console.log('⚡ [useAuth] Performing fast token validation...')
            
            // 使用快速验证，只检查JWT token有效性
            const fastVerificationPromise = auth.verifyTokenFast()
            const timeoutPromise = new Promise((_, reject) => {
              setTimeout(() => reject(new Error('Fast verification timeout')), 3000) // 缩短超时时间到3秒
            })
            
            const fastResponse = await Promise.race([
              fastVerificationPromise,
              timeoutPromise
            ]) as any
            
            console.log('📥 [useAuth] Fast verification response:', fastResponse)
            
            if (fastResponse.success) {
              // 快速验证成功，token有效
              console.log('✅ [useAuth] Fast verification successful, token is valid')
              
              // 如果用户数据比较旧（超过1小时），在后台更新用户信息（不阻塞UI）
              const userDataAge = backendUser.last_login_at ? 
                Date.now() - new Date(backendUser.last_login_at).getTime() : 
                Infinity
              
              if (userDataAge > 60 * 60 * 1000) { // 1小时
                console.log('🔄 [useAuth] User data is old, refreshing in background...')
                
                // 后台刷新用户数据，不等待结果
                auth.getCurrentUser().then(fullResponse => {
                  if (fullResponse.success && fullResponse.data) {
                    console.log('✅ [useAuth] Background user data refresh successful')
                    setBackendUser(fullResponse.data)
                  }
                }).catch(err => {
                  console.warn('⚠️ [useAuth] Background user data refresh failed:', err)
                })
              }
              
              // 直接继续，不需要完整的用户数据验证
            } else {
              // 快速验证失败，token无效
              console.log('❌ [useAuth] Fast verification failed, clearing auth state')
              logout()
              
              if (requireAuth) {
                console.log('🔄 [useAuth] Redirecting to login (fast verification failed)')
                router.push('/login')
              }
            }
          } catch (error: any) {
            console.error('❌ [useAuth] Fast verification error:', error)
            
            // 对于可选认证模式，验证失败时不应该阻塞用户
            if (!requireAuth) {
              console.log('ℹ️ [useAuth] Optional auth mode - verification failed but allowing access')
              logout() // 清除无效的认证状态
              // 不跳转到登录页面
            } else {
              // 检查是否是超时错误
              if (error.message && error.message.includes('timeout')) {
                console.log('⏰ [useAuth] Fast verification timeout, falling back to full verification')
                
                // 快速验证超时，回退到完整验证（但有更短的超时时间）
                try {
                  const fullVerificationPromise = auth.getCurrentUser()
                  const shortTimeoutPromise = new Promise((_, reject) => {
                    setTimeout(() => reject(new Error('Full verification timeout')), 5000) // 5秒超时
                  })
                  
                  const response = await Promise.race([
                    fullVerificationPromise,
                    shortTimeoutPromise
                  ]) as any
                  
                  if (response.success && response.data) {
                    console.log('✅ [useAuth] Fallback verification successful')
                    setBackendUser(response.data)
                  } else {
                    console.log('❌ [useAuth] Fallback verification failed')
                    logout()
                    router.push('/login')
                  }
                } catch (fallbackError: any) {
                  console.error('❌ [useAuth] Fallback verification also failed:', fallbackError)
                  logout()
                  router.push('/login')
                }
              } else {
                // 其他错误，清除认证状态
                logout()
                router.push('/login')
              }
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
        
        // 对于可选认证模式，即使出错也应该允许访问
        if (!requireAuth) {
          console.log('ℹ️ [useAuth] Optional auth mode - error occurred but allowing access')
          logout() // 清除可能有问题的认证状态
          // 不显示错误信息，不跳转到登录页面
        } else {
          // 提供更具体的错误信息
          let errorMessage = '认证检查失败'
          if (error?.message) {
            if (error.message.includes('Network') || error.message.includes('网络')) {
              errorMessage = '网络连接失败，请检查网络设置'
            } else if (error.message.includes('timeout') || error.message.includes('超时')) {
              errorMessage = '连接超时，请稍后重试'
            } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
              errorMessage = '登录已过期，正在跳转到登录页面'
            } else if (error.message.includes('500')) {
              errorMessage = '服务器错误，请稍后重试'
            }
          }
          
          setError(errorMessage)
          
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