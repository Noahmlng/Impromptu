'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/lib/store'

interface NavItem {
  id: string
  label: { zh: string; en: string }
}

const navItems: NavItem[] = [
  {
    id: 'hero',
    label: { zh: '首页', en: 'Home' }
  },
  {
    id: 'features',
    label: { zh: '功能', en: 'Features' }
  },
  {
    id: 'stats',
    label: { zh: '数据', en: 'Stats' }
  },
  {
    id: 'testimonials',
    label: { zh: '评价', en: 'Reviews' }
  },
  {
    id: 'cta',
    label: { zh: '开始', en: 'Get Started' }
  }
]

export function ScrollNavbar() {
  const { language } = useAppStore()
  const [activeSection, setActiveSection] = useState('hero')
  const [isVisible, setIsVisible] = useState(false)
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY
      
      // 显示/隐藏导航栏 - 滚动超过100px时显示
      setIsVisible(scrollY > 100)
      
      // 计算滚动进度 - 更平滑的计算
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = Math.min(100, Math.max(0, (scrollY / documentHeight) * 100))
      setScrollProgress(progress)

      // 获取所有section元素
      const sections = navItems.map(item => {
        const element = document.getElementById(item.id)
        if (!element) return { id: item.id, top: Infinity, bottom: Infinity }
        
        const rect = element.getBoundingClientRect()
        return {
          id: item.id,
          top: rect.top + scrollY,
          bottom: rect.bottom + scrollY
        }
      })

      // 找到当前激活的section
      const currentSection = sections.find(section => {
        const offset = 200 // 偏移量，提前激活
        return scrollY >= section.top - offset && scrollY < section.bottom - offset
      })

      if (currentSection) {
        setActiveSection(currentSection.id)
      }
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // 初始调用

    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      const offsetTop = element.offsetTop - 80 // 留出一些顶部空间
      window.scrollTo({
        top: offsetTop,
        behavior: 'smooth'
      })
    }
  }

  if (!isVisible) return null

  return (
    <div className="fixed left-4 top-1/2 transform -translate-y-1/2 z-50">
      {/* 主容器 - 作为进度条背景 */}
      <div className="relative bg-gray-50/40 dark:bg-gray-900/40 backdrop-blur-sm rounded-full shadow-sm border border-gray-200/20 dark:border-gray-700/20 overflow-hidden">
        {/* 进度条背景 - 更丝滑的过渡，从顶部开始填充 */}
        <div 
          className="absolute top-0 left-0 w-full bg-gradient-to-b from-blue-500/20 to-purple-600/15 dark:from-blue-400/20 dark:to-purple-500/15 transition-all duration-500 ease-out rounded-full"
          style={{
            height: `${scrollProgress}%`
          }}
        />
        
        {/* 内容容器 */}
        <div className="relative z-10 px-2 py-6">
          {/* 导航项 */}
          <div className="space-y-5">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => scrollToSection(item.id)}
                className="group relative flex items-center justify-center w-full transition-all duration-200"
              >
                {/* 小圆圈 - 轻微蓝紫色 */}
                <div className={`
                  w-2.5 h-2.5 rounded-full transition-all duration-200 relative z-10
                  ${activeSection === item.id 
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 scale-125' 
                    : 'bg-gray-100 dark:bg-gray-800 group-hover:bg-blue-400/60 dark:group-hover:bg-purple-400/60 group-hover:scale-110'
                  }
                `} />
                
                {/* 工具提示 */}
                <div className={`
                  absolute left-6 px-2 py-1 bg-gray-800 dark:bg-gray-700 text-white text-xs rounded
                  opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none
                  whitespace-nowrap z-20
                `}>
                  {language === 'zh' ? item.label.zh : item.label.en}
                  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-0 h-0 border-t-2 border-b-2 border-r-2 border-transparent border-r-gray-800 dark:border-r-gray-700"></div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 