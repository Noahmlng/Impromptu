'use client'

import { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'

export function StoreInitializer() {
  const [isClient, setIsClient] = useState(false)
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    // Mark as client-side after hydration
    setIsClient(true)
    
    // Small delay to ensure store is fully hydrated
    const timer = setTimeout(() => {
      setIsHydrated(true)
    }, 50)

    return () => clearTimeout(timer)
  }, [])

  // Expose hydration state globally
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__STORE_HYDRATED__ = isHydrated
    }
  }, [isHydrated])

  // This component doesn't render anything, it just initializes the store
  return null
} 