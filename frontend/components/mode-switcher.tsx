'use client'

import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { Heart, Award, User } from 'lucide-react'
import { cn } from '@/lib/utils'
import { usePathname, useRouter } from 'next/navigation'

export function ModeSwitcher() {
  const { themeMode, setThemeMode } = useAppStore()
  const pathname = usePathname()
  const router = useRouter()
  
  // Don't show ModeSwitcher on landing page and login/register pages
  const hiddenPages = ['/', '/login', '/register']
  if (hiddenPages.includes(pathname)) {
    return null
  }

  const handleProfileClick = () => {
    router.push('/profile')
  }

  const handleRomanticClick = () => {
    setThemeMode('romantic')
    router.push('/home')
  }

  const handleTeamClick = () => {
    setThemeMode('team')
    router.push('/home')
  }

  return (
    <div className="fixed left-6 top-1/2 z-50 -translate-y-1/2">
      <div className="flex flex-col space-y-2 rounded-full bg-background/80 p-2 shadow-lg backdrop-blur-sm border">
        <Button
          variant={pathname === '/profile' ? 'default' : 'ghost'}
          size="icon"
          onClick={handleProfileClick}
          className="h-12 w-12 rounded-full"
          title="Profile"
        >
          <User className="h-5 w-5" />
        </Button>
        
        <Button
          variant={themeMode === 'romantic' ? 'default' : 'ghost'}
          size="icon"
          onClick={handleRomanticClick}
          className={cn(
            "h-12 w-12 rounded-full",
            themeMode === 'romantic' && "bg-romantic-pink-500 hover:bg-romantic-pink-600"
          )}
          title="Love Mode"
        >
          <Heart className="h-5 w-5" />
        </Button>
        
        <Button
          variant={themeMode === 'team' ? 'default' : 'ghost'}
          size="icon"
          onClick={handleTeamClick}
          className={cn(
            "h-12 w-12 rounded-full",
            themeMode === 'team' && "bg-miami-blue-500 hover:bg-miami-blue-600"
          )}
          title="Team Mode"
        >
          <Award className="h-5 w-5" />
        </Button>
      </div>
    </div>
  )
} 