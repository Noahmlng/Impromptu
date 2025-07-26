'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/hooks/useAuth'
import { profile, auth, tags } from '@/lib/api'
import { User, UserMetadata, Language, UserTag } from '@/lib/types'
import { User as UserIcon, Mail, Phone, MapPin, Calendar, Camera, Save, Edit3, Upload, AlertCircle, CheckCircle, RefreshCw, Plus, ExternalLink, Trash2, Link, X, Image as ImageIcon } from 'lucide-react'
import { supabase } from '@/lib/supabase'

interface SocialLink {
  id: string
  platform: string
  url: string
  label: string
}

interface UserPhoto {
  id: string
  url: string
  file?: File
  isUploading?: boolean
}

export default function ProfilePage() {
  console.log('📄 [ProfilePage] Component rendering...')
  
  // 添加性能监控
  const authStartTime = useRef<number>(Date.now())
  const authEndTime = useRef<number>(0)
  
  // Auth check
  const { user: authUser, isLoading: authLoading } = useRequireAuth()
  
  // 监控认证完成时间
  useEffect(() => {
    if (!authLoading && authUser) {
      authEndTime.current = Date.now()
      const authDuration = authEndTime.current - authStartTime.current
      console.log(`⏱️ [ProfilePage] Authentication completed in ${authDuration}ms`)
      
      if (authDuration > 3000) {
        console.warn(`⚠️ [ProfilePage] Authentication took longer than expected: ${authDuration}ms`)
      }
    }
  }, [authLoading, authUser])
  
  console.log('📄 [ProfilePage] Auth state:', {
    authUser: authUser ? authUser.email : 'NO_USER',
    authLoading,
    userExists: !!authUser
  })
  
  const { 
    language, 
    userMetadata, 
    setUserMetadata,
    setIsLoading,
    setError,
    error,
    isLoading,
    clearError,
    userTags,
    setUserTags
  } = useAppStore()
  
  const [isEditing, setIsEditing] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [userPhotos, setUserPhotos] = useState<UserPhoto[]>([])
  const [socialLinks, setSocialLinks] = useState<SocialLink[]>([])
  const [newLink, setNewLink] = useState({ platform: '', url: '', label: '' })
  const [isAddingLink, setIsAddingLink] = useState(false)
  const [generatedTags, setGeneratedTags] = useState<string[]>([])
  const [isGeneratingTags, setIsGeneratingTags] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
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

  // 预定义的社媒平台
  const socialPlatforms = [
    { value: 'wechat', label: language === 'zh' ? '微信' : 'WeChat' },
    { value: 'weibo', label: language === 'zh' ? '微博' : 'Weibo' },
    { value: 'linkedin', label: 'LinkedIn' },
    { value: 'twitter', label: 'Twitter/X' },
    { value: 'instagram', label: 'Instagram' },
    { value: 'facebook', label: 'Facebook' },
    { value: 'github', label: 'GitHub' },
    { value: 'website', label: language === 'zh' ? '个人网站' : 'Website' },
    { value: 'other', label: language === 'zh' ? '其他' : 'Other' }
  ]
  const [dataLoading, setDataLoading] = useState(false) // 区分数据加载和认证加载

  // Load user data function
  const loadUserData = async () => {
    if (!authUser) return
    
    console.log('Loading user data for:', authUser.email)
    setDataLoading(true)
    setError(null) // 清除之前的错误
    
    try {
      // 使用后端API获取完整用户档案数据
      const backendResponse = await profile.getBackendMetadata()
      console.log('📥 [Profile] Backend response:', backendResponse)
      
      if (backendResponse.success && backendResponse.data) {
        const userData = backendResponse.data
        
        // 设置基本信息（从basic_info获取）
        const basicInfo = userData.basic_info || {}
        
        // 解析metadata - 后端返回的格式：{ profile: { personal: { content: {...} } } }
        const metadata = userData.metadata || {}
        const profileSection: any = metadata.profile || {}
        
        // 安全地获取content数据 - 每个字段都是对象，包含content属性
        const personalInfo = profileSection.personal || {}
        const contactInfo = profileSection.contact || {}  
        const preferencesInfo = profileSection.preferences || {}
        const photosInfo = profileSection.photos || {}
        
        const personalData = personalInfo.content || {}
        const contactData = contactInfo.content || {}
        const preferencesData = preferencesInfo.content || {}
        const photosData = photosInfo.content || []
        
        setProfileData({
          name: String(basicInfo.display_name || authUser.display_name || ''),
          email: String(basicInfo.email || authUser.email || ''),
          phone: String(basicInfo.phone || contactData.phone || ''),
          location: String(basicInfo.location || personalData.location || ''),
          age: String(personalData.age || ''),
          bio: String(basicInfo.bio || personalData.bio || ''),
          preferences: {
            romanticMode: preferencesData.romantic_mode !== false,
            teamMode: preferencesData.team_mode !== false,
            publicProfile: preferencesData.public_profile !== false,
            emailNotifications: preferencesData.email_notifications !== false
          }
        })
        
        // 设置照片数据
        if (Array.isArray(photosData) && photosData.length > 0) {
          setUserPhotos(photosData.map((photo: any, index: number) => ({
            id: photo.id || `photo_${index}`,
            url: photo.url || photo,
            isUploading: false
          })))
        } else if (authUser?.avatar_url) {
          // 如果没有照片数据但有头像，将头像作为第一张照片
          setUserPhotos([{
            id: 'avatar_photo',
            url: authUser.avatar_url,
            isUploading: false
          }])
        }
        
        // 设置标签 - 确保是数组格式
        const userTagsData = Array.isArray(userData.tags) ? userData.tags : []
        setUserTags(userTagsData)
        setGeneratedTags(userTagsData.map((tag: UserTag) => tag.tag_name || ''))
        
        // 设置到store中
        setUserMetadata(metadata)
        
        console.log('✅ [Profile] Data loaded successfully')
      } else {
        // 如果后端API失败，回退到Supabase直接获取
        console.warn('⚠️ [Profile] Backend API failed, falling back to direct Supabase access')
        
        // 获取完整的user_profile数据
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) throw new Error('Supabase user not found')
        
        // 获取用户的profile_id和完整profile数据
        const { data: userProfile } = await supabase
          .from('user_profile')
          .select('*')
          .eq('auth_user_id', user.id)
          .single()
        
        if (!userProfile) throw new Error('User profile not found')
        
        // Load metadata from Supabase directly
        const metadataResponse = await profile.getMetadata()
        if (metadataResponse.success) {
          // Load additional metadata for preferences and contact info
          const profileSection = metadataResponse.data.profile || {}
          const personalData = profileSection.personal?.content || {}
          const contactData = profileSection.contact?.content || {}
          const preferencesData = profileSection.preferences?.content || {}
          const socialLinksData = profileSection.social_links?.content || []
          const photosData = profileSection.photos?.content || []
          
          setUserMetadata(metadataResponse.data)
          setSocialLinks(socialLinksData)
          
          // 设置照片数据
          if (Array.isArray(photosData) && photosData.length > 0) {
            setUserPhotos(photosData.map((photo: any, index: number) => ({
              id: photo.id || `photo_${index}`,
              url: photo.url || photo,
              isUploading: false
            })))
          } else if (authUser?.avatar_url) {
            // 如果没有照片数据但有头像，将头像作为第一张照片
            setUserPhotos([{
              id: 'avatar_photo',
              url: authUser.avatar_url,
              isUploading: false
            }])
          }
          
          setProfileData({
            name: userProfile.display_name || authUser.display_name || '',
            email: userProfile.email || authUser.email || '',
            phone: userProfile.phone || contactData.phone || '',
            location: userProfile.location || personalData.location || '',
            age: personalData.age || '',
            bio: userProfile.bio || personalData.bio || '',
            preferences: {
              romanticMode: preferencesData.romantic_mode !== false,
              teamMode: preferencesData.team_mode !== false,
              publicProfile: preferencesData.public_profile !== false,
              emailNotifications: preferencesData.email_notifications !== false
            }
          })
        }
        
        // Load tags from Supabase directly
        const tagsResponse = await tags.getUserTags()
        if (tagsResponse.success && tagsResponse.data) {
          setUserTags(tagsResponse.data)
          setGeneratedTags(tagsResponse.data.map((tag: UserTag) => tag.tag_name))
        }
      }
      
    } catch (error: any) {
      console.error('Failed to load profile data:', error)
      setError(error.message || '加载个人资料失败，请稍后重试')
    } finally {
      setDataLoading(false)
    }
  }

  // Load user data on mount
  useEffect(() => {
    // 只有当authUser存在且不在认证加载中时才加载数据
    if (authUser && !authLoading) {
      loadUserData()
    }
  }, [authUser, authLoading])

  // 重试加载数据
  const retryLoadData = () => {
    if (authUser) {
      loadUserData()
    }
  }

  // 显示加载状态，等待认证检查完成
  if (authLoading) {
    console.log('⏳ [ProfilePage] Showing auth loading state')
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground mb-2">
            {language === 'zh' ? '验证身份中...' : 'Verifying authentication...'}
          </p>
          <p className="text-xs text-muted-foreground/60">
            {language === 'zh' ? '如果长时间无响应，请刷新页面' : 'Refresh if this takes too long'}
          </p>
        </div>
      </div>
    )
  }

  // 如果认证检查完成但没有用户信息，显示错误（这种情况下useRequireAuth应该已经重定向了）
  if (!authUser) {
    console.log('❌ [ProfilePage] No auth user found, showing error state')
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-muted-foreground mb-4">
            {language === 'zh' ? '用户信息加载失败' : 'Failed to load user information'}
          </p>
          <Button onClick={() => window.location.reload()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            {language === 'zh' ? '刷新页面' : 'Refresh Page'}
          </Button>
        </div>
      </div>
    )
  }

  const handleSave = async () => {
    if (!authUser) {
      setError('用户信息未加载，请刷新页面重试')
      return
    }
    
    console.log('🔍 [ProfilePage.handleSave] Starting save process...')
    console.log('👤 [ProfilePage.handleSave] Auth user:', authUser.email)
    
    setIsLoading(true)
    setSaveSuccess(false)
    setError(null)
    
    try {
      // 检查认证状态
      const { authToken, backendUser } = useAppStore.getState()
      console.log('🏪 [ProfilePage.handleSave] Store auth state:', { 
        hasToken: !!authToken, 
        hasBackendUser: !!backendUser 
      })
      
      // 1. 更新基本档案信息
      const profileUpdateData = {
        display_name: profileData.name,
        phone: profileData.phone,
        location: profileData.location,
        bio: profileData.bio
      }
      
      console.log('📝 [ProfilePage.handleSave] Updating profile via backend API:', profileUpdateData)
      
      try {
        const profileUpdateResponse = await profile.updateProfile(profileUpdateData)
        if (profileUpdateResponse.success) {
          console.log('✅ [ProfilePage.handleSave] Backend profile update successful')
        } else {
          console.error('❌ [ProfilePage.handleSave] Backend profile update failed:', profileUpdateResponse)
          throw new Error(profileUpdateResponse.message || '更新基本信息失败')
        }
      } catch (profileError: any) {
        console.error('❌ [ProfilePage.handleSave] Profile update failed:', profileError)
        
        // 如果是认证错误，提示用户重新登录
        if (profileError.message?.includes('401') || profileError.message?.includes('Unauthorized')) {
          throw new Error('登录状态已过期，请重新登录')
        }
        
        // 其他错误直接抛出
        throw new Error(profileError.message || '更新基本信息失败，请稍后重试')
      }

      // 2. 更新metadata
      const metadataEntries = [
        {
          section_type: 'profile',
          section_key: 'personal',
          content: {
            location: profileData.location,
            age: profileData.age,
            bio: profileData.bio,
            description: `我是${profileData.name}，${profileData.bio || '热爱生活的人'}。我来自${profileData.location || '未知地区'}，${profileData.age ? `今年${profileData.age}岁` : ''}。${profileData.preferences.teamMode ? '我希望找到优秀的团队合作伙伴。' : ''}${profileData.preferences.romanticMode ? '我在寻找人生伴侣。' : ''}`
          }
        },
        {
          section_type: 'profile',
          section_key: 'contact',
          content: {
            phone: profileData.phone,
            email: profileData.email
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
        },
        {
          section_type: 'profile',
          section_key: 'social_links',
          content: socialLinks
        },
        {
          section_type: 'profile',
          section_key: 'photos',
          content: userPhotos.filter(photo => !photo.file).map(photo => ({
            id: photo.id,
            url: photo.url
          }))
        },
        {
          section_type: 'user_request',
          section_key: 'description',
          content: {
            description: `我是${profileData.name}，${profileData.bio || '一个热爱生活的人'}。我目前居住在${profileData.location || '某个城市'}。我的联系方式是${profileData.phone || '暂未提供'}。我希望通过这个平台${profileData.preferences.teamMode ? '找到志同道合的团队合作伙伴' : ''}${profileData.preferences.teamMode && profileData.preferences.romanticMode ? '，同时也' : ''}${profileData.preferences.romanticMode ? '寻找到合适的人生伴侣' : ''}。`,
            request_type: profileData.preferences.teamMode && profileData.preferences.romanticMode ? '找队友和找对象' : profileData.preferences.teamMode ? '找队友' : profileData.preferences.romanticMode ? '找对象' : '未指定',
            detailed_bio: profileData.bio,
            location_preference: profileData.location,
            contact_info: {
              phone: profileData.phone,
              email: profileData.email
            }
          }
        }
      ]

      console.log('📝 [ProfilePage.handleSave] Updating metadata via backend API')
      
      try {
        const metadataResponse = await profile.batchUpdateMetadata(metadataEntries)
        if (metadataResponse.success) {
          console.log('✅ [ProfilePage.handleSave] Backend metadata update successful')
        } else {
          console.error('❌ [ProfilePage.handleSave] Backend metadata update failed:', metadataResponse)
          throw new Error(metadataResponse.error || '更新详细信息失败')
        }
      } catch (metadataError: any) {
        console.error('❌ [ProfilePage.handleSave] Metadata update failed:', metadataError)
        
        // 如果是认证错误，提示用户重新登录
        if (metadataError.message?.includes('401') || metadataError.message?.includes('Unauthorized')) {
          throw new Error('登录状态已过期，请重新登录')
        }
        
        // 其他错误给出提示但不阻止整个保存流程
        console.warn('⚠️ [ProfilePage.handleSave] Metadata update failed, but continuing with save process')
      }
      
      // 等待一下确保数据已经保存
      console.log('⏳ [ProfilePage.handleSave] Waiting for metadata to be saved...')
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 3. 生成标签（可选，如果后端可用的话）
      let matchingTypes: ('找队友' | '找对象')[] = []
      if (profileData.preferences.teamMode) {
        matchingTypes.push('找队友')
      }
      if (profileData.preferences.romanticMode) {
        matchingTypes.push('找对象')
      }
      
      console.log('🔍 [ProfilePage.handleSave] 用户偏好设置:', {
        teamMode: profileData.preferences.teamMode,
        romanticMode: profileData.preferences.romanticMode,
        matchingTypes
      })
      
      if (matchingTypes.length > 0) {
        try {
          console.log('🏷️ [ProfilePage.handleSave] Attempting tag generation for:', matchingTypes[0])
          console.log('🔑 [ProfilePage.handleSave] Current auth state before tag generation:', {
            authUser: !!authUser,
            authToken: !!useAppStore.getState().authToken,
            backendUser: !!useAppStore.getState().backendUser
          })
          
          const tagGenerationResponse = await tags.generate(matchingTypes[0])
          
          console.log('📥 [ProfilePage.handleSave] Tag generation response:', {
            success: tagGenerationResponse.success,
            message: tagGenerationResponse.message,
            dataExists: !!tagGenerationResponse.data,
            tagsCount: tagGenerationResponse.data?.generated_tags?.length || 0
          })
          
          if (tagGenerationResponse.success) {
            setUserTags(tagGenerationResponse.data.generated_tags)
            setGeneratedTags(tagGenerationResponse.data.generated_tags.map((tag: UserTag) => tag.tag_name))
            console.log('✅ [ProfilePage.handleSave] Tags generated successfully:', {
              tagsCount: tagGenerationResponse.data.generated_tags.length,
              tagNames: tagGenerationResponse.data.generated_tags.map((tag: UserTag) => tag.tag_name).slice(0, 5)
            })
          } else {
            console.warn('⚠️ [ProfilePage.handleSave] Tag generation failed:', tagGenerationResponse.message)
            console.warn('📊 [ProfilePage.handleSave] Full response:', tagGenerationResponse)
          }
        } catch (tagError: any) {
          console.error('❌ [ProfilePage.handleSave] Tag generation error (non-critical):', tagError.message)
          console.error('📊 [ProfilePage.handleSave] Full error:', tagError)
          console.error('🔍 [ProfilePage.handleSave] Error details:', {
            name: tagError.name,
            message: tagError.message,
            stack: tagError.stack?.split('\n').slice(0, 3)
          })
        }
      } else {
        console.log('ℹ️ [ProfilePage.handleSave] No matching types enabled, skipping tag generation')
      }
      
      setSaveSuccess(true)
      setIsEditing(false)
      console.log('🎉 [ProfilePage.handleSave] Save completed successfully')
      
      // Auto-hide success message
      setTimeout(() => setSaveSuccess(false), 3000)
      
    } catch (error: any) {
      console.error('❌ [ProfilePage.handleSave] Save failed:', error)
      let errorMessage = error.message || '保存失败，请稍后重试'
      
      // 针对常见错误提供更友好的提示
      if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        errorMessage = '登录状态已过期，请重新登录'
      } else if (error.message?.includes('网络')) {
        errorMessage = '网络连接失败，请检查网络设置'
      } else if (error.message?.includes('500')) {
        errorMessage = '服务器错误，请稍后重试'
      } else if (error.message?.includes('token')) {
        errorMessage = '认证信息异常，请重新登录'
      }
      
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  // Social Links Management Functions
  const addSocialLink = () => {
    if (!newLink.platform || !newLink.url) {
      setError(language === 'zh' ? '请填写平台和链接' : 'Please fill in platform and URL')
      return
    }

    const link: SocialLink = {
      id: Date.now().toString(),
      platform: newLink.platform,
      url: newLink.url,
      label: newLink.label || newLink.platform
    }

    setSocialLinks(prev => [...prev, link])
    setNewLink({ platform: '', url: '', label: '' })
    setIsAddingLink(false)
    setError(null)
  }

  const removeSocialLink = (id: string) => {
    setSocialLinks(prev => prev.filter(link => link.id !== id))
  }

  const updateSocialLink = (id: string, updatedLink: Partial<SocialLink>) => {
    setSocialLinks(prev => prev.map(link => 
      link.id === id ? { ...link, ...updatedLink } : link
    ))
  }

  // 照片管理函数
  const handlePhotosUpload = () => {
    if (userPhotos.length >= 9) {
      setError(language === 'zh' ? '最多只能上传9张照片' : 'Maximum 9 photos allowed')
      return
    }
    fileInputRef.current?.click()
  }

  const handleFilesChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    if (!files.length) return

    // 检查照片数量限制
    const availableSlots = 9 - userPhotos.length
    if (files.length > availableSlots) {
      setError(language === 'zh' ? `最多还能上传${availableSlots}张照片` : `Can only upload ${availableSlots} more photos`)
      return
    }

    // 验证文件
    const validFiles = files.filter(file => {
      if (!file.type.startsWith('image/')) {
        setError(language === 'zh' ? '请选择图片文件' : 'Please select image files')
        return false
      }
      if (file.size > 5 * 1024 * 1024) {
        setError(language === 'zh' ? '图片大小不能超过5MB' : 'Image size cannot exceed 5MB')
        return false
      }
      return true
    })

    if (validFiles.length === 0) return

    setError(null)

    // 为每个文件创建预览
    const newPhotos: UserPhoto[] = []
    
    for (const file of validFiles) {
      const photoId = `temp_${Date.now()}_${Math.random()}`
      
      // 创建预览URL
      const previewUrl = URL.createObjectURL(file)
      
      const newPhoto: UserPhoto = {
        id: photoId,
        url: previewUrl,
        file: file,
        isUploading: true
      }
      
      newPhotos.push(newPhoto)
    }

    // 添加到照片列表
    setUserPhotos(prev => [...prev, ...newPhotos])

    // 模拟上传过程
    for (const photo of newPhotos) {
      try {
        // 这里应该调用实际的上传API
        // const formData = new FormData()
        // formData.append('photo', photo.file!)
        // const response = await profile.uploadPhoto(formData)
        
        // 模拟上传延迟
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // 上传成功，更新照片状态
        setUserPhotos(prev => prev.map(p => 
          p.id === photo.id 
            ? { ...p, isUploading: false }
            : p
        ))
        
      } catch (error: any) {
        console.error('Photo upload failed:', error)
        // 上传失败，移除该照片
        setUserPhotos(prev => prev.filter(p => p.id !== photo.id))
        setError(error.message || 'Failed to upload photo')
      }
    }
  }

  const removePhoto = (photoId: string) => {
    setUserPhotos(prev => {
      const photo = prev.find(p => p.id === photoId)
      if (photo?.url.startsWith('blob:')) {
        URL.revokeObjectURL(photo.url)
      }
      return prev.filter(p => p.id !== photoId)
    })
  }

  const reorderPhotos = (dragIndex: number, hoverIndex: number) => {
    setUserPhotos(prev => {
      const newPhotos = [...prev]
      const dragPhoto = newPhotos[dragIndex]
      newPhotos.splice(dragIndex, 1)
      newPhotos.splice(hoverIndex, 0, dragPhoto)
      return newPhotos
    })
  }
      
  const generateTags = async (requestType: '找队友' | '找对象') => {
    if (!authUser) return
    
    setIsGeneratingTags(true)
    setError(null)
    
    try {
      const response = await tags.generate(requestType)
      if (response.success) {
        setUserTags(response.data.generated_tags)
        setGeneratedTags(response.data.generated_tags.map((tag: UserTag) => tag.tag_name))
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 3000)
      }
    } catch (error: any) {
      setError(error.message || '生成标签失败，请稍后重试')
    } finally {
      setIsGeneratingTags(false)
    }
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

  // 显示数据加载状态
  if (dataLoading) {
    console.log('📊 [ProfilePage] Showing data loading state')
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">
            {language === 'zh' ? '加载个人资料中...' : 'Loading profile...'}
          </p>
        </div>
      </div>
    )
  }

  console.log('✅ [ProfilePage] Rendering main profile content')
  return (
    <div className="max-w-4xl mx-auto space-y-8">
        {/* Status Messages */}
        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <span className="text-sm text-destructive">{error}</span>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={retryLoadData}>
                <RefreshCw className="h-4 w-4 mr-2" />
                {language === 'zh' ? '重试' : 'Retry'}
              </Button>
              <Button variant="outline" size="sm" onClick={clearError}>
                {language === 'zh' ? '关闭' : 'Close'}
              </Button>
            </div>
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
          onClick={isEditing ? handleSave : () => setIsEditing(true)}
          variant={isEditing ? 'default' : 'outline'}
          disabled={isLoading}
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
        {/* Photos and Basic Info */}
        <div className="md:col-span-1 space-y-6">
          {/* 照片展示区域 */}
          <div className="text-center space-y-4">
            <h3 className="font-semibold text-lg">
              {language === 'zh' ? '我的照片' : 'My Photos'}
            </h3>
            
            {/* 照片网格 */}
            <div className="grid grid-cols-3 gap-2">
              {/* 现有照片 */}
              {userPhotos.map((photo, index) => (
                <div key={photo.id} className="relative aspect-square group">
                  <div className="w-full h-full rounded-lg overflow-hidden bg-muted">
                    <img 
                      src={photo.url} 
                      alt={`Photo ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  {/* 上传中状态 */}
                  {photo.isUploading && (
                    <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                      <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    </div>
                  )}
                  
                  {/* 删除按钮 */}
                  {isEditing && !photo.isUploading && (
                    <Button
                      size="icon"
                      variant="destructive"
                      className="absolute -top-2 -right-2 h-6 w-6 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => removePhoto(photo.id)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                  
                  {/* 主照片标识 */}
                  {index === 0 && (
                    <div className="absolute bottom-1 left-1 bg-primary text-primary-foreground text-xs px-1 py-0.5 rounded">
                      {language === 'zh' ? '主照片' : 'Main'}
                    </div>
                  )}
                </div>
              ))}
              
              {/* 添加照片按钮 */}
              {userPhotos.length < 9 && isEditing && (
                <button
                  onClick={handlePhotosUpload}
                  className="aspect-square rounded-lg border-2 border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5 transition-colors flex flex-col items-center justify-center gap-1 text-muted-foreground hover:text-primary"
                >
                  <Plus className="h-6 w-6" />
                  <span className="text-xs">
                    {language === 'zh' ? '添加' : 'Add'}
                  </span>
                </button>
              )}
              
              {/* 空白占位 */}
              {Array.from({ length: 9 - userPhotos.length - (isEditing && userPhotos.length < 9 ? 1 : 0) }).map((_, index) => (
                <div key={`empty-${index}`} className="aspect-square rounded-lg bg-muted/30" />
              ))}
            </div>
            
            {/* 上传按钮和说明 */}
            {isEditing && (
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePhotosUpload}
                  disabled={userPhotos.length >= 9}
                  className="w-full"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {language === 'zh' ? '上传照片' : 'Upload Photos'} 
                  <span className="ml-1 text-xs">({userPhotos.length}/9)</span>
                </Button>
                <p className="text-xs text-muted-foreground">
                  {language === 'zh' 
                    ? '支持 JPG、PNG 格式，最大 5MB，最多 9 张' 
                    : 'Support JPG, PNG format, max 5MB, up to 9 photos'
                  }
                </p>
              </div>
            )}

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFilesChange}
              className="hidden"
            />
            
            <div>
              <h2 className="text-2xl font-semibold">{profileData.name || authUser?.display_name}</h2>
              <p className="text-muted-foreground">{profileData.email || authUser?.email}</p>
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
                <span className="font-medium">0</span>
              </div>
              <div className="flex justify-between">
                <span>{language === 'zh' ? '订阅等级' : 'Subscription'}</span>
                <span className="font-medium capitalize">{authUser?.subscription_type || 'Free'}</span>
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

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center space-x-2">
                  <Calendar className="h-4 w-4" />
                  <span>{language === 'zh' ? '年龄' : 'Age'}</span>
                </label>
                {isEditing ? (
                  <input
                    type="number"
                    value={profileData.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profileData.age}</p>
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

          {/* Social Links */}
          <div className="bg-card rounded-lg p-6 space-y-4">
            <h3 className="text-xl font-semibold">
              {language === 'zh' ? '社媒链接' : 'Social Links'}
            </h3>
            <div className="space-y-3">
              {socialLinks.map(link => (
                <div key={link.id} className="space-y-2">
                  {isEditing ? (
                    <div className="bg-muted/50 p-3 rounded-md space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                        <select
                          value={link.platform}
                          onChange={(e) => updateSocialLink(link.id, { platform: e.target.value })}
                          className="px-3 py-2 border border-input rounded-md bg-background text-sm"
                        >
                          {socialPlatforms.map(platform => (
                            <option key={platform.value} value={platform.value}>
                              {platform.label}
                            </option>
                          ))}
                        </select>
                        <input
                          type="text"
                          placeholder={language === 'zh' ? '显示名称' : 'Display Name'}
                          value={link.label}
                          onChange={(e) => updateSocialLink(link.id, { label: e.target.value })}
                          className="px-3 py-2 border border-input rounded-md bg-background text-sm"
                        />
                        <input
                          type="url"
                          placeholder={language === 'zh' ? '链接地址' : 'URL'}
                          value={link.url}
                          onChange={(e) => updateSocialLink(link.id, { url: e.target.value })}
                          className="px-3 py-2 border border-input rounded-md bg-background text-sm"
                        />
                      </div>
                      <div className="flex justify-end">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeSocialLink(link.id)}
                          className="text-destructive hover:text-destructive/80"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          {language === 'zh' ? '删除' : 'Delete'}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between bg-muted/50 p-3 rounded-md">
                      <div className="flex items-center space-x-3">
                        <Link className="h-5 w-5 text-muted-foreground" />
                        <span className="font-medium">{link.label}</span>
                        <span className="text-sm text-muted-foreground">
                          ({socialPlatforms.find(p => p.value === link.platform)?.label || link.platform})
                        </span>
                      </div>
                      <a 
                        href={link.url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-primary hover:text-primary/80 flex items-center space-x-1"
                      >
                        <ExternalLink className="h-4 w-4" />
                        <span className="text-sm">
                          {language === 'zh' ? '访问' : 'Visit'}
                        </span>
                      </a>
                    </div>
                  )}
                </div>
              ))}

              {/* Add New Link Form */ }
              {isEditing && isAddingLink && (
                <div className="bg-muted/30 p-4 rounded-md border-2 border-dashed border-muted-foreground/30 space-y-3">
                  <h4 className="font-medium text-sm">
                    {language === 'zh' ? '添加新链接' : 'Add New Link'}
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <select
                      value={newLink.platform}
                      onChange={(e) => setNewLink(prev => ({ ...prev, platform: e.target.value }))}
                      className="px-3 py-2 border border-input rounded-md bg-background text-sm"
                    >
                      <option value="">
                        {language === 'zh' ? '选择平台' : 'Select Platform'}
                      </option>
                      {socialPlatforms.map(platform => (
                        <option key={platform.value} value={platform.value}>
                          {platform.label}
                        </option>
                      ))}
                    </select>
                    <input
                      type="text"
                      placeholder={language === 'zh' ? '显示名称' : 'Display Name'}
                      value={newLink.label}
                      onChange={(e) => setNewLink(prev => ({ ...prev, label: e.target.value }))}
                      className="px-3 py-2 border border-input rounded-md bg-background text-sm"
                    />
                    <input
                      type="url"
                      placeholder={language === 'zh' ? '链接地址' : 'URL'}
                      value={newLink.url}
                      onChange={(e) => setNewLink(prev => ({ ...prev, url: e.target.value }))}
                      className="px-3 py-2 border border-input rounded-md bg-background text-sm"
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setIsAddingLink(false)
                        setNewLink({ platform: '', url: '', label: '' })
                      }}
                    >
                      {language === 'zh' ? '取消' : 'Cancel'}
                    </Button>
                    <Button
                      variant="default"
                      size="sm"
                      onClick={addSocialLink}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      {language === 'zh' ? '添加' : 'Add'}
                    </Button>
                  </div>
                </div>
              )}

              {/* Add Link Button */}
              {isEditing && !isAddingLink && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsAddingLink(true)}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {language === 'zh' ? '添加社媒链接' : 'Add Social Link'}
                </Button>
              )}

              {/* Empty State */}
              {socialLinks.length === 0 && !isEditing && (
                <div className="text-center py-8 text-muted-foreground">
                  <Link className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="text-sm">
                    {language === 'zh' ? '暂无社媒链接' : 'No social links yet'}
                  </p>
                </div>
              )}
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