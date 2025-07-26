'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { useOptionalAuth } from '@/hooks/useAuth'
import { 
  Heart, 
  Users, 
  Brain, 
  Shield, 
  Zap, 
  Star,
  ArrowRight,
  Check,
  ChevronRight
} from 'lucide-react'

export default function LandingPage() {
  const { language } = useAppStore()
  const router = useRouter()
  const { isAuthenticated, isLoading } = useOptionalAuth()

  // Redirect to /home if user is authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/home')
    }
  }, [isAuthenticated, isLoading, router])

  // Show loading or redirect if authenticated
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">
            {language === 'zh' ? '加载中...' : 'Loading...'}
          </p>
        </div>
      </div>
    )
  }

  // Don't render landing page if user is authenticated (will redirect)
  if (isAuthenticated) {
    return null
  }

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
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center space-y-8">
            <div className="flex items-center justify-center space-x-3 mb-6">
              <div className="relative">
                <Heart className="h-16 w-16 text-pink-500 animate-pulse" />
                <Users className="h-10 w-10 text-blue-500 absolute -top-2 -right-2" />
              </div>
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              {language === 'zh' ? 'Linker' : 'Linker'}
            </h1>
            
            <p className="text-xl lg:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
              {language === 'zh' 
                ? '通过AI驱动的智能匹配系统，为您找到最合适的伙伴。无论是工作合作、学习交流，还是生活陪伴，Linker都能为您精准匹配。'
                : 'Find your perfect match through our AI-powered intelligent matching system. Whether for work collaboration, study partners, or life companions, Linker provides precise matching for you.'
              }
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
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
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white dark:bg-gray-950">
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
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-8 text-center hover:shadow-lg transition-shadow">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <feature.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
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
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
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
      <section className="py-20 bg-white dark:bg-gray-950">
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
    </div>
  )
} 