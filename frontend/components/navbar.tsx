'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
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
import { useOptionalAuth } from '@/hooks/useAuth'
import { Heart, Users, Moon, Sun, Globe, Crown, Coins, LogOut } from 'lucide-react'
import { useTheme } from 'next-themes'
import SubscribeModal from './SubscribeModal'

export function Navbar() {
  const { themeMode, language, user, setLanguage } = useAppStore()
  const { theme, setTheme } = useTheme()
  const { logout } = useOptionalAuth()
  const router = useRouter()
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
            <a href="/" className="flex items-center cursor-pointer" style={{height: '64px', paddingTop: '8px', paddingBottom: '8px'}}>
              <span style={{display: 'inline-block', height: '48px', width: 'auto'}}>
                <svg width="96" height="36" viewBox="0 0 1292 507" fill="none" xmlns="http://www.w3.org/2000/svg" style={{height: '48px', width: 'auto'}}>
                  <path d="M268.07 30.8866C204.27 101.316 147.27 175.614 92.2696 260.292C21.8696 369.194 -7.13037 435.349 1.46963 468.121C5.86963 484.609 19.4696 499.265 35.8696 504.558C46.6696 508.222 80.0696 507.611 98.4696 503.743C137.47 495.398 183.07 476.264 268.47 432.499C319.47 406.241 376.87 374.893 400.87 360.034L407.07 356.166L406.87 366.548C406.47 375.504 407.27 377.54 412.07 381.814C418.47 387.31 426.47 388.125 436.07 383.85C439.67 382.425 457.87 366.344 476.47 348.228C495.27 330.112 516.07 310.774 522.87 305.278L535.27 295.304L522.27 322.173C515.27 337.032 509.47 351.485 509.47 354.538C509.47 361.255 517.27 367.362 523.27 365.326C525.47 364.716 540.87 349.246 557.27 331.129C584.47 301.41 611.47 274.745 614.27 274.745C614.87 274.745 613.67 279.223 611.67 284.515C598.27 318.916 603.67 339.882 625.47 339.882C634.67 339.882 660.07 329.094 682.47 315.659C693.47 309.145 702.87 304.057 703.27 304.464C703.87 305.074 700.87 312.606 696.47 321.359C687.87 339.475 687.87 347.007 696.47 349.246C699.27 349.856 702.67 350.06 704.07 349.449C707.27 348.228 719.47 322.987 727.67 300.393C735.67 278.612 736.27 278.002 737.67 291.64C739.27 306.703 744.27 313.624 755.67 317.084C783.47 325.633 848.87 304.667 897.47 271.488L918.47 257.036L924.47 260.903C945.67 273.931 984.67 254.796 1031.47 207.775L1057.27 182.128L1058.27 189.252C1058.87 193.119 1059.47 204.315 1059.47 214.086C1059.47 229.352 1060.07 232.609 1063.47 236.069C1071.47 244.212 1077.07 240.344 1087.87 219.378C1111.67 172.764 1188.67 121.672 1268.67 99.4844C1286.07 94.8027 1291.47 91.1387 1291.47 84.4214C1291.47 72.4117 1279.07 72.6153 1241.47 85.4392C1182.27 105.591 1120.67 143.045 1090.67 177.649L1080.07 189.659L1078.87 176.021C1078.07 168.489 1076.27 160.144 1074.47 157.497C1070.67 151.594 1063.27 149.559 1057.27 152.612C1054.87 154.037 1040.07 168.286 1024.67 184.163C997.47 212.254 978.47 228.334 963.07 236.273C955.07 240.548 939.47 244.619 939.47 242.38C939.47 241.769 944.47 237.087 950.67 231.998C964.47 220.803 989.27 194.341 997.87 181.517C1002.27 174.8 1004.47 169.1 1005.07 161.976C1005.67 152.816 1005.27 150.984 1000.47 146.505C996.67 142.842 993.27 141.62 987.27 141.62C966.07 142.231 927.87 185.181 916.27 221.617L911.87 235.052L889.47 250.522C839.67 284.922 779.67 307.924 763.47 299.171C756.87 295.507 758.87 281.869 768.07 267.824C773.87 259.071 778.27 255.204 790.87 248.283C834.67 223.856 852.67 206.147 847.47 192.305C840.67 174.189 811.67 185.995 778.47 220.803C762.07 237.901 747.47 249.097 747.47 244.619C747.47 243.601 748.87 238.716 750.67 233.83C756.67 216.325 765.47 175.817 765.87 163.401C766.27 149.559 763.67 144.47 756.47 144.47C749.47 144.47 746.07 150.373 744.67 165.843C743.47 181.11 735.87 210.625 724.27 246.654L717.27 268.435L697.87 281.055C673.67 296.932 634.87 317.491 629.27 317.491C625.27 317.491 625.07 316.677 626.27 309.349C626.87 304.871 630.67 293.472 634.47 283.905C645.27 257.443 642.87 244.008 627.07 243.601C617.67 243.397 610.07 248.69 581.87 274.541L559.47 295.304L565.47 282.48C568.87 275.355 571.47 267.62 571.47 264.974C571.47 259.275 563.07 250.318 557.67 250.318C550.67 250.318 514.27 281.869 457.67 336.829C442.87 351.281 430.27 361.866 429.87 360.441C429.47 359.22 432.47 347.007 436.47 333.776C443.47 310.57 443.67 309.145 440.67 304.26C438.27 300.8 435.47 299.171 431.47 299.171C426.47 299.171 422.27 302.632 407.07 318.509C397.07 329.297 382.87 342.325 375.67 347.821C348.47 367.973 232.47 429.039 168.47 456.926C120.87 477.688 93.8696 485.016 64.2696 485.22C43.0696 485.424 41.8696 485.22 34.8696 479.724C19.0696 467.511 17.4696 456.315 27.4696 424.968C50.0696 352.706 168.27 174.596 265.07 66.5087C306.47 20.3018 309.47 16.6378 309.47 10.5312C309.47 7.47789 308.47 3.81392 307.07 2.38903C301.27 -3.51404 296.27 -0.0536177 268.07 30.8866ZM979.47 170.728C978.47 172.968 970.67 181.72 962.27 190.677C951.27 202.279 948.07 204.722 950.87 199.633C954.47 192.916 977.67 166.861 980.27 166.861C981.07 166.861 980.67 168.693 979.47 170.728Z" fill="currentColor"/>
                  <path d="M444.27 231.388C438.67 237.698 437.47 238.309 437.47 234.848C437.47 229.149 433.67 225.892 427.07 225.892C416.67 225.892 414.87 237.291 421.67 259.275C424.67 269.656 426.87 273.524 430.67 275.152C438.47 278.816 444.47 274.134 454.67 257.036C465.87 238.309 467.07 233.627 461.67 228.131C455.67 222.024 452.07 222.839 444.27 231.388Z" fill="currentColor"/>
                </svg>
              </span>
            </a>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-4">
              {/* Language Toggle */}
              <button
                onClick={toggleLanguage}
                className="h-9 w-9 rounded-full border flex items-center justify-center focus:outline-none bg-muted hover:bg-accent transition-colors"
                style={{minWidth: '2.25rem', minHeight: '2.25rem'}}
              >
                <span className="font-semibold text-sm">
                  {language === 'zh' ? 'En' : '中'}
                </span>
                <span className="sr-only">Toggle language</span>
              </button>

              {/* Theme Toggle */}
              <div className="flex items-center bg-muted rounded-full p-1 h-9 w-20 cursor-pointer select-none justify-between" onClick={toggleTheme}>
                <span className={`flex items-center justify-center h-7 w-7 transition-colors rounded-full ${theme === 'light' ? 'bg-background text-primary shadow' : 'text-muted-foreground'}`}> 
                  <Sun className="h-4 w-4" />
                </span>
                <span className={`flex items-center justify-center h-7 w-7 transition-colors rounded-full ${theme === 'dark' ? 'bg-background text-primary shadow' : 'text-muted-foreground'}`}> 
                  <Moon className="h-4 w-4" />
                </span>
              </div>

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
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logout} className="text-red-600 focus:text-red-600">
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>{language === 'zh' ? '退出登录' : 'Logout'}</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button size="sm" onClick={() => router.push('/login')}>
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