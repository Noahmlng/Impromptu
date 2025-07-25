'use client'

import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { Heart, Users } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ModeSwitcher() {
  const { themeMode, setThemeMode } = useAppStore()

  return (
    <div className="fixed left-6 top-1/2 z-50 -translate-y-1/2">
      <div className="flex flex-col space-y-2 rounded-full bg-background/80 p-2 shadow-lg backdrop-blur-sm border">
        <Button
          variant={themeMode === 'romantic' ? 'default' : 'ghost'}
          size="icon"
          onClick={() => setThemeMode('romantic')}
          className={cn(
            "h-12 w-12 rounded-full",
            themeMode === 'romantic' && "bg-romantic-pink-500 hover:bg-romantic-pink-600"
          )}
        >
          <Heart className="h-5 w-5" />
        </Button>
        
        <Button
          variant={themeMode === 'team' ? 'default' : 'ghost'}
          size="icon"
          onClick={() => setThemeMode('team')}
          className={cn(
            "h-12 w-12 rounded-full",
            themeMode === 'team' && "bg-miami-blue-500 hover:bg-miami-blue-600"
          )}
        >
          <Users className="h-5 w-5" />
        </Button>
      </div>
    </div>
  )
} 