'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useAppStore } from '@/lib/store'
import { Heart, Users, Moon, Sun, Globe, Crown, Coins } from 'lucide-react'
import { useTheme } from 'next-themes'

export function Navbar() {
  const { themeMode, language, user, setLanguage } = useAppStore()
  const { theme, setTheme } = useTheme()

  const toggleLanguage = () => {
    setLanguage(language === 'zh' ? 'en' : 'zh')
  }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            {themeMode === 'romantic' ? (
              <Heart className="h-8 w-8 text-romantic-pink-500" />
            ) : (
              <Users className="h-8 w-8 text-miami-blue-500" />
            )}
            <span className="text-xl font-bold">Impromptu</span>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {/* Language Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleLanguage}
              className="h-9 w-9"
            >
              <Globe className="h-4 w-4" />
              <span className="sr-only">Toggle language</span>
            </Button>

            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="h-9 w-9"
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
              <span className="sr-only">Toggle theme</span>
            </Button>

            {/* User Profile */}
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.avatar} alt={user.name} />
                      <AvatarFallback>{user.name?.charAt(0) || 'U'}</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user.name}</p>
                      <div className="flex items-center space-x-2 text-xs leading-none text-muted-foreground">
                        <Crown className="h-3 w-3" />
                        <span className="capitalize">{user.subscription || 'free'}</span>
                      </div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="flex items-center">
                    <Coins className="mr-2 h-4 w-4" />
                    <span>{language === 'zh' ? '积分余额' : 'Credits'}: {user.credits || 0}</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Crown className="mr-2 h-4 w-4" />
                    <span>{language === 'zh' ? '订阅 Basic' : 'Subscribe Basic'}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Crown className="mr-2 h-4 w-4" />
                    <span>{language === 'zh' ? '订阅 Pro' : 'Subscribe Pro'}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Crown className="mr-2 h-4 w-4" />
                    <span>{language === 'zh' ? '订阅 Max' : 'Subscribe Max'}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button size="sm">
                {language === 'zh' ? '登录' : 'Login'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
} 