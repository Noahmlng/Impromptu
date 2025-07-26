'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { useAppStore } from '@/lib/store'
import { useOptionalAuth } from '@/hooks/useAuth'
import { ScrollNavbar } from '@/components/scroll-navbar'
import { 
  Heart, 
  Users, 
  Brain, 
  Shield, 
  Zap, 
  Star,
  ArrowRight,
  Check,
  ChevronRight,
  Youtube,
  Linkedin,
  Instagram
} from 'lucide-react'

export default function LandingPage() {
  const { language } = useAppStore()
  const router = useRouter()
  const { isAuthenticated, isLoading } = useOptionalAuth()

  // 设置全局语言变量供嵌入的HTML使用
  useEffect(() => {
    if (typeof window !== 'undefined') {
      ;(window as any).chatLanguage = language
      // 如果聊天动画已经初始化，重新启动以应用新语言
      setTimeout(() => {
        if (typeof window !== 'undefined' && (window as any).restartChatAnimation) {
          (window as any).restartChatAnimation()
        }
      }, 100)
    }
  }, [language])

  // Redirect to /home if user is authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      // 立即跳转，不显示重定向消息
      router.replace('/home')
    }
  }, [isAuthenticated, isLoading, router])

  // 优化loading显示逻辑：只有在明确检查认证状态时才显示loading
  // 对于可选认证模式，不应该因为loading而阻塞页面显示
  if (isLoading && isAuthenticated) {
    // 只有在已认证但还在loading时才显示loading（准备跳转）
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">
            {language === 'zh' ? '正在跳转...' : 'Redirecting...'}
          </p>
        </div>
      </div>
    )
  }

  // 如果用户已认证但页面还没跳转，显示跳转提示
  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">
            {language === 'zh' ? '正在跳转...' : 'Redirecting...'}
          </p>
        </div>
      </div>
    )
  }

  // 对于未认证用户或loading状态下，直接显示landing page内容
  // 这确保了即使在loading时，用户也能看到页面内容

  const features = [
    {
      icon: Brain,
      title: language === 'zh' ? 'AI智能匹配' : 'AI Smart Matching',
      description: language === 'zh' 
        ? '运用先进的机器学习算法，基于性格、兴趣和价值观进行精准匹配'
        : 'Advanced ML algorithms for precise matching based on personality, interests, and values'
    },
    {
      icon: Heart,
      title: language === 'zh' ? '多维度分析' : 'Multi-dimensional Analysis',
      description: language === 'zh'
        ? '深度分析用户画像，从多个维度评估兼容性，提高匹配成功率'
        : 'Deep user profiling with multi-dimensional compatibility analysis for higher success rates'
    },
    {
      icon: Shield,
      title: language === 'zh' ? '隐私安全' : 'Privacy & Security',
      description: language === 'zh'
        ? '严格的隐私保护机制，确保用户信息安全，让您安心使用'
        : 'Strict privacy protection mechanisms ensuring user data security and peace of mind'
    },
    {
      icon: Zap,
      title: language === 'zh' ? '实时匹配' : 'Real-time Matching',
      description: language === 'zh'
        ? '快速响应，实时更新匹配结果，第一时间发现最佳候选'
        : 'Fast response with real-time matching updates to discover best candidates instantly'
    }
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: language === 'zh' ? '产品经理' : 'Product Manager',
      content: language === 'zh' 
        ? '通过Linker找到了完美的工作伙伴，团队合作效率提升了30%！'
        : 'Found the perfect work partner through Linker, our team efficiency increased by 30%!'
    },
    {
      name: 'Alex Wang',
      role: language === 'zh' ? '创业者' : 'Entrepreneur',
      content: language === 'zh'
        ? '匹配算法非常精准，为我的创业项目找到了理想的联合创始人。'
        : 'The matching algorithm is incredibly accurate, found my ideal co-founder for my startup.'
    },
    {
      name: 'Emily Zhang',
      role: language === 'zh' ? '设计师' : 'Designer',
      content: language === 'zh'
        ? '界面设计简洁美观，使用体验很棒，推荐给所有朋友！'
        : 'Clean and beautiful interface design, great user experience, recommended to all friends!'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* 滚动导航 */}
      <ScrollNavbar />
      
      {/* Hero Section */}
      <section id="hero" className="relative overflow-hidden" style={{ minHeight: '1200px' }}>
        {/* Background Image - 放在最上边 */}
        <div 
          className="absolute inset-0 bg-contain bg-no-repeat"
          style={{
            backgroundImage: `url('/bg.png')`,
            backgroundPosition: 'center top',
          }}
        />
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center">
            {/* Logo */}
            <div className="flex items-center justify-center mb-6 -mt-[70px]">
              <svg width="240" height="90" viewBox="0 0 1292 507" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style={{stopColor: '#2563eb'}}/>
                    <stop offset="50%" style={{stopColor: '#9333ea'}}/>
                    <stop offset="100%" style={{stopColor: '#ec4899'}}/>
                  </linearGradient>
                </defs>
                <path d="M268.07 30.8866C204.27 101.316 147.27 175.614 92.2696 260.292C21.8696 369.194 -7.13037 435.349 1.46963 468.121C5.86963 484.609 19.4696 499.265 35.8696 504.558C46.6696 508.222 80.0696 507.611 98.4696 503.743C137.47 495.398 183.07 476.264 268.47 432.499C319.47 406.241 376.87 374.893 400.87 360.034L407.07 356.166L406.87 366.548C406.47 375.504 407.27 377.54 412.07 381.814C418.47 387.31 426.47 388.125 436.07 383.85C439.67 382.425 457.87 366.344 476.47 348.228C495.27 330.112 516.07 310.774 522.87 305.278L535.27 295.304L522.27 322.173C515.27 337.032 509.47 351.485 509.47 354.538C509.47 361.255 517.27 367.362 523.27 365.326C525.47 364.716 540.87 349.246 557.27 331.129C584.47 301.41 611.47 274.745 614.27 274.745C614.87 274.745 613.67 279.223 611.67 284.515C598.27 318.916 603.67 339.882 625.47 339.882C634.67 339.882 660.07 329.094 682.47 315.659C693.47 309.145 702.87 304.057 703.27 304.464C703.87 305.074 700.87 312.606 696.47 321.359C687.87 339.475 687.87 347.007 696.47 349.246C699.27 349.856 702.67 350.06 704.07 349.449C707.27 348.228 719.47 322.987 727.67 300.393C735.67 278.612 736.27 278.002 737.67 291.64C739.27 306.703 744.27 313.624 755.67 317.084C783.47 325.633 848.87 304.667 897.47 271.488L918.47 257.036L924.47 260.903C945.67 273.931 984.67 254.796 1031.47 207.775L1057.27 182.128L1058.27 189.252C1058.87 193.119 1059.47 204.315 1059.47 214.086C1059.47 229.352 1060.07 232.609 1063.47 236.069C1071.47 244.212 1077.07 240.344 1087.87 219.378C1111.67 172.764 1188.67 121.672 1268.67 99.4844C1286.07 94.8027 1291.47 91.1387 1291.47 84.4214C1291.47 72.4117 1279.07 72.6153 1241.47 85.4392C1182.27 105.591 1120.67 143.045 1090.67 177.649L1080.07 189.659L1078.87 176.021C1078.07 168.489 1076.27 160.144 1074.47 157.497C1070.67 151.594 1063.27 149.559 1057.27 152.612C1054.87 154.037 1040.07 168.286 1024.67 184.163C997.47 212.254 978.47 228.334 963.07 236.273C955.07 240.548 939.47 244.619 939.47 242.38C939.47 241.769 944.47 237.087 950.67 231.998C964.47 220.803 989.27 194.341 997.87 181.517C1002.27 174.8 1004.47 169.1 1005.07 161.976C1005.67 152.816 1005.27 150.984 1000.47 146.505C996.67 142.842 993.27 141.62 987.27 141.62C966.07 142.231 927.87 185.181 916.27 221.617L911.87 235.052L889.47 250.522C839.67 284.922 779.67 307.924 763.47 299.171C756.87 295.507 758.87 281.869 768.07 267.824C773.87 259.071 778.27 255.204 790.87 248.283C834.67 223.856 852.67 206.147 847.47 192.305C840.67 174.189 811.67 185.995 778.47 220.803C762.07 237.901 747.47 249.097 747.47 244.619C747.47 243.601 748.87 238.716 750.67 233.83C756.67 216.325 765.47 175.817 765.87 163.401C766.27 149.559 763.67 144.47 756.47 144.47C749.47 144.47 746.07 150.373 744.67 165.843C743.47 181.11 735.87 210.625 724.27 246.654L717.27 268.435L697.87 281.055C673.67 296.932 634.87 317.491 629.27 317.491C625.27 317.491 625.07 316.677 626.27 309.349C626.87 304.871 630.67 293.472 634.47 283.905C645.27 257.443 642.87 244.008 627.07 243.601C617.67 243.397 610.07 248.69 581.87 274.541L559.47 295.304L565.47 282.48C568.87 275.355 571.47 267.62 571.47 264.974C571.47 259.275 563.07 250.318 557.67 250.318C550.67 250.318 514.27 281.869 457.67 336.829C442.87 351.281 430.27 361.866 429.87 360.441C429.47 359.22 432.47 347.007 436.47 333.776C443.47 310.57 443.67 309.145 440.67 304.26C438.27 300.8 435.47 299.171 431.47 299.171C426.47 299.171 422.27 302.632 407.07 318.509C397.07 329.297 382.87 342.325 375.67 347.821C348.47 367.973 232.47 429.039 168.47 456.926C120.87 477.688 93.8696 485.016 64.2696 485.22C43.0696 485.424 41.8696 485.22 34.8696 479.724C19.0696 467.511 17.4696 456.315 27.4696 424.968C50.0696 352.706 168.27 174.596 265.07 66.5087C306.47 20.3018 309.47 16.6378 309.47 10.5312C309.47 7.47789 308.47 3.81392 307.07 2.38903C301.27 -3.51404 296.27 -0.0536177 268.07 30.8866ZM979.47 170.728C978.47 172.968 970.67 181.72 962.27 190.677C951.27 202.279 948.07 204.722 950.87 199.633C954.47 192.916 977.67 166.861 980.27 166.861C981.07 166.861 980.67 168.693 979.47 170.728Z" fill="url(#logoGradient)"/>
                <path d="M444.27 231.388C438.67 237.698 437.47 238.309 437.47 234.848C437.47 229.149 433.67 225.892 427.07 225.892C416.67 225.892 414.87 237.291 421.67 259.275C424.67 269.656 426.87 273.524 430.67 275.152C438.47 278.816 444.47 274.134 454.67 257.036C465.87 238.309 467.07 233.627 461.67 228.131C455.67 222.024 452.07 222.839 444.27 231.388Z" fill="url(#logoGradient)"/>
              </svg>
            </div>
            
            <div className="absolute bottom-[-450px] left-1/2 transform -translate-x-1/2 flex flex-col sm:flex-row gap-10 justify-center items-center">
              <Link href="/login">
                <Button size="lg" className="text-lg px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  {language === 'zh' ? '开始匹配' : 'Start Matching'}
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              
              <Link href="/home">
                <Button variant="outline" size="lg" className="text-lg px-8 py-4">
                  {language === 'zh' ? '了解更多' : 'Learn More'}
                  <ChevronRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
            
            {/* 介绍文字 - 在按钮下方 */}
            <div className="absolute bottom-[-750px] left-1/2 transform -translate-x-1/2 text-center">
              <p className="text-lg lg:text-xl text-gray-600 dark:text-gray-300 max-w-7xl mx-auto leading-relaxed font-montserrat">
                {language === 'zh' 
                  ? '通过AI驱动的智能匹配系统，为您找到最合适的伙伴。无论是工作合作、学习交流，还是生活陪伴，Linker都能为您精准匹配。'
                  : 'Find your perfect match through our AI-powered intelligent matching system. Whether for work collaboration, study partners, or life companions, Linker provides precise matching for you.'
                }
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white dark:bg-gray-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {language === 'zh' ? '为什么选择Linker？' : 'Why Choose Linker?'}
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              {language === 'zh'
                ? '我们提供最先进的匹配技术，帮助您找到最合适的伙伴'
                : 'We provide the most advanced matching technology to help you find the perfect partner'
              }
            </p>
          </div>

          {/* shadcn现代卡片布局 */}
          <div className="space-y-20">
            {/* 第一行：左图右文 */}
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-12 items-center">
              {/* 左侧：AI对话气泡 */}
              <div className="aspect-[4/3]">
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 h-full overflow-hidden shadow-lg" style={{boxShadow: '0 10px 25px rgba(59, 130, 246, 0.15)'}}>
                  {/* 嵌入的聊天动画 */}
                  <div 
                    className="w-full h-full"
                    dangerouslySetInnerHTML={{
                      __html: `
                        <style>
                          @font-face {
                            font-family: 'MiSans';
                            src: url('https://assets-persist.lovart.ai/agent-static-assets/MiSans-Regular.ttf') format('truetype');
                            font-weight: normal;
                            font-style: normal;
                          }
                          
                          @font-face {
                            font-family: 'MiSans';
                            src: url('https://assets-persist.lovart.ai/agent-static-assets/MiSans-Medium.ttf') format('truetype');
                            font-weight: 500;
                            font-style: normal;
                          }
                          
                          @font-face {
                            font-family: 'MiSans';
                            src: url('https://assets-persist.lovart.ai/agent-static-assets/MiSans-Bold.ttf') format('truetype');
                            font-weight: bold;
                            font-style: normal;
                          }
                          
                          .chat-animation-container {
                            font-family: 'MiSans', sans-serif;
                            width: 100%;
                            height: 100%;
                            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                            border-radius: 16px;
                            overflow: hidden;
                            display: flex;
                            flex-direction: column;
                            position: relative;
                          }
                          
                          .chat-animation-header {
                            padding: 16px 20px;
                            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                            color: white;
                            font-weight: 600;
                            font-size: 16px;
                            display: flex;
                            align-items: center;
                            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            z-index: 10;
                            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
                          }
                          
                          .chat-animation-header i {
                            margin-right: 12px;
                            font-size: 20px;
                            background: rgba(255, 255, 255, 0.2);
                            padding: 8px;
                            border-radius: 12px;
                          }
                          
                          .chat-animation-body {
                            flex: 1;
                            padding: 16px 20px;
                            padding-top: 80px;
                            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                            display: flex;
                            flex-direction: column;
                            position: relative;
                            overflow: hidden;
                            height: 100%;
                          }
                          
                          .chat-animation-message {
                            display: flex;
                            margin-bottom: 16px;
                            opacity: 0;
                            transform: translateY(20px);
                            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                            position: absolute;
                            width: calc(100% - 40px);
                          }
                          
                          .chat-animation-message.visible {
                            opacity: 1;
                            transform: translateY(0);
                          }
                          
                          .chat-animation-avatar {
                            width: 36px;
                            height: 36px;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin-right: 12px;
                            flex-shrink: 0;
                            font-size: 16px;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                          }
                          
                          .chat-animation-bot-avatar {
                            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                            color: white;
                            position: relative;
                            overflow: hidden;
                          }
                          
                          .chat-animation-bot-avatar::before {
                            content: '';
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            width: 20px;
                            height: 20px;
                            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A2.5 2.5 0 0 0 5 15.5A2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5a2.5 2.5 0 0 0 2.5 2.5a2.5 2.5 0 0 0 2.5-2.5a2.5 2.5 0 0 0-2.5-2.5"/></svg>') no-repeat center;
                            background-size: contain;
                            opacity: 0.9;
                          }
                          
                          .chat-animation-user-avatar {
                            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
                            color: white;
                            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>');
                            background-size: 60%;
                            background-repeat: no-repeat;
                            background-position: center;
                          }
                          
                          .chat-animation-message-content {
                            max-width: 75%;
                            padding: 14px 18px;
                            border-radius: 20px;
                            font-size: 14px;
                            line-height: 1.5;
                            position: relative;
                            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
                            font-weight: 500;
                          }
                          
                          .chat-animation-bot .chat-animation-message-content {
                            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                            color: white;
                            border-top-left-radius: 6px;
                            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
                          }
                          
                          .chat-animation-user {
                            flex-direction: row-reverse;
                            align-self: flex-end;
                          }
                          
                          .chat-animation-user .chat-animation-avatar {
                            margin-right: 0;
                            margin-left: 12px;
                          }
                          
                          .chat-animation-user .chat-animation-message-content {
                            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                            color: #1e293b;
                            border-top-right-radius: 6px;
                            border: 1px solid rgba(59, 130, 246, 0.1);
                            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
                          }
                          
                          .chat-animation-cursor {
                            display: inline-block;
                            width: 2px;
                            height: 18px;
                            background-color: currentColor;
                            margin-left: 3px;
                            vertical-align: middle;
                            animation: chat-animation-blink 1.2s infinite;
                            border-radius: 1px;
                          }
                          
                          @keyframes chat-animation-blink {
                            0%, 100% {
                              opacity: 1;
                            }
                            50% {
                              opacity: 0;
                            }
                          }
                          
                          /* 添加打字机效果的光晕 */
                          .chat-animation-message-content::after {
                            content: '';
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            border-radius: inherit;
                            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
                            opacity: 0;
                            transition: opacity 0.3s ease;
                          }
                          
                          .chat-animation-message.typing .chat-animation-message-content::after {
                            opacity: 1;
                          }
                          
                          .chat-animation-frame {
                            display: none;
                          }
                          
                          .chat-animation-frame.active {
                            display: block;
                          }
                          
                          .chat-animation-text-animation {
                            display: inline;
                          }
                          
                          /* 第一个对话中机器人消息向下移动20px */
                          #chat-frame1 .chat-animation-bot {
                            transform: translateY(20px);
                          }
                        </style>
                        
                        <div class="chat-animation-container">
                          <div class="chat-animation-header">
                            <i class="ri-message-3-line"></i>
                            ${language === 'zh' ? '你的身份是什么？' : "What's your identity?"}
                    </div>
                          <div class="chat-animation-body">
                            <!-- Frame 1 -->
                            <div class="chat-animation-frame" id="chat-frame1">
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                  </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-bot-text-1"></span>
                                  <span class="chat-animation-cursor"></span>
                    </div>
                    </div>
                              <div class="chat-animation-message chat-animation-user">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                  </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-user-text-1"></span>
                                  <span class="chat-animation-cursor"></span>
                  </div>
                              </div>
                            </div>
                            
                            <!-- Frame 2 -->
                            <div class="chat-animation-frame" id="chat-frame2">
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！我想更好地了解你。' : "Hi! I'd like to know you better."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！当然可以。' : "Hi! Sure."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-bot-text-2"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-user-text-2"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                            </div>
                            
                            <!-- Frame 3 -->
                            <div class="chat-animation-frame" id="chat-frame3">
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！我想更好地了解你。' : "Hi! I'd like to know you better."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！当然可以。' : "Hi! Sure."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '对你来说，什么是完美的一天？' : 'What would constitute a "perfect" day for you?'}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '和朋友在一起，享受美食和音乐的一天。' : "A day with friends, good food, and music."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-bot-text-3"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-user-text-3"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                            </div>
                            
                            <!-- Frame 4 -->
                            <div class="chat-animation-frame" id="chat-frame4">
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！我想更好地了解你。' : "Hi! I'd like to know you better."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！当然可以。' : "Hi! Sure."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '对你来说，什么是完美的一天？' : 'What would constitute a "perfect" day for you?'}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '和朋友在一起，享受美食和音乐的一天。' : "A day with friends, good food, and music."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '如果你明天醒来能获得任何一种品质或能力，你希望是什么？' : "If you could wake up tomorrow having gained any one quality or ability, what would it be?"}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '能够说所有语言的能力。' : "The ability to speak every language."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-bot-text-4"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-user-text-4"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                            </div>
                            
                            <!-- Frame 5 -->
                            <div class="chat-animation-frame" id="chat-frame5">
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！我想更好地了解你。' : "Hi! I'd like to know you better."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '你好！当然可以。' : "Hi! Sure."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '对你来说，什么是完美的一天？' : 'What would constitute a "perfect" day for you?'}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '和朋友在一起，享受美食和音乐的一天。' : "A day with friends, good food, and music."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '如果你明天醒来能获得任何一种品质或能力，你希望是什么？' : "If you could wake up tomorrow having gained any one quality or ability, what would it be?"}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '能够说所有语言的能力。' : "The ability to speak every language."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '在友谊中你最看重什么？' : "What do you value most in a friendship?"}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user visible">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span>${language === 'zh' ? '信任和诚实。' : "Trust and honesty."}</span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-bot visible">
                                <div class="chat-animation-avatar chat-animation-bot-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-bot-text-5"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                              <div class="chat-animation-message chat-animation-user">
                                <div class="chat-animation-avatar chat-animation-user-avatar">
                                </div>
                                <div class="chat-animation-message-content">
                                  <span class="chat-animation-text-animation" id="chat-user-text-5"></span>
                                  <span class="chat-animation-cursor"></span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <script>
                          // Get current language from parent component
                          const getCurrentLanguage = () => {
                            // Try to get language from parent React component
                            return window.chatLanguage || '${language}';
                          };
                          
                          // Text content for each frame - function to get current texts
                          const getChatFrameTexts = () => {
                            const lang = getCurrentLanguage();
                            return {
                              frame1: {
                                bot: lang === 'zh' ? "你好！我想更好地了解你。" : "Hi! I'd like to know you better.",
                                user: lang === 'zh' ? "你好！当然可以。" : "Hi! Sure."
                              },
                              frame2: {
                                bot: lang === 'zh' ? "对你来说，什么是完美的一天？" : 'What would constitute a "perfect" day for you?',
                                user: lang === 'zh' ? "和朋友在一起，享受美食和音乐的一天。" : "A day with friends, good food, and music."
                              },
                              frame3: {
                                bot: lang === 'zh' ? "如果你明天醒来能获得任何一种品质或能力，你希望是什么？" : "If you could wake up tomorrow having gained any one quality or ability, what would it be?",
                                user: lang === 'zh' ? "能够说所有语言的能力。" : "The ability to speak every language."
                              },
                              frame4: {
                                bot: lang === 'zh' ? "在友谊中你最看重什么？" : "What do you value most in a friendship?",
                                user: lang === 'zh' ? "信任和诚实。" : "Trust and honesty."
                              },
                              frame5: {
                                bot: lang === 'zh' ? "谢谢！我对你了解了很多。" : "Thanks! I'm learning a lot about you.",
                                user: "😊"
                              }
                            };
                          };

                          // Animation variables
                          let chatCurrentFrame = 1;
                          const chatTypingSpeed = 40; // ms per character
                          let chatAnimationInterval;
                          
                          // Initialize chat animation
                          function initChatAnimation() {
                            showChatFrame(chatCurrentFrame);
                            startChatAutoPlay();
                          }
                          
                          // Restart chat animation (for language changes)
                          function restartChatAnimation() {
                            // Clear existing interval
                            if (chatAnimationInterval) {
                              clearInterval(chatAnimationInterval);
                            }
                            // Update static texts first
                            updateStaticTexts();
                            // Reset to first frame
                            chatCurrentFrame = 1;
                            // Restart animation
                            initChatAnimation();
                          }
                          
                          // Make restart function globally available
                          window.restartChatAnimation = restartChatAnimation;
                          
                          // Show specific frame
                          function showChatFrame(frameNumber) {
                            // Hide all frames
                            document.querySelectorAll('.chat-animation-frame').forEach(frame => {
                              if (frame && frame.classList) {
                                frame.classList.remove('active');
                              }
                            });
                            
                            // Show current frame
                            const currentFrameElement = document.getElementById(\`chat-frame\${frameNumber}\`);
                            if (currentFrameElement && currentFrameElement.classList) {
                              currentFrameElement.classList.add('active');
                            }
                            
                            // Reset and start animations for the current frame
                            resetChatFrameAnimations(frameNumber);
                            startChatFrameAnimations(frameNumber);
                            
                            // Auto-scroll to show new messages with smooth animation
                            setTimeout(() => {
                              const bodyElement = document.querySelector('.chat-animation-body');
                              if (bodyElement) {
                                const scrollDistance = 120; // 增加滚动距离
                                const currentScroll = bodyElement.scrollTop;
                                const targetScroll = currentScroll + scrollDistance;
                                
                                // 平滑滚动动画
                                const scrollStep = () => {
                                  if (bodyElement.scrollTop < targetScroll) {
                                    bodyElement.scrollTop += 8;
                                    requestAnimationFrame(scrollStep);
                                  }
                                };
                                scrollStep();
                              }
                            }, 200);
                          }
                          
                          // Reset animations for a frame
                          function resetChatFrameAnimations(frameNumber) {
                            const botTextElement = document.getElementById(\`chat-bot-text-\${frameNumber}\`);
                            const userTextElement = document.getElementById(\`chat-user-text-\${frameNumber}\`);
                            
                            if (botTextElement) botTextElement.textContent = '';
                            if (userTextElement) userTextElement.textContent = '';
                            
                            // Reset message visibility and position
                            const frameElement = document.getElementById(\`chat-frame\${frameNumber}\`);
                            if (frameElement) {
                              const messages = frameElement.querySelectorAll('.chat-animation-message');
                              
                              messages.forEach((message, index) => {
                                if (index >= messages.length - 2) { // Only the last two messages (bot and user)
                                  if (message && message.classList) {
                                    message.classList.remove('visible');
                                    message.classList.remove('typing');
                                    message.style.top = '';
                                  }
                                }
                              });
                            }
                          }
                          
                          // Start animations for a frame
                          function startChatFrameAnimations(frameNumber) {
                            const frameKey = \`frame\${frameNumber}\`;
                            const chatFrameTexts = getChatFrameTexts();
                            const botText = chatFrameTexts[frameKey].bot;
                            const userText = chatFrameTexts[frameKey].user;
                            
                            const botTextElement = document.getElementById(\`chat-bot-text-\${frameNumber}\`);
                            const userTextElement = document.getElementById(\`chat-user-text-\${frameNumber}\`);
                            
                            const frameElement = document.getElementById(\`chat-frame\${frameNumber}\`);
                            if (!frameElement) return;
                            
                            const messages = frameElement.querySelectorAll('.chat-animation-message');
                            if (messages.length < 2) return;
                            
                            const botMessage = messages[messages.length - 2]; // Second to last message
                            const userMessage = messages[messages.length - 1]; // Last message
                            
                            // Position messages for mobile-style display
                            const messageHeight = 80;
                            const startY = 50; // 向下移动起始位置
                            
                            messages.forEach((message, index) => {
                              if (message && message.classList && message.classList.contains('visible')) {
                                message.classList.remove('typing');
                                message.style.top = \`\${startY + index * messageHeight}px\`;
                              }
                            });
                            
                            // Show bot message with typing animation
                            setTimeout(() => {
                              if (botMessage && botMessage.classList) {
                                botMessage.classList.add('visible');
                                botMessage.classList.add('typing');
                                botMessage.style.top = \`\${startY + (messages.length - 2) * messageHeight}px\`;
                                typeChatText(botTextElement, botText, 0, () => {
                                  // After bot finishes typing, show user message
                                  if (botMessage && botMessage.classList) {
                                    botMessage.classList.remove('typing');
                                  }
                                  setTimeout(() => {
                                    if (userMessage && userMessage.classList) {
                                      userMessage.classList.add('visible');
                                      userMessage.classList.add('typing');
                                      userMessage.style.top = \`\${startY + (messages.length - 1) * messageHeight}px\`;
                                      typeChatText(userTextElement, userText, 0, () => {
                                        if (userMessage && userMessage.classList) {
                                          userMessage.classList.remove('typing');
                                        }
                                      });
                                    }
                                  }, 400);
                                });
                              }
                            }, 400);
                          }
                          
                          // Typing animation
                          function typeChatText(element, text, index, callback) {
                            if (index < text.length) {
                              element.textContent += text.charAt(index);
                              setTimeout(() => {
                                typeChatText(element, text, index + 1, callback);
                              }, chatTypingSpeed);
                            } else if (callback) {
                              callback();
                            }
                          }
                          
                          // Start auto-play
                          function startChatAutoPlay() {
                            // Auto-advance frames
                            chatAnimationInterval = setInterval(() => {
                              if (chatCurrentFrame < 5) {
                                chatCurrentFrame++;
                                showChatFrame(chatCurrentFrame);
                              } else {
                                // Loop back to first frame
                                chatCurrentFrame = 1;
                                showChatFrame(chatCurrentFrame);
                              }
                            }, 6000); // Time for each frame (typing + reading)
                          }
                          
                          // Update static text content based on current language
                          function updateStaticTexts() {
                            const lang = getCurrentLanguage();
                            const headerElement = document.querySelector('.chat-animation-header');
                            if (headerElement) {
                              headerElement.textContent = lang === 'zh' ? '你的身份是什么？' : "What's your identity?";
                            }
                            
                            // Update all static message texts
                            const staticMessages = document.querySelectorAll('.chat-animation-message span:not(.chat-animation-text-animation)');
                            const chatFrameTexts = getChatFrameTexts();
                            
                            staticMessages.forEach((span, index) => {
                              const text = span.textContent;
                              // Update based on known text patterns
                              if (text === '你好！我想更好地了解你。' || text === "Hi! I'd like to know you better.") {
                                span.textContent = chatFrameTexts.frame1.bot;
                              } else if (text === '你好！当然可以。' || text === "Hi! Sure.") {
                                span.textContent = chatFrameTexts.frame1.user;
                              } else if (text === '对你来说，什么是完美的一天？' || text === 'What would constitute a "perfect" day for you?') {
                                span.textContent = chatFrameTexts.frame2.bot;
                              } else if (text === '和朋友在一起，享受美食和音乐的一天。' || text === "A day with friends, good food, and music.") {
                                span.textContent = chatFrameTexts.frame2.user;
                              } else if (text === '如果你明天醒来能获得任何一种品质或能力，你希望是什么？' || text === "If you could wake up tomorrow having gained any one quality or ability, what would it be?") {
                                span.textContent = chatFrameTexts.frame3.bot;
                              } else if (text === '能够说所有语言的能力。' || text === "The ability to speak every language.") {
                                span.textContent = chatFrameTexts.frame3.user;
                              } else if (text === '在友谊中你最看重什么？' || text === "What do you value most in a friendship?") {
                                span.textContent = chatFrameTexts.frame4.bot;
                              } else if (text === '信任和诚实。' || text === "Trust and honesty.") {
                                span.textContent = chatFrameTexts.frame4.user;
                              }
                            });
                          }
                          
                          // Initialize when DOM is loaded
                          document.addEventListener('DOMContentLoaded', () => {
                            updateStaticTexts();
                            initChatAnimation();
                          });
                          
                          // Also initialize immediately if DOM is already loaded
                          if (document.readyState === 'loading') {
                            document.addEventListener('DOMContentLoaded', () => {
                              updateStaticTexts();
                              initChatAnimation();
                            });
                          } else {
                            updateStaticTexts();
                            initChatAnimation();
                          }
                        </script>
                      `
                    }}
                  />
                </div>
              </div>
              
              {/* 右侧：文字内容 */}
              <div className="space-y-4 max-w-xs mx-auto lg:mx-0 lg:ml-24 flex flex-col justify-center">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white leading-tight font-helvetica">
                  {features[0].title}
                </h3>
                <p className="text-base text-gray-600 dark:text-gray-300 leading-relaxed font-helvetica">
                  {features[0].description} {language === 'zh' 
                    ? '我们的AI系统能够深度分析用户的行为模式、兴趣爱好和价值观，通过先进的机器学习算法，为您找到最匹配的伙伴。无论是寻找浪漫伴侣还是工作伙伴，我们都能提供精准的推荐。'
                    : 'Our AI system deeply analyzes user behavior patterns, interests, and values, using advanced machine learning algorithms to find your perfect match. Whether you\'re looking for a romantic partner or work companion, we provide accurate recommendations.'
                  }
                </p>
                <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold w-[85px] h-[35px] rounded-md text-sm shadow-sm hover:shadow-md transition-all">
                  {language === 'zh' ? '立即体验' : 'Try Now'}
                </Button>
              </div>
            </div>

            {/* 第二行：左文右图 */}
            <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-12 items-center">
              {/* 左侧：文字内容 */}
              <div className="space-y-4 max-w-xs mx-auto lg:mx-0 lg:mr-24 flex flex-col justify-center">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white leading-tight font-helvetica">
                  {features[1].title}
                </h3>
                <p className="text-base text-gray-600 dark:text-gray-300 leading-relaxed font-helvetica">
                  {features[1].description} {language === 'zh'
                    ? '我们不仅仅看表面的兴趣爱好，还会从性格特征、沟通方式、生活目标等多个维度进行深度分析。通过科学的兼容性评估，确保匹配的准确性和长期稳定性。'
                    : 'We don\'t just look at surface interests, but also analyze personality traits, communication styles, and life goals from multiple dimensions. Through scientific compatibility assessment, we ensure matching accuracy and long-term stability.'
                  }
                </p>
                <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold w-[85px] h-[35px] rounded-md text-sm shadow-sm hover:shadow-md transition-all">
                  {language === 'zh' ? '立即体验' : 'Try Now'}
                </Button>
              </div>
              
              {/* 右侧：多维度分析图表 */}
              <div className="bg-gradient-to-br from-pink-50 to-rose-100 dark:from-pink-950 dark:to-rose-900 rounded-3xl p-8 aspect-[4/3]">
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 h-full">
                  {/* 界面功能截图占位 */}
                  <div className="flex items-center justify-center mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-rose-500 rounded-2xl flex items-center justify-center">
                      <Heart className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="text-center">
                    <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                      {language === 'zh' ? '多维度兼容性' : 'Multi-dimensional Compatibility'}
                    </h4>
                    <div className="flex justify-center space-x-2">
                      <div className="w-3 h-3 bg-pink-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-rose-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-pink-300 rounded-full"></div>
                    </div>
                  </div>
                  {/* 添加界面元素 */}
                  <div className="mt-6 grid grid-cols-3 gap-2">
                    <div className="bg-pink-100 rounded-lg p-2 text-center text-xs font-medium">性格</div>
                    <div className="bg-rose-100 rounded-lg p-2 text-center text-xs font-medium">兴趣</div>
                    <div className="bg-pink-100 rounded-lg p-2 text-center text-xs font-medium">价值观</div>
                  </div>
                </div>
              </div>
            </div>

            {/* 第三行：左图右文 */}
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-12 items-center">
              {/* 左侧：安全盾牌 */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-950 dark:to-emerald-900 rounded-3xl p-8 aspect-[4/3]">
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 h-full">
                  {/* 界面功能截图占位 */}
                  <div className="flex items-center justify-center mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center">
                      <Shield className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="text-center">
                    <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                      {language === 'zh' ? '隐私安全' : 'Privacy & Security'}
                    </h4>
                    <div className="flex justify-center space-x-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                      <div className="w-2 h-2 bg-green-300 rounded-full"></div>
                    </div>
                  </div>
                  {/* 添加界面元素 */}
                  <div className="mt-6 space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span>端到端加密</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
                      <span>隐私保护</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* 右侧：文字内容 */}
              <div className="space-y-4 max-w-xs mx-auto lg:mx-0 lg:ml-24 flex flex-col justify-center">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white leading-tight font-helvetica">
                  {features[2].title}
                </h3>
                <p className="text-base text-gray-600 dark:text-gray-300 leading-relaxed font-helvetica">
                  {features[2].description} {language === 'zh'
                    ? '您的隐私是我们的首要考虑。我们采用银行级别的加密技术，所有个人信息都经过严格保护。您可以放心地分享您的想法和需求，我们承诺绝不会泄露您的任何隐私信息。'
                    : 'Your privacy is our top priority. We use bank-level encryption technology, and all personal information is strictly protected. You can safely share your thoughts and needs, and we promise never to disclose any of your private information.'
                  }
                </p>
                <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold w-[85px] h-[35px] rounded-md text-sm shadow-sm hover:shadow-md transition-all">
                  {language === 'zh' ? '立即体验' : 'Try Now'}
                </Button>
              </div>
            </div>

            {/* 第四行：左文右图 */}
            <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-12 items-center">
              {/* 左侧：文字内容 */}
              <div className="space-y-4 max-w-xs mx-auto lg:mx-0 lg:mr-24 flex flex-col justify-center">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white leading-tight font-helvetica">
                  {features[3].title}
                </h3>
                <p className="text-base text-gray-600 dark:text-gray-300 leading-relaxed font-helvetica">
                  {features[3].description} {language === 'zh'
                    ? '我们的系统响应速度极快，通常在几秒钟内就能为您找到合适的匹配。实时更新功能确保您总是能看到最新的推荐结果，不错过任何潜在的优质匹配。'
                    : 'Our system responds extremely fast, usually finding suitable matches for you within seconds. Real-time updates ensure you always see the latest recommendations, never missing any potential quality matches.'
                  }
                </p>
                <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold w-[85px] h-[35px] rounded-md text-sm shadow-sm hover:shadow-md transition-all">
                  {language === 'zh' ? '立即体验' : 'Try Now'}
                </Button>
              </div>
              
              {/* 右侧：实时响应 */}
              <div className="bg-gradient-to-br from-purple-50 to-violet-100 dark:from-purple-950 dark:to-violet-900 rounded-3xl p-8 aspect-[4/3]">
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 h-full">
                  {/* 界面功能截图占位 */}
                  <div className="flex items-center justify-center mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-violet-500 rounded-2xl flex items-center justify-center">
                      <Zap className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="text-center">
                    <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                      {language === 'zh' ? '实时响应' : 'Real-time Response'}
                    </h4>
                    <div className="flex justify-center space-x-1">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-violet-400 rounded-full animate-pulse delay-100"></div>
                      <div className="w-2 h-2 bg-purple-300 rounded-full animate-pulse delay-200"></div>
                    </div>
                  </div>
                  {/* 添加界面元素 */}
                  <div className="mt-6 flex items-center justify-center">
                    <div className="bg-purple-100 rounded-lg px-4 py-2 text-sm font-medium">
                      <span className="text-purple-700">响应时间: 0.5s</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section id="stats" className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center text-white">
            <div>
              <div className="text-5xl font-bold mb-2">10K+</div>
              <div className="text-xl opacity-90">
                {language === 'zh' ? '成功匹配' : 'Successful Matches'}
              </div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">95%</div>
              <div className="text-xl opacity-90">
                {language === 'zh' ? '满意度' : 'Satisfaction Rate'}
              </div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">50K+</div>
              <div className="text-xl opacity-90">
                {language === 'zh' ? '活跃用户' : 'Active Users'}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {language === 'zh' ? '用户评价' : 'What Our Users Say'}
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-6 italic">
                  "{testimonial.content}"
                </p>
                <div>
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {testimonial.name}
                  </div>
                  <div className="text-gray-500 dark:text-gray-400">
                    {testimonial.role}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="cta" className="py-20 bg-white dark:bg-gray-950">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
            {language === 'zh' ? '准备好开始了吗？' : 'Ready to Get Started?'}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            {language === 'zh'
              ? '立即注册，开启您的智能匹配之旅。找到最合适的伙伴，从今天开始。'
              : 'Sign up now and start your intelligent matching journey. Find your perfect partner, starting today.'
            }
          </p>
          <Link href="/login">
            <Button size="lg" className="text-lg px-12 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              {language === 'zh' ? '免费开始' : 'Get Started Free'}
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>
      <footer className="w-full mt-auto border-t bg-background text-foreground">
        <div className="container mx-auto px-4 flex flex-col md:flex-row items-start py-12 gap-8 justify-between">
          {/* 左侧logo和社交icon */}
          <div className="flex flex-col gap-2 items-start min-w-[220px] mt-[-20px]">
            <div className="flex items-center gap-2 mb-2">
              <span style={{display: 'inline-block', height: '8em', width: '8em'}}>
                <svg width="8em" height="8em" viewBox="0 0 1292 507" fill="none" xmlns="http://www.w3.org/2000/svg" style={{height: '8em', width: '8em'}}>
                  <path d="M268.07 30.8866C204.27 101.316 147.27 175.614 92.2696 260.292C21.8696 369.194 -7.13037 435.349 1.46963 468.121C5.86963 484.609 19.4696 499.265 35.8696 504.558C46.6696 508.222 80.0696 507.611 98.4696 503.743C137.47 495.398 183.07 476.264 268.47 432.499C319.47 406.241 376.87 374.893 400.87 360.034L407.07 356.166L406.87 366.548C406.47 375.504 407.27 377.54 412.07 381.814C418.47 387.31 426.47 388.125 436.07 383.85C439.67 382.425 457.87 366.344 476.47 348.228C495.27 330.112 516.07 310.774 522.87 305.278L535.27 295.304L522.27 322.173C515.27 337.032 509.47 351.485 509.47 354.538C509.47 361.255 517.27 367.362 523.27 365.326C525.47 364.716 540.87 349.246 557.27 331.129C584.47 301.41 611.47 274.745 614.27 274.745C614.87 274.745 613.67 279.223 611.67 284.515C598.27 318.916 603.67 339.882 625.47 339.882C634.67 339.882 660.07 329.094 682.47 315.659C693.47 309.145 702.87 304.057 703.27 304.464C703.87 305.074 700.87 312.606 696.47 321.359C687.87 339.475 687.87 347.007 696.47 349.246C699.27 349.856 702.67 350.06 704.07 349.449C707.27 348.228 719.47 322.987 727.67 300.393C735.67 278.612 736.27 278.002 737.67 291.64C739.27 306.703 744.27 313.624 755.67 317.084C783.47 325.633 848.87 304.667 897.47 271.488L918.47 257.036L924.47 260.903C945.67 273.931 984.67 254.796 1031.47 207.775L1057.27 182.128L1058.27 189.252C1058.87 193.119 1059.47 204.315 1059.47 214.086C1059.47 229.352 1060.07 232.609 1063.47 236.069C1071.47 244.212 1077.07 240.344 1087.87 219.378C1111.67 172.764 1188.67 121.672 1268.67 99.4844C1286.07 94.8027 1291.47 91.1387 1291.47 84.4214C1291.47 72.4117 1279.07 72.6153 1241.47 85.4392C1182.27 105.591 1120.67 143.045 1090.67 177.649L1080.07 189.659L1078.87 176.021C1078.07 168.489 1076.27 160.144 1074.47 157.497C1070.67 151.594 1063.27 149.559 1057.27 152.612C1054.87 154.037 1040.07 168.286 1024.67 184.163C997.47 212.254 978.47 228.334 963.07 236.273C955.07 240.548 939.47 244.619 939.47 242.38C939.47 241.769 944.47 237.087 950.67 231.998C964.47 220.803 989.27 194.341 997.87 181.517C1002.27 174.8 1004.47 169.1 1005.07 161.976C1005.67 152.816 1005.27 150.984 1000.47 146.505C996.67 142.842 993.27 141.62 987.27 141.62C966.07 142.231 927.87 185.181 916.27 221.617L911.87 235.052L889.47 250.522C839.67 284.922 779.67 307.924 763.47 299.171C756.87 295.507 758.87 281.869 768.07 267.824C773.87 259.071 778.27 255.204 790.87 248.283C834.67 223.856 852.67 206.147 847.47 192.305C840.67 174.189 811.67 185.995 778.47 220.803C762.07 237.901 747.47 249.097 747.47 244.619C747.47 243.601 748.87 238.716 750.67 233.83C756.67 216.325 765.47 175.817 765.87 163.401C766.27 149.559 763.67 144.47 756.47 144.47C749.47 144.47 746.07 150.373 744.67 165.843C743.47 181.11 735.87 210.625 724.27 246.654L717.27 268.435L697.87 281.055C673.67 296.932 634.87 317.491 629.27 317.491C625.27 317.491 625.07 316.677 626.27 309.349C626.87 304.871 630.67 293.472 634.47 283.905C645.27 257.443 642.87 244.008 627.07 243.601C617.67 243.397 610.07 248.69 581.87 274.541L559.47 295.304L565.47 282.48C568.87 275.355 571.47 267.62 571.47 264.974C571.47 259.275 563.07 250.318 557.67 250.318C550.67 250.318 514.27 281.869 457.67 336.829C442.87 351.281 430.27 361.866 429.87 360.441C429.47 359.22 432.47 347.007 436.47 333.776C443.47 310.57 443.67 309.145 440.67 304.26C438.27 300.8 435.47 299.171 431.47 299.171C426.47 299.171 422.27 302.632 407.07 318.509C397.07 329.297 382.87 342.325 375.67 347.821C348.47 367.973 232.47 429.039 168.47 456.926C120.87 477.688 93.8696 485.016 64.2696 485.22C43.0696 485.424 41.8696 485.22 34.8696 479.724C19.0696 467.511 17.4696 456.315 27.4696 424.968C50.0696 352.706 168.27 174.596 265.07 66.5087C306.47 20.3018 309.47 16.6378 309.47 10.5312C309.47 7.47789 308.47 3.81392 307.07 2.38903C301.27 -3.51404 296.27 -0.0536177 268.07 30.8866ZM979.47 170.728C978.47 172.968 970.67 181.72 962.27 190.677C951.27 202.279 948.07 204.722 950.87 199.633C954.47 192.916 977.67 166.861 980.27 166.861C981.07 166.861 980.67 168.693 979.47 170.728Z" fill="currentColor"/>
                  <path d="M444.27 231.388C438.67 237.698 437.47 238.309 437.47 234.848C437.47 229.149 433.67 225.892 427.07 225.892C416.67 225.892 414.87 237.291 421.67 259.275C424.67 269.656 426.87 273.524 430.67 275.152C438.47 278.816 444.47 274.134 454.67 257.036C465.87 238.309 467.07 233.627 461.67 228.131C455.67 222.024 452.07 222.839 444.27 231.388Z" fill="currentColor"/>
                </svg>
              </span>
            </div>
            <div className="flex gap-4 mb-2">
              <span className="rounded-lg border border-muted-foreground p-2 flex items-center justify-center" style={{width: '2.5em', height: '2.5em'}}>
                {/* Discord icon SVG */}
                <svg width="1.5em" height="1.5em" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.472 3.368A17.826 17.826 0 0 0 12 2.25c-1.89 0-3.728.273-5.472.784C3.368 5.472 2.25 8.16 2.25 12c0 3.84 1.118 6.528 4.278 8.966A17.826 17.826 0 0 0 12 21.75c1.89 0 3.728-.273 5.472-.784C20.632 18.528 21.75 15.84 21.75 12c0-3.84-1.118-6.528-4.278-8.966Z"/><path d="M15.5 9.5h.01M8.5 9.5h.01M12 17.5c-2.5 0-4.5-2-4.5-4.5s2-4.5 4.5-4.5 4.5 2 4.5 4.5-2 4.5-4.5 4.5Z"/></svg>
              </span>
              <span className="rounded-lg border border-muted-foreground p-2 flex items-center justify-center" style={{width: '2.5em', height: '2.5em'}}>
                {/* X(Twitter) icon SVG */}
                <svg width="1.5em" height="1.5em" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.5 6.5l-11 11M6.5 6.5l11 11"/></svg>
              </span>
              <span className="rounded-lg border border-muted-foreground p-2 flex items-center justify-center" style={{width: '2.5em', height: '2.5em'}}>
                <Youtube className="w-6 h-6" />
              </span>
              <span className="rounded-lg border border-muted-foreground p-2 flex items-center justify-center" style={{width: '2.5em', height: '2.5em'}}>
                <Linkedin className="w-6 h-6" />
              </span>
              <span className="rounded-lg border border-muted-foreground p-2 flex items-center justify-center" style={{width: '2.5em', height: '2.5em'}}>
                <Instagram className="w-6 h-6" />
              </span>
              <span className="rounded-lg border border-muted-foreground p-2 flex items-center justify-center" style={{width: '2.5em', height: '2.5em'}}>
                {/* TikTok icon SVG */}
                <svg width="1.5em" height="1.5em" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 17a4 4 0 1 1 0-8v8Zm0 0a4 4 0 0 0 4-4V3.5c1.5.5 2.5 2 4 2"/></svg>
              </span>
            </div>
            <div className="flex flex-wrap gap-4 items-center text-sm text-muted-foreground">
              <span>2025 © Linker</span>
              <span className="cursor-pointer hover:underline">{language === 'zh' ? '服务条款' : 'Terms of Service'}</span>
              <span className="cursor-pointer hover:underline">{language === 'zh' ? '隐私政策' : 'Privacy Policy'}</span>
            </div>
          </div>
          {/* 右侧三列导航 */}
          <div className="flex-1 flex flex-col sm:flex-row justify-end w-full gap-8 ml-10 translate-x-10">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 w-full max-w-2xl ml-auto">
              <div>
                <div className="font-bold mb-2">{language === 'zh' ? '产品' : 'Product'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '社区画廊' : 'Community Gallery'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '新闻' : 'News'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '价格' : 'Pricing'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '更新日志' : 'Release Notes'}</div>
              </div>
              <div>
                <div className="font-bold mb-2">{language === 'zh' ? '资源' : 'Resources'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '工具' : 'Tools'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '功能' : 'Features'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '博客' : 'Blog'}</div>
              </div>
              <div>
                <div className="font-bold mb-2">{language === 'zh' ? '关于' : 'About'}</div>
                <div className="mb-1 cursor-pointer hover:underline">{language === 'zh' ? '联系我们' : 'Contact Us'}</div>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
} 