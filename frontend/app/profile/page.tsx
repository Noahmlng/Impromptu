'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Switch } from '@/components/ui/switch'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/hooks/useAuth'
import { profile, tags } from '@/lib/api'
import { User, UserMetadata, Language } from '@/lib/types'
import { User as UserIcon, Mail, Phone, MapPin, Calendar, Camera, Save, Edit3, Tag, AlertCircle, CheckCircle } from 'lucide-react'

export default function ProfilePage() {
  // Auth check
  const { user: authUser, isLoading: authLoading } = useRequireAuth()
  
  const { 
    language, 
    user, 
    backendUser, 
    userMetadata, 
    userTags,
    setUserMetadata,
    setUserTags,
    setIsLoading,
    setError,
    error,
    isLoading
  } = useAppStore()
  
  const [isEditing, setIsEditing] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    age: '',
    bio: '',
    preferences: {
      romanticMode: true,
      teamMode: true,
      publicProfile: true,
      emailNotifications: true
    }
  })
  const [generatedTags, setGeneratedTags] = useState<string[]>([])

  // Load user data on mount
  useEffect(() => {
    const loadUserData = async () => {
      if (!authUser) return
      
      setIsLoading(true)
      try {
        // Load user profile (includes basic info from user_profile + personal metadata)
        const profileResponse = await profile.getProfile()
        if (profileResponse.success) {
          const userData = profileResponse.data
          
          // Load additional metadata for preferences and contact info
          const metadataResponse = await profile.getMetadata()
          const profileSection = metadataResponse.success ? metadataResponse.data.profile || {} : {}
          const contactData = profileSection.contact?.content || {}
          const preferencesData = profileSection.preferences?.content || {}
          
          setUserMetadata(metadataResponse.success ? metadataResponse.data : {})
          
          setProfileData({
            name: userData.display_name || '',
            email: userData.email || '',
            phone: contactData.phone || '',
            location: userData.location || '',  // Now from user_profile + personal metadata
            age: userData.age || '',            // Now from user_profile + personal metadata
            bio: userData.bio || '',            // Now from user_profile + personal metadata
            preferences: {
              romanticMode: preferencesData.romantic_mode !== false,
              teamMode: preferencesData.team_mode !== false,
              publicProfile: preferencesData.public_profile !== false,
              emailNotifications: preferencesData.email_notifications !== false
            }
          })
        }
        
        // Load tags
        const tagsResponse = await tags.getUserTags()
        if (tagsResponse.success && tagsResponse.data) {
          setUserTags(tagsResponse.data)
          setGeneratedTags(tagsResponse.data.map(tag => tag.tag_name))
        }
        
      } catch (error: any) {
        setError(error.message || 'Failed to load profile data')
      } finally {
        setIsLoading(false)
      }
    }

    loadUserData()
  }, [authUser, backendUser])

  const handleSave = async () => {
    if (!authUser) return
    
    setIsLoading(true)
    setSaveSuccess(false)
    setError(null)
    
    try {
      // Save basic profile info (bio, location, age) using the new profile API
      await profile.updateProfile({
        bio: profileData.bio,
        location: profileData.location,
        age: profileData.age
      })

      // Save other metadata (contact info and preferences)
      const metadataEntries = [
        {
          section_type: 'profile',
          section_key: 'contact',
          content: {
            phone: profileData.phone
          }
        },
        {
          section_type: 'profile',
          section_key: 'preferences',
          content: {
            romantic_mode: profileData.preferences.romanticMode,
            team_mode: profileData.preferences.teamMode,
            public_profile: profileData.preferences.publicProfile,
            email_notifications: profileData.preferences.emailNotifications
          }
        }
      ]

      // Save additional metadata
      await profile.batchUpdateMetadata(metadataEntries)
      
      setSaveSuccess(true)
    setIsEditing(false)
      
      // Auto-hide success message
      setTimeout(() => setSaveSuccess(false), 3000)
      
    } catch (error: any) {
      setError(error.message || 'Failed to save profile')
    } finally {
      setIsLoading(false)
    }
  }

  const generateTags = async (requestType: '找队友' | '找对象') => {
    if (!authUser) return
    
    setIsLoading(true)
    try {
      const response = await tags.generate(requestType)
      if (response.success) {
        setUserTags(response.data.generated_tags)
        setGeneratedTags(response.data.generated_tags.map(tag => tag.tag_name))
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 3000)
      }
    } catch (error: any) {
      setError(error.message || 'Failed to generate tags')
    } finally {
      setIsLoading(false)
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const handleInputChange = (field: string, value: any) => {
    setProfileData(prev => ({ ...prev, [field]: value }))
  }

  const handlePreferenceChange = (preference: string, value: boolean) => {
    setProfileData(prev => ({
      ...prev,
      preferences: { ...prev.preferences, [preference]: value }
    }))
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
        {/* Status Messages */}
        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-destructive" />
            <span className="text-sm text-destructive">{error}</span>
          </div>
        )}
        
        {saveSuccess && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-sm text-green-600">
              {language === 'zh' ? '保存成功！' : 'Saved successfully!'}
            </span>
          </div>
        )}
        
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">
          {language === 'zh' ? '个人资料' : 'Profile'}
        </h1>
        <Button
          onClick={() => setIsEditing(!isEditing)}
          variant={isEditing ? 'default' : 'outline'}
        >
          {isEditing ? (
            <>
              <Save className="h-4 w-4 mr-2" />
              {language === 'zh' ? '保存' : 'Save'}
            </>
          ) : (
            <>
              <Edit3 className="h-4 w-4 mr-2" />
              {language === 'zh' ? '编辑' : 'Edit'}
            </>
          )}
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Profile Image and Basic Info */}
        <div className="md:col-span-1 space-y-6">
          <div className="text-center space-y-4">
            <div className="relative">
              <Avatar className="h-32 w-32 mx-auto">
                <AvatarImage src={user?.avatar} />
                <AvatarFallback className="text-2xl">
                  {(profileData.name || backendUser?.display_name || 'U').charAt(0)}
                </AvatarFallback>
              </Avatar>
              {isEditing && (
                <Button
                  size="icon"
                  className="absolute bottom-0 right-1/2 translate-x-1/2 translate-y-1/2 rounded-full"
                >
                  <Camera className="h-4 w-4" />
                </Button>
              )}
            </div>
            <div>
              <h2 className="text-2xl font-semibold">{profileData.name || backendUser?.display_name}</h2>
              <p className="text-muted-foreground">{profileData.email || backendUser?.email}</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-card rounded-lg p-6 space-y-4">
            <h3 className="font-semibold">
              {language === 'zh' ? '账户统计' : 'Account Stats'}
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>{language === 'zh' ? '积分余额' : 'Credits'}</span>
                <span className="font-medium">{user?.credits || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>{language === 'zh' ? '订阅等级' : 'Subscription'}</span>
                <span className="font-medium capitalize">{backendUser?.subscription_type || user?.subscription || 'Free'}</span>
              </div>
              <div className="flex justify-between">
                <span>{language === 'zh' ? '匹配数量' : 'Matches'}</span>
                <span className="font-medium">12</span>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Details */}
        <div className="md:col-span-2 space-y-6">
          {/* Basic Information */}
          <div className="bg-card rounded-lg p-6 space-y-4">
            <h3 className="text-xl font-semibold">
              {language === 'zh' ? '基本信息' : 'Basic Information'}
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <UserIcon className="h-4 w-4" />
                  <span>{language === 'zh' ? '姓名' : 'Name'}</span>
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={profileData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profileData.name}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <Mail className="h-4 w-4" />
                  <span>{language === 'zh' ? '邮箱' : 'Email'}</span>
                </label>
                {isEditing ? (
                  <input
                    type="email"
                    value={profileData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profileData.email}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <Phone className="h-4 w-4" />
                  <span>{language === 'zh' ? '电话' : 'Phone'}</span>
                </label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={profileData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profileData.phone}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>{language === 'zh' ? '位置' : 'Location'}</span>
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={profileData.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profileData.location}</p>
                )}
              </div>
            </div>

            {/* Bio */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                {language === 'zh' ? '个人简介' : 'Bio'}
              </label>
              {isEditing ? (
                <textarea
                  value={profileData.bio}
                  onChange={(e) => handleInputChange('bio', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                />
              ) : (
                <p className="px-3 py-2 text-sm leading-relaxed">{profileData.bio}</p>
              )}
            </div>
          </div>

          {/* Tags */}
          <div className="bg-card rounded-lg p-6 space-y-4">
            <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold">
                {language === 'zh' ? '个人标签' : 'Tags'}
            </h3>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => generateTags('找队友')}
                  disabled={isLoading}
                >
                  <Tag className="h-4 w-4 mr-2" />
                  {language === 'zh' ? '生成队友标签' : 'Generate Team Tags'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => generateTags('找对象')}
                  disabled={isLoading}
                >
                  <Tag className="h-4 w-4 mr-2" />
                  {language === 'zh' ? '生成浪漫标签' : 'Generate Romantic Tags'}
                </Button>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {generatedTags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
              {generatedTags.length === 0 && (
                <p className="text-muted-foreground text-sm">
                  {language === 'zh' ? '暂无标签，点击按钮生成' : 'No tags yet, click button to generate'}
                </p>
              )}
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-card rounded-lg p-6 space-y-4">
            <h3 className="text-xl font-semibold">
              {language === 'zh' ? '偏好设置' : 'Preferences'}
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="font-medium">
                    {language === 'zh' ? '启用浪漫模式' : 'Enable Romantic Mode'}
                  </label>
                  <p className="text-sm text-muted-foreground">
                    {language === 'zh' 
                      ? '允许其他用户在浪漫匹配中找到您'
                      : 'Allow others to find you in romantic matching'
                    }
                  </p>
                </div>
                <Switch
                  checked={profileData.preferences.romanticMode}
                  onCheckedChange={(value) => handlePreferenceChange('romanticMode', value)}
                  disabled={!isEditing}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="font-medium">
                    {language === 'zh' ? '启用组队模式' : 'Enable Team Mode'}
                  </label>
                  <p className="text-sm text-muted-foreground">
                    {language === 'zh' 
                      ? '允许其他用户在团队匹配中找到您'
                      : 'Allow others to find you in team matching'
                    }
                  </p>
                </div>
                <Switch
                  checked={profileData.preferences.teamMode}
                  onCheckedChange={(value) => handlePreferenceChange('teamMode', value)}
                  disabled={!isEditing}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="font-medium">
                    {language === 'zh' ? '公开资料' : 'Public Profile'}
                  </label>
                  <p className="text-sm text-muted-foreground">
                    {language === 'zh' 
                      ? '让您的基本信息对其他用户可见'
                      : 'Make your basic information visible to other users'
                    }
                  </p>
                </div>
                <Switch
                  checked={profileData.preferences.publicProfile}
                  onCheckedChange={(value) => handlePreferenceChange('publicProfile', value)}
                  disabled={!isEditing}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="font-medium">
                    {language === 'zh' ? '邮件通知' : 'Email Notifications'}
                  </label>
                  <p className="text-sm text-muted-foreground">
                    {language === 'zh' 
                      ? '接收新匹配和消息的邮件通知'
                      : 'Receive email notifications for new matches and messages'
                    }
                  </p>
                </div>
                <Switch
                  checked={profileData.preferences.emailNotifications}
                  onCheckedChange={(value) => handlePreferenceChange('emailNotifications', value)}
                  disabled={!isEditing}
                />
              </div>
            </div>
          </div>

          {/* Save Button for Mobile */}
          {isEditing && (
            <div className="md:hidden">
              <Button onClick={handleSave} className="w-full" size="lg">
                <Save className="h-4 w-4 mr-2" />
                {language === 'zh' ? '保存更改' : 'Save Changes'}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 