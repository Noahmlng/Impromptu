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
    setError,
    error
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
    if (isSubmitting) {
      return;
    }
    
    setError(null)
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
            subscription_type: response.data!.subscription_type || 'free',
            created_at: response.data!.created_at || new Date().toISOString(),
            updated_at: response.data!.updated_at || new Date().toISOString(),
            last_login_at: response.data!.last_login_at || new Date().toISOString(),
            is_active: response.data!.is_active !== undefined ? response.data!.is_active : true
          })
          
          // Create legacy user object for compatibility
          setUser({
            id: response.data!.user_id,
            name: response.data!.display_name,
            email: response.data!.email,
            avatar: response.data!.avatar_url,
            credits: 0,
            subscription: response.data!.subscription_type || 'free'
          })
          
          // 等待状态更新完成后再跳转，直接跳转到主页
          setTimeout(() => {
            router.push('/home')
          }, 100)
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
            subscription_type: response.data!.subscription_type || 'free',
            created_at: response.data!.created_at || new Date().toISOString(),
            updated_at: response.data!.updated_at || new Date().toISOString(),
            last_login_at: response.data!.last_login_at || new Date().toISOString(),
            is_active: response.data!.is_active !== undefined ? response.data!.is_active : true
          })
          
          // Create legacy user object for compatibility
          setUser({
            id: response.data!.user_id,
            name: response.data!.display_name,
            email: response.data!.email,
            avatar: response.data!.avatar_url,
            credits: 0,
            subscription: response.data!.subscription_type || 'free'
          })
          
          // 等待状态更新完成后再跳转到新手引导页面
          setTimeout(() => {
            router.push('/onboarding')
          }, 100)
        } else {
          setError(response.message)
        }
      }
    } catch (error: any) {
      setError(error.message || (language === 'zh' ? '操作失败，请重试' : 'Operation failed, please try again'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted/50 px-4">
      <div className="w-full max-w-md space-y-8 -mt-32">
        {/* Logo and Title */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <div className="flex items-center">
              <svg 
                width="144" 
                height="104" 
                viewBox="0 20 1292 467" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
                className="h-26 w-auto"
              >
                <defs>
                  <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    {themeMode === 'romantic' ? (
                      <>
                        <stop offset="0%" stopColor="#ec4899" />
                        <stop offset="100%" stopColor="#be185d" />
                      </>
                    ) : (
                      <>
                        <stop offset="0%" stopColor="#06b6d4" />
                        <stop offset="100%" stopColor="#0891b2" />
                      </>
                    )}
                  </linearGradient>
                </defs>
                <path d="M268.07 30.8866C204.27 101.316 147.27 175.614 92.2696 260.292C21.8696 369.194 -7.13037 435.349 1.46963 468.121C5.86963 484.609 19.4696 499.265 35.8696 504.558C46.6696 508.222 80.0696 507.611 98.4696 503.743C137.47 495.398 183.07 476.264 268.47 432.499C319.47 406.241 376.87 374.893 400.87 360.034L407.07 356.166L406.87 366.548C406.47 375.504 407.27 377.54 412.07 381.814C418.47 387.31 426.47 388.125 436.07 383.85C439.67 382.425 457.87 366.344 476.47 348.228C495.27 330.112 516.07 310.774 522.87 305.278L535.27 295.304L522.27 322.173C515.27 337.032 509.47 351.485 509.47 354.538C509.47 361.255 517.27 367.362 523.27 365.326C525.47 364.716 540.87 349.246 557.27 331.129C584.47 301.41 611.47 274.745 614.27 274.745C614.87 274.745 613.67 279.223 611.67 284.515C598.27 318.916 603.67 339.882 625.47 339.882C634.67 339.882 660.07 329.094 682.47 315.659C693.47 309.145 702.87 304.057 703.27 304.464C703.87 305.074 700.87 312.606 696.47 321.359C687.87 339.475 687.87 347.007 696.47 349.246C699.27 349.856 702.67 350.06 704.07 349.449C707.27 348.228 719.47 322.987 727.67 300.393C735.67 278.612 736.27 278.002 737.67 291.64C739.27 306.703 744.27 313.624 755.67 317.084C783.47 325.633 848.87 304.667 897.47 271.488L918.47 257.036L924.47 260.903C945.67 273.931 984.67 254.796 1031.47 207.775L1057.27 182.128L1058.27 189.252C1058.87 193.119 1059.47 204.315 1059.47 214.086C1059.47 229.352 1060.07 232.609 1063.47 236.069C1071.47 244.212 1077.07 240.344 1087.87 219.378C1111.67 172.764 1188.67 121.672 1268.67 99.4844C1286.07 94.8027 1291.47 91.1387 1291.47 84.4214C1291.47 72.4117 1279.07 72.6153 1241.47 85.4392C1182.27 105.591 1120.67 143.045 1090.67 177.649L1080.07 189.659L1078.87 176.021C1078.07 168.489 1076.27 160.144 1074.47 157.497C1070.67 151.594 1063.27 149.559 1057.27 152.612C1054.87 154.037 1040.07 168.286 1024.67 184.163C997.47 212.254 978.47 228.334 963.07 236.273C955.07 240.548 939.47 244.619 939.47 242.38C939.47 241.769 944.47 237.087 950.67 231.998C964.47 220.803 989.27 194.341 997.87 181.517C1002.27 174.8 1004.47 169.1 1005.07 161.976C1005.67 152.816 1005.27 150.984 1000.47 146.505C996.67 142.842 993.27 141.62 987.27 141.62C966.07 142.231 927.87 185.181 916.27 221.617L911.87 235.052L889.47 250.522C839.67 284.922 779.67 307.924 763.47 299.171C756.87 295.507 758.87 281.869 768.07 267.824C773.87 259.071 778.27 255.204 790.87 248.283C834.67 223.856 852.67 206.147 847.47 192.305C840.67 174.189 811.67 185.995 778.47 220.803C762.07 237.901 747.47 249.097 747.47 244.619C747.47 243.601 748.87 238.716 750.67 233.83C756.67 216.325 765.47 175.817 765.87 163.401C766.27 149.559 763.67 144.47 756.47 144.47C749.47 144.47 746.07 150.373 744.67 165.843C743.47 181.11 735.87 210.625 724.27 246.654L717.27 268.435L697.87 281.055C673.67 296.932 634.87 317.491 629.27 317.491C625.27 317.491 625.07 316.677 626.27 309.349C626.87 304.871 630.67 293.472 634.47 283.905C645.27 257.443 642.87 244.008 627.07 243.601C617.67 243.397 610.07 248.69 581.87 274.541L559.47 295.304L565.47 282.48C568.87 275.355 571.47 267.62 571.47 264.974C571.47 259.275 563.07 250.318 557.67 250.318C550.67 250.318 514.27 281.869 457.67 336.829C442.87 351.281 430.27 361.866 429.87 360.441C429.47 359.22 432.47 347.007 436.47 333.776C443.47 310.57 443.67 309.145 440.67 304.26C438.27 300.8 435.47 299.171 431.47 299.171C426.47 299.171 422.27 302.632 407.07 318.509C397.07 329.297 382.87 342.325 375.67 347.821C348.47 367.973 232.47 429.039 168.47 456.926C120.87 477.688 93.8696 485.016 64.2696 485.22C43.0696 485.424 41.8696 485.22 34.8696 479.724C19.0696 467.511 17.4696 456.315 27.4696 424.968C50.0696 352.706 168.27 174.596 265.07 66.5087C306.47 20.3018 309.47 16.6378 309.47 10.5312C309.47 7.47789 308.47 3.81392 307.07 2.38903C301.27 -3.51404 296.27 -0.0536177 268.07 30.8866ZM979.47 170.728C978.47 172.968 970.67 181.72 962.27 190.677C951.27 202.279 948.07 204.722 950.87 199.633C954.47 192.916 977.67 166.861 980.27 166.861C981.07 166.861 980.67 168.693 979.47 170.728Z" fill="url(#logoGradient)"/>
                <path d="M444.27 231.388C438.67 237.698 437.47 238.309 437.47 234.848C437.47 229.149 433.67 225.892 427.07 225.892C416.67 225.892 414.87 237.291 421.67 259.275C424.67 269.656 426.87 273.524 430.67 275.152C438.47 278.816 444.47 274.134 454.67 257.036C465.87 238.309 467.07 233.627 461.67 228.131C455.67 222.024 452.07 222.839 444.27 231.388Z" fill="url(#logoGradient)"/>
              </svg>
            </div>

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
              disabled={isSubmitting}
            >
              {isSubmitting ? (
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
                disabled={isSubmitting}
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
              <Button variant="outline" className="w-full" disabled={isSubmitting}>
                <svg className="h-4 w-4 mr-2" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google
              </Button>
              <Button variant="outline" className="w-full" disabled={isSubmitting}>
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