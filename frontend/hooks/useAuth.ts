import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'
import { auth } from '@/lib/api'

export function useAuth() {
  const { 
    isAuthenticated, 
    authToken, 
    backendUser,
    setAuthToken,
    setIsAuthenticated,
    logout
  } = useAppStore()

  return {
    isAuthenticated,
    authToken,
    backendUser,
    setAuthToken,
    setIsAuthenticated,
    logout
  }
}

// Custom hook to handle hydration safely
export function useHydration() {
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    // Mark as hydrated after initial client-side render
    const timer = setTimeout(() => {
      setIsHydrated(true)
    }, 0)

    return () => clearTimeout(timer)
  }, [])

  return isHydrated
}

// Hook to safely access store values after hydration
export function useStoreValue<T>(selector: (state: any) => T, fallback: T): T {
  const isHydrated = useHydration()
  const value = useAppStore(selector)
  
  return isHydrated ? value : fallback
}

export function useRequireAuth() {
  console.log('🔐 [useRequireAuth] Called')
  return useAuth(true)
}

export function useOptionalAuth() {
  console.log('🔓 [useOptionalAuth] Called')
  return useAuth(false)
}