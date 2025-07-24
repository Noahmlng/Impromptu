'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Switch } from '@/components/ui/switch'
import { useAppStore } from '@/lib/store'
import { User, UserMetadata, Language } from '@/lib/types'
import { User as UserIcon, Mail, Phone, MapPin, Calendar, Camera, Save, Edit3 } from 'lucide-react'

export default function ProfilePage() {
  const { language, user } = useAppStore()
  const [isEditing, setIsEditing] = useState(false)
  const [profile, setProfile] = useState({
    name: user?.name || 'Alex Chen',
    email: 'alex.chen@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    age: 28,
    bio: language === 'zh' 
      ? '热爱科技的产品经理，喜欢旅行和摄影。正在寻找志同道合的伙伴，无论是工作还是生活。'
      : 'Tech-savvy product manager who loves traveling and photography. Looking for like-minded partners for both work and life.',
    interests: ['Technology', 'Travel', 'Photography', 'Startups', 'Design'],
    preferences: {
      romanticMode: true,
      teamMode: true,
      publicProfile: true,
      emailNotifications: true
    }
  })

  const handleSave = () => {
    // Save profile logic here
    setIsEditing(false)
  }

  const handleInputChange = (field: string, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }))
  }

  const handlePreferenceChange = (preference: string, value: boolean) => {
    setProfile(prev => ({
      ...prev,
      preferences: { ...prev.preferences, [preference]: value }
    }))
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
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
                  {profile.name.charAt(0)}
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
              <h2 className="text-2xl font-semibold">{profile.name}</h2>
              <p className="text-muted-foreground">{profile.email}</p>
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
                <span className="font-medium capitalize">{user?.subscription || 'Free'}</span>
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
                    value={profile.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profile.name}</p>
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
                    value={profile.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profile.email}</p>
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
                    value={profile.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profile.phone}</p>
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
                    value={profile.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  />
                ) : (
                  <p className="px-3 py-2">{profile.location}</p>
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
                  value={profile.bio}
                  onChange={(e) => handleInputChange('bio', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                />
              ) : (
                <p className="px-3 py-2 text-sm leading-relaxed">{profile.bio}</p>
              )}
            </div>
          </div>

          {/* Interests */}
          <div className="bg-card rounded-lg p-6 space-y-4">
            <h3 className="text-xl font-semibold">
              {language === 'zh' ? '兴趣爱好' : 'Interests'}
            </h3>
            <div className="flex flex-wrap gap-2">
              {profile.interests.map((interest, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                >
                  {interest}
                </span>
              ))}
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
                  checked={profile.preferences.romanticMode}
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
                  checked={profile.preferences.teamMode}
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
                  checked={profile.preferences.publicProfile}
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
                  checked={profile.preferences.emailNotifications}
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