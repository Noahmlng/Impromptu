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
import SubscribeModal from './SubscribeModal'

export function Navbar() {
  const { themeMode, language, user, setLanguage } = useAppStore()
  const { theme, setTheme } = useTheme()
  const [showSubscribeModal, setShowSubscribeModal] = useState(false)
  const [isPending, setIsPending] = useState(false)

  const toggleLanguage = () => {
    setLanguage(language === 'zh' ? 'en' : 'zh')
  }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  // 翻译对象
  const t = {
    subscription: {
      title: language === 'zh' ? '选择订阅计划' : 'Choose Subscription Plan',
      plan: language === 'zh' ? '订阅计划' : 'Subscription Plans',
      addon: language === 'zh' ? '附加服务' : 'Add-ons',
      earlyBird: language === 'zh' ? '早鸟' : 'Early Bird',
      bestValue: language === 'zh' ? '最超值' : 'Best Value',
      currentPlan: language === 'zh' ? '当前计划' : 'Current Plan',
      subscribe: language === 'zh' ? '立即订阅' : 'Subscribe Now',
      newUserGift: language === 'zh' ? '新用户礼品' : 'New User Gift',
      validForMonth: language === 'zh' ? '有效期一个月' : 'Valid for 1 month'
    }
  }

  // 订阅计划数据
  const subscriptionPlans = [
    {
      id: 'free',
      name: language === 'zh' ? '免费计划' : 'Free Plan',
      originalPrice: 0,
      price: 0,
      coins: language === 'zh' ? '100 积分' : '100 Credits',
      isPopular: false,
      isEarlyBird: false,
      features: [
        language === 'zh' ? '基础匹配功能' : 'Basic matching features',
        language === 'zh' ? '每日3次匹配' : '3 matches per day',
        language === 'zh' ? '标准客服支持' : 'Standard support'
      ]
    },
    {
      id: 'basic',
      name: language === 'zh' ? '基础计划' : 'Basic Plan',
      originalPrice: 19,
      price: 9,
      coins: language === 'zh' ? '500 积分' : '500 Credits',
      isPopular: false,
      isEarlyBird: true,
      features: [
        language === 'zh' ? '无限匹配' : 'Unlimited matches',
        language === 'zh' ? '高级筛选' : 'Advanced filters',
        language === 'zh' ? '优先客服支持' : 'Priority support',
        language === 'zh' ? '匹配分析报告' : 'Match analysis reports'
      ]
    },
    {
      id: 'pro',
      name: language === 'zh' ? '专业计划' : 'Pro Plan',
      originalPrice: 39,
      price: 19,
      coins: language === 'zh' ? '1200 积分' : '1200 Credits',
      isPopular: true,
      isEarlyBird: false,
      features: [
        language === 'zh' ? '所有基础功能' : 'All Basic features',
        language === 'zh' ? 'AI深度分析' : 'AI deep analysis',
        language === 'zh' ? '个性化推荐' : 'Personalized recommendations',
        language === 'zh' ? '专属客服' : 'Dedicated support',
        language === 'zh' ? '高级隐私设置' : 'Advanced privacy settings'
      ]
    },
    {
      id: 'max',
      name: language === 'zh' ? '至尊计划' : 'Max Plan',
      originalPrice: 79,
      price: 39,
      coins: language === 'zh' ? '3000 积分' : '3000 Credits',
      isPopular: false,
      isEarlyBird: false,
      features: [
        language === 'zh' ? '所有专业功能' : 'All Pro features',
        language === 'zh' ? '无限AI分析' : 'Unlimited AI analysis',
        language === 'zh' ? '专属匹配顾问' : 'Personal match consultant',
        language === 'zh' ? '优先匹配权限' : 'Priority matching',
        language === 'zh' ? '定制化服务' : 'Custom services'
      ]
    }
  ]

  const handleSubscribe = async (planId: string) => {
    setIsPending(true)
    try {
      // 这里实现订阅逻辑
      console.log('Subscribing to plan:', planId)
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000))
      setShowSubscribeModal(false)
    } catch (error) {
      console.error('Subscription failed:', error)
    } finally {
      setIsPending(false)
    }
  }

  return (
    <>
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
              <span className="text-xl font-bold">Linker</span>
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
                    <DropdownMenuItem onClick={() => setShowSubscribeModal(true)}>
                      <Crown className="mr-2 h-4 w-4" />
                      <span>{language === 'zh' ? '管理订阅' : 'Manage Subscription'}</span>
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

      <SubscribeModal
        show={showSubscribeModal}
        onClose={() => setShowSubscribeModal(false)}
        subscriptionPlans={subscriptionPlans}
        onSubscribe={handleSubscribe}
        isPending={isPending}
        t={t}
      />
    </>
  )
} 