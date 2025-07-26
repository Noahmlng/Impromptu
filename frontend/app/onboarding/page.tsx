'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/hooks/useAuth'
import { profile, matching } from '@/lib/api'
import { MatchUser } from '@/lib/types'
import { 
  User, 
  Search, 
  Heart, 
  Users, 
  ArrowRight, 
  CheckCircle,
  AlertCircle,
  Loader2,
  Star
} from 'lucide-react'

interface OnboardingStep {
  id: number
  title: string
  description: string
  completed: boolean
}

export default function OnboardingPage() {
  const router = useRouter()
  const { user: authUser, isLoading: authLoading } = useRequireAuth()
  const { 
    language, 
    backendUser,
    setIsLoading,
    setError,
    error,
    isLoading
  } = useAppStore()
  
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  
  // Step 1: Basic Info
  const [basicInfo, setBasicInfo] = useState({
    age_range: '',
    location: '',
    living_situation: '',
    occupation: '',
    industry: '',
    bio: '',
    interests: '',
    goals: ''
  })
  
  // Step 2: Search Results
  const [selectedRequestType, setSelectedRequestType] = useState<'找队友' | '找对象'>('找队友')
  const [searchDescription, setSearchDescription] = useState('')
  const [searchResults, setSearchResults] = useState<MatchUser[]>([])
  
  const steps: OnboardingStep[] = [
    {
      id: 1,
      title: language === 'zh' ? '填写基本信息' : 'Basic Information',
      description: language === 'zh' ? '让我们了解您的基本情况' : 'Tell us about yourself',
      completed: currentStep > 1
    },
    {
      id: 2,
      title: language === 'zh' ? '开始匹配' : 'Start Matching',
      description: language === 'zh' ? '描述需求并开始匹配' : 'Describe your needs and start matching',
      completed: currentStep > 2
    }
  ]

  // Save basic info and move to next step
  const handleSaveBasicInfo = async () => {
    if (!authUser) return
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      // Prepare metadata entries
      const metadataEntries = [
        {
          section_type: 'profile',
          section_key: 'personal',
          content: {
            age_range: basicInfo.age_range,
            location: basicInfo.location,
            living_situation: basicInfo.living_situation,
            bio: basicInfo.bio,
            interests: basicInfo.interests,
            goals: basicInfo.goals
          }
        },
        {
          section_type: 'profile',
          section_key: 'professional',
          content: {
            current_role: basicInfo.occupation,
            industry: basicInfo.industry
          }
        }
      ]

      // Save metadata
      await profile.batchUpdateMetadata(metadataEntries)
      
      setSuccessMessage(language === 'zh' ? '基本信息保存成功！标签将自动生成。' : 'Basic information saved successfully! Tags will be generated automatically.')
      setTimeout(() => {
        setSuccessMessage('')
        setCurrentStep(2)
      }, 1500)
      
    } catch (error: any) {
      setError(error.message || (language === 'zh' ? '保存失败，请重试' : 'Failed to save, please try again'))
    } finally {
      setIsSubmitting(false)
    }
  }

  // Search for matching users
  const handleSearchMatches = async () => {
    if (!authUser || !searchDescription.trim()) return
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      const response = await matching.search(
        searchDescription,
        [], // Empty tags array since backend will use auto-generated tags
        selectedRequestType,
        10
      )
      
      if (response.success) {
        setSearchResults(response.data)
        setSuccessMessage(
          language === 'zh' 
            ? `找到${response.data.length}个匹配用户！` 
            : `Found ${response.data.length} matching users!`
        )
        
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (error: any) {
      setError(error.message || (language === 'zh' ? '搜索失败，请重试' : 'Search failed, please try again'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFinishOnboarding = () => {
    router.push('/home')
  }

  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">
            {language === 'zh' ? '加载中...' : 'Loading...'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Heart className="h-8 w-8 text-romantic-pink-500" />
            <Users className="h-8 w-8 text-miami-blue-500" />
          </div>
          <h1 className="text-3xl font-bold mb-2">
            {language === 'zh' ? '欢迎来到 Linker！' : 'Welcome to Linker!'}
          </h1>
          <p className="text-muted-foreground">
            {language === 'zh' 
              ? '让我们帮您设置个人档案，开始智能匹配之旅' 
              : 'Let us help you set up your profile and start your matching journey'
            }
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                step.completed 
                  ? 'bg-primary border-primary text-primary-foreground' 
                  : currentStep === step.id
                  ? 'border-primary text-primary'
                  : 'border-muted text-muted-foreground'
              }`}>
                {step.completed ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <span className="text-sm font-medium">{step.id}</span>
                )}
              </div>
              {index < steps.length - 1 && (
                <div className={`w-20 h-0.5 mx-4 ${
                  step.completed ? 'bg-primary' : 'bg-muted'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Status Messages */}
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-destructive" />
            <span className="text-sm text-destructive">{error}</span>
          </div>
        )}
        
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-sm text-green-600">{successMessage}</span>
          </div>
        )}

        {/* Step Content */}
        <div className="bg-card rounded-lg p-8 shadow-lg border">
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <User className="h-12 w-12 text-primary mx-auto mb-4" />
                <h2 className="text-2xl font-semibold mb-2">
                  {language === 'zh' ? '基本信息' : 'Basic Information'}
                </h2>
                <p className="text-muted-foreground">
                  {language === 'zh' ? '请填写您的基本信息，保存后系统将自动生成个性化标签' : 'Please fill in your basic information, personalized tags will be generated automatically after saving'}
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '年龄范围' : 'Age Range'}
                  </label>
                  <select
                    value={basicInfo.age_range}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, age_range: e.target.value }))}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  >
                    <option value="">{language === 'zh' ? '请选择' : 'Please select'}</option>
                    <option value="18-25岁">18-25{language === 'zh' ? '岁' : ' years'}</option>
                    <option value="25-30岁">25-30{language === 'zh' ? '岁' : ' years'}</option>
                    <option value="30-35岁">30-35{language === 'zh' ? '岁' : ' years'}</option>
                    <option value="35-40岁">35-40{language === 'zh' ? '岁' : ' years'}</option>
                    <option value="40+岁">40+{language === 'zh' ? '岁' : ' years'}</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '所在城市' : 'Location'}
                  </label>
                  <input
                    type="text"
                    value={basicInfo.location}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, location: e.target.value }))}
                    placeholder={language === 'zh' ? '如：深圳' : 'e.g., Shenzhen'}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '居住情况' : 'Living Situation'}
                  </label>
                  <select
                    value={basicInfo.living_situation}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, living_situation: e.target.value }))}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  >
                    <option value="">{language === 'zh' ? '请选择' : 'Please select'}</option>
                    <option value="独居">{language === 'zh' ? '独居' : 'Living alone'}</option>
                    <option value="合租">{language === 'zh' ? '合租' : 'Shared housing'}</option>
                    <option value="与家人同住">{language === 'zh' ? '与家人同住' : 'Living with family'}</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '职业' : 'Occupation'}
                  </label>
                  <input
                    type="text"
                    value={basicInfo.occupation}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, occupation: e.target.value }))}
                    placeholder={language === 'zh' ? '如：软件工程师' : 'e.g., Software Engineer'}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '行业' : 'Industry'}
                  </label>
                  <input
                    type="text"
                    value={basicInfo.industry}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, industry: e.target.value }))}
                    placeholder={language === 'zh' ? '如：互联网/技术' : 'e.g., Internet/Technology'}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '个人简介' : 'Bio'}
                  </label>
                  <textarea
                    value={basicInfo.bio}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, bio: e.target.value }))}
                    placeholder={language === 'zh' ? '简单介绍一下自己...' : 'Tell us about yourself...'}
                    rows={3}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '兴趣爱好' : 'Interests'}
                  </label>
                  <textarea
                    value={basicInfo.interests}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, interests: e.target.value }))}
                    placeholder={language === 'zh' ? '您的兴趣爱好，如：读书、运动、旅行...' : 'Your interests, e.g., reading, sports, travel...'}
                    rows={2}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '目标或期望' : 'Goals or Expectations'}
                  </label>
                  <textarea
                    value={basicInfo.goals}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, goals: e.target.value }))}
                    placeholder={language === 'zh' ? '您希望通过Linker实现什么目标...' : 'What do you hope to achieve through Linker...'}
                    rows={2}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                  />
                </div>
              </div>

              <Button
                onClick={handleSaveBasicInfo}
                className="w-full"
                size="lg"
                disabled={isSubmitting || !basicInfo.age_range || !basicInfo.location}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {language === 'zh' ? '保存中...' : 'Saving...'}
                  </>
                ) : (
                  <>
                    {language === 'zh' ? '保存并继续' : 'Save and Continue'}
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          )}

          {/* Step 2: Start Matching */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Search className="h-12 w-12 text-primary mx-auto mb-4" />
                <h2 className="text-2xl font-semibold mb-2">
                  {language === 'zh' ? '开始匹配' : 'Start Matching'}
                </h2>
                <p className="text-muted-foreground">
                  {language === 'zh' ? '选择匹配类型并描述您的需求，我们将为您找到最合适的伙伴' : 'Choose matching type and describe your needs, we will find the most suitable partners for you'}
                </p>
              </div>

              {/* Request Type Selection */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">
                  {language === 'zh' ? '选择匹配类型' : 'Select Matching Type'}
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <button
                    onClick={() => setSelectedRequestType('找队友')}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      selectedRequestType === '找队友' 
                        ? 'border-miami-blue-500 bg-miami-blue-50 text-miami-blue-700' 
                        : 'border-muted hover:border-primary'
                    }`}
                  >
                    <Users className="h-8 w-8 mx-auto mb-2" />
                    <h4 className="font-medium">{language === 'zh' ? '寻找队友' : 'Find Teammates'}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {language === 'zh' ? '工作合作、项目伙伴、学习同伴' : 'Work collaboration, project partners, study companions'}
                    </p>
                  </button>
                  
                  <button
                    onClick={() => setSelectedRequestType('找对象')}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      selectedRequestType === '找对象' 
                        ? 'border-romantic-pink-500 bg-romantic-pink-50 text-romantic-pink-700' 
                        : 'border-muted hover:border-primary'
                    }`}
                  >
                    <Heart className="h-8 w-8 mx-auto mb-2" />
                    <h4 className="font-medium">{language === 'zh' ? '寻找对象' : 'Find Partner'}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {language === 'zh' ? '恋爱关系、长期伴侣、生活陪伴' : 'Romantic relationships, long-term partners, life companions'}
                    </p>
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    {language === 'zh' ? '描述您的需求' : 'Describe Your Needs'}
                  </label>
                  <textarea
                    value={searchDescription}
                    onChange={(e) => setSearchDescription(e.target.value)}
                    placeholder={
                      selectedRequestType === '找队友'
                        ? (language === 'zh' ? '例如：寻找技术合作伙伴，一起开发产品...' : 'e.g., Looking for technical partners to develop products together...')
                        : (language === 'zh' ? '例如：希望找到志趣相投的伴侣，一起分享生活...' : 'e.g., Looking for a like-minded partner to share life together...')
                    }
                    rows={4}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                  />
                </div>

                <Button
                  onClick={handleSearchMatches}
                  className="w-full"
                  size="lg"
                  disabled={isSubmitting || !searchDescription.trim()}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      {language === 'zh' ? '匹配中...' : 'Matching...'}
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      {language === 'zh' ? '开始匹配' : 'Start Matching'}
                    </>
                  )}
                </Button>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">
                    {language === 'zh' ? '匹配结果' : 'Match Results'}
                  </h3>
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {searchResults.map((match, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                              <span className="text-primary font-medium">
                                {match.display_name.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <h4 className="font-medium">{match.display_name}</h4>
                              <p className="text-sm text-muted-foreground">{match.email}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Star className="h-4 w-4 text-yellow-500 fill-current" />
                            <span className="text-sm font-medium">
                              {Math.round(match.match_score * 100)}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex flex-wrap gap-1">
                          {match.user_tags.slice(0, 5).map((tag, tagIndex) => (
                            <span
                              key={tagIndex}
                              className="px-2 py-1 bg-muted rounded text-xs"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                        
                        {match.metadata_summary?.profile?.personal && (
                          <div className="text-sm text-muted-foreground">
                            <p>
                              {match.metadata_summary.profile.personal.location && 
                                `📍 ${match.metadata_summary.profile.personal.location}`
                              }
                              {match.metadata_summary.profile.personal.age_range && 
                                ` • 🎂 ${match.metadata_summary.profile.personal.age_range}`
                              }
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Finish Button */}
              <div className="text-center pt-6">
                <Button
                  onClick={handleFinishOnboarding}
                  size="lg"
                  className="bg-gradient-to-r from-primary to-primary/80"
                >
                  {language === 'zh' ? '完成引导，开始使用' : 'Finish Onboarding, Start Using'}
                  <CheckCircle className="h-4 w-4 ml-2" />
                </Button>
                <p className="text-sm text-muted-foreground mt-2">
                  {language === 'zh' ? '您可以随时在设置中修改这些信息' : 'You can modify this information anytime in settings'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 