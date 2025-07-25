'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { auth } from '@/lib/api'
import { Heart, Users, Mail, Lock, User, Eye, EyeOff, AlertCircle } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const { 
    themeMode, 
    language, 
    setAuthToken, 
    setBackendUser, 
    setUser,
    setIsAuthLoading,
    setError,
    error,
    isAuthLoading
  } = useAppStore()
  
  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Prevent double submission
    if (isSubmitting || isAuthLoading) {
      return;
    }
    
    setError(null)
    setIsAuthLoading(true)
    setIsSubmitting(true)

    try {
      if (isLogin) {
        // Login
        const response = await auth.login(formData.email, formData.password)
        
        if (response.success) {
          // Update store with user data
          setAuthToken(response.data!.token)
          setBackendUser({
            user_id: response.data!.user_id,
            email: response.data!.email,
            display_name: response.data!.display_name,
            avatar_url: response.data!.avatar_url,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            last_login_at: new Date().toISOString(),
            is_active: true
          })
          
          // Create legacy user object for compatibility
          setUser({
            id: response.data!.user_id,
            name: response.data!.display_name,
            email: response.data!.email,
            avatar: response.data!.avatar_url,
            credits: 0,
            subscription: 'free'
          })
          
          // Redirect to main app
          router.push('/')
        } else {
          setError(response.message)
        }
      } else {
        // Register
        if (formData.password !== formData.confirmPassword) {
          setError(language === 'zh' ? '密码不匹配' : 'Passwords do not match')
          return
        }
        
        if (formData.password.length < 6) {
          setError(language === 'zh' ? '密码至少需要6个字符' : 'Password must be at least 6 characters')
          return
        }
        
        const response = await auth.register(
          formData.email, 
          formData.password, 
          formData.name
        )
        
        if (response.success) {
          // Update store with user data
          setAuthToken(response.data!.token)
          setBackendUser({
            user_id: response.data!.user_id,
            email: response.data!.email,
            display_name: response.data!.display_name,
            avatar_url: response.data!.avatar_url,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            last_login_at: new Date().toISOString(),
            is_active: true
          })
          
          // Create legacy user object for compatibility
          setUser({
            id: response.data!.user_id,
            name: response.data!.display_name,
            email: response.data!.email,
            avatar: response.data!.avatar_url,
            credits: 0,
            subscription: 'free'
          })
          
          // Redirect to onboarding for new users
          router.push('/onboarding')
        } else {
          setError(response.message)
        }
      }
    } catch (error: any) {
      setError(error.message || (language === 'zh' ? '操作失败，请重试' : 'Operation failed, please try again'))
    } finally {
      setIsAuthLoading(false)
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted/50 px-4">
      <div className="w-full max-w-md space-y-8">
        {/* Logo and Title */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-2">
            {themeMode === 'romantic' ? (
              <Heart className="h-10 w-10 text-romantic-pink-500" />
            ) : (
              <Users className="h-10 w-10 text-miami-blue-500" />
            )}
            <h1 className="text-3xl font-bold">Linker</h1>
          </div>
          <h2 className="text-xl font-semibold">
            {isLogin 
              ? (language === 'zh' ? '登录您的账户' : 'Sign in to your account')
              : (language === 'zh' ? '创建新账户' : 'Create new account')
            }
          </h2>
          <p className="text-muted-foreground">
            {language === 'zh' 
              ? '开始您的智能匹配之旅'
              : 'Start your AI-powered matching journey'
            }
          </p>
        </div>

        {/* Form */}
        <div className="bg-card p-8 rounded-lg shadow-lg border">
          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center space-x-2" suppressHydrationWarning>
              <AlertCircle className="h-4 w-4 text-destructive" />
              <span className="text-sm text-destructive">{error}</span>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name field for registration */}
            {!isLogin && (
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span>{language === 'zh' ? '姓名' : 'Name'}</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder={language === 'zh' ? '请输入您的姓名' : 'Enter your name'}
                  autoComplete="name"
                  required
                />
              </div>
            )}

            {/* Email field */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center space-x-2">
                <Mail className="h-4 w-4" />
                <span>{language === 'zh' ? '邮箱' : 'Email'}</span>
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder={language === 'zh' ? '请输入邮箱地址' : 'Enter your email'}
                autoComplete="email"
                required
              />
            </div>

            {/* Password field */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center space-x-2">
                <Lock className="h-4 w-4" />
                <span>{language === 'zh' ? '密码' : 'Password'}</span>
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className="w-full px-3 py-2 pr-10 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder={language === 'zh' ? '请输入密码' : 'Enter your password'}
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Confirm Password field for registration */}
            {!isLogin && (
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <Lock className="h-4 w-4" />
                  <span>{language === 'zh' ? '确认密码' : 'Confirm Password'}</span>
                </label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder={language === 'zh' ? '再次输入密码' : 'Confirm your password'}
                  autoComplete="new-password"
                  required
                />
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={isAuthLoading || isSubmitting}
            >
              {isAuthLoading || isSubmitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>
                    {language === 'zh' ? '处理中...' : 'Processing...'}
                  </span>
                </div>
              ) : (
                isLogin 
                ? (language === 'zh' ? '登录' : 'Sign In')
                : (language === 'zh' ? '注册' : 'Sign Up')
              )}
            </Button>
          </form>

          {/* Toggle between login and register */}
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              {isLogin 
                ? (language === 'zh' ? '还没有账户？' : "Don't have an account?")
                : (language === 'zh' ? '已有账户？' : 'Already have an account?')
              }
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="ml-2 text-primary hover:underline font-medium"
                disabled={isAuthLoading || isSubmitting}
              >
                {isLogin 
                  ? (language === 'zh' ? '立即注册' : 'Sign up')
                  : (language === 'zh' ? '立即登录' : 'Sign in')
                }
              </button>
            </p>
          </div>

          {/* Social Login */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-muted" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">
                  {language === 'zh' ? '或者' : 'Or'}
                </span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <Button variant="outline" className="w-full" disabled={isAuthLoading || isSubmitting}>
                <svg className="h-4 w-4 mr-2" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google
              </Button>
              <Button variant="outline" className="w-full" disabled={isAuthLoading || isSubmitting}>
                <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Facebook
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 