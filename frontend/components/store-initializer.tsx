'use client'

import { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'

export function StoreInitializer() {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    // Mark as client-side after hydration
    setIsClient(true)
  }, [])

  // This component doesn't render anything, it just initializes the store
  if (!isClient) {
    return null
  }

  return null
} 