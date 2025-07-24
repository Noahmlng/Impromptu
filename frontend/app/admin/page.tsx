'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAppStore } from '@/lib/store'
import { 
  Users, 
  MessageSquare, 
  BarChart3, 
  Settings, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  Ban,
  UserCheck
} from 'lucide-react'

export default function AdminPage() {
  const { language } = useAppStore()
  const [activeTab, setActiveTab] = useState('dashboard')

  const stats = [
    {
      title: language === 'zh' ? '总用户数' : 'Total Users',
      value: '12,456',
      change: '+12%',
      icon: Users,
      color: 'text-blue-600'
    },
    {
      title: language === 'zh' ? '匹配成功数' : 'Successful Matches',
      value: '3,421',
      change: '+8%',
      icon: CheckCircle,
      color: 'text-green-600'
    },
    {
      title: language === 'zh' ? '待审核内容' : 'Pending Reviews',
      value: '89',
      change: '-5%',
      icon: Clock,
      color: 'text-orange-600'
    },
    {
      title: language === 'zh' ? '系统警告' : 'System Alerts',
      value: '3',
      change: 'stable',
      icon: AlertTriangle,
      color: 'text-red-600'
    }
  ]

  const recentUsers = [
    { id: 1, name: 'Alice Chen', email: 'alice@example.com', status: 'active', joinDate: '2024-01-15' },
    { id: 2, name: 'Bob Wang', email: 'bob@example.com', status: 'pending', joinDate: '2024-01-14' },
    { id: 3, name: 'Carol Li', email: 'carol@example.com', status: 'active', joinDate: '2024-01-13' },
    { id: 4, name: 'David Zhang', email: 'david@example.com', status: 'suspended', joinDate: '2024-01-12' },
  ]

  const pendingContent = [
    { id: 1, user: 'Alice Chen', type: 'profile', content: '个人简介更新', status: 'pending', date: '2024-01-15' },
    { id: 2, user: 'Bob Wang', type: 'image', content: '头像上传', status: 'pending', date: '2024-01-14' },
    { id: 3, user: 'Carol Li', type: 'message', content: '匹配消息', status: 'approved', date: '2024-01-13' },
  ]

  const tabs = [
    { id: 'dashboard', name: language === 'zh' ? '仪表板' : 'Dashboard', icon: BarChart3 },
    { id: 'users', name: language === 'zh' ? '用户管理' : 'User Management', icon: Users },
    { id: 'content', name: language === 'zh' ? '内容审核' : 'Content Review', icon: MessageSquare },
    { id: 'settings', name: language === 'zh' ? '系统设置' : 'System Settings', icon: Settings },
  ]

  const getStatusBadge = (status: string) => {
    const variants = {
      active: { variant: 'default' as const, text: language === 'zh' ? '活跃' : 'Active' },
      pending: { variant: 'secondary' as const, text: language === 'zh' ? '待审核' : 'Pending' },
      suspended: { variant: 'destructive' as const, text: language === 'zh' ? '已暂停' : 'Suspended' },
      approved: { variant: 'default' as const, text: language === 'zh' ? '已通过' : 'Approved' },
    }
    return variants[status as keyof typeof variants] || variants.pending
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-2">
            <Shield className="h-8 w-8 text-primary" />
            <span>{language === 'zh' ? '后台管理系统' : 'Admin Dashboard'}</span>
          </h1>
          <p className="text-muted-foreground mt-2">
            {language === 'zh' 
              ? '管理用户、审核内容、监控系统状态'
              : 'Manage users, review content, and monitor system status'
            }
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-8">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">
                    <span className={stat.change.startsWith('+') ? 'text-green-600' : stat.change.startsWith('-') ? 'text-red-600' : 'text-gray-600'}>
                      {stat.change}
                    </span>
                    {' '}{language === 'zh' ? '较上月' : 'from last month'}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{language === 'zh' ? '最新用户' : 'Recent Users'}</CardTitle>
                <CardDescription>
                  {language === 'zh' ? '最近注册的用户' : 'Recently registered users'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{user.name}</p>
                        <p className="text-sm text-muted-foreground">{user.email}</p>
                      </div>
                      <div className="text-right">
                        <Badge variant={getStatusBadge(user.status).variant}>
                          {getStatusBadge(user.status).text}
                        </Badge>
                        <p className="text-xs text-muted-foreground mt-1">{user.joinDate}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{language === 'zh' ? '待审核内容' : 'Pending Content'}</CardTitle>
                <CardDescription>
                  {language === 'zh' ? '需要人工审核的内容' : 'Content requiring manual review'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {pendingContent.map((item) => (
                    <div key={item.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{item.user}</p>
                        <p className="text-sm text-muted-foreground">{item.content}</p>
                      </div>
                      <div className="text-right flex flex-col items-end space-y-1">
                        <Badge variant={getStatusBadge(item.status).variant}>
                          {getStatusBadge(item.status).text}
                        </Badge>
                        <p className="text-xs text-muted-foreground">{item.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold">{language === 'zh' ? '用户管理' : 'User Management'}</h2>
            <Button>
              <UserCheck className="h-4 w-4 mr-2" />
              {language === 'zh' ? '批量操作' : 'Bulk Actions'}
            </Button>
          </div>
          
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-4">{language === 'zh' ? '用户' : 'User'}</th>
                      <th className="text-left p-4">{language === 'zh' ? '邮箱' : 'Email'}</th>
                      <th className="text-left p-4">{language === 'zh' ? '状态' : 'Status'}</th>
                      <th className="text-left p-4">{language === 'zh' ? '注册日期' : 'Join Date'}</th>
                      <th className="text-left p-4">{language === 'zh' ? '操作' : 'Actions'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentUsers.map((user) => (
                      <tr key={user.id} className="border-b hover:bg-muted/50">
                        <td className="p-4">
                          <div className="font-medium">{user.name}</div>
                        </td>
                        <td className="p-4 text-muted-foreground">{user.email}</td>
                        <td className="p-4">
                          <Badge variant={getStatusBadge(user.status).variant}>
                            {getStatusBadge(user.status).text}
                          </Badge>
                        </td>
                        <td className="p-4 text-muted-foreground">{user.joinDate}</td>
                        <td className="p-4">
                          <div className="flex space-x-2">
                            <Button size="sm" variant="outline">
                              <Eye className="h-3 w-3" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <Ban className="h-3 w-3" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Other tabs would be implemented similarly */}
      {activeTab === 'content' && (
        <div className="text-center py-12">
          <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">
            {language === 'zh' ? '内容审核模块' : 'Content Review Module'}
          </h3>
          <p className="text-muted-foreground">
            {language === 'zh' ? '内容审核功能正在开发中' : 'Content review functionality is under development'}
          </p>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="text-center py-12">
          <Settings className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">
            {language === 'zh' ? '系统设置' : 'System Settings'}
          </h3>
          <p className="text-muted-foreground">
            {language === 'zh' ? '系统配置功能正在开发中' : 'System configuration is under development'}
          </p>
        </div>
      )}
    </div>
  )
} 