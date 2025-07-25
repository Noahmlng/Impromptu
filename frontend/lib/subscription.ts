import { supabase } from './supabase'

export type SubscriptionType = 'free' | 'pro' | 'premium'

export interface SubscriptionPlan {
  type: SubscriptionType
  name: string
  price: number
  features: string[]
  limits: {
    tags_per_month: number
    searches_per_day: number
    matches_per_day: number
  }
}

export const subscriptionPlans: SubscriptionPlan[] = [
  {
    type: 'free',
    name: 'Free',
    price: 0,
    features: ['基础匹配', '5个标签', '每日3次搜索'],
    limits: {
      tags_per_month: 5,
      searches_per_day: 3,
      matches_per_day: 10
    }
  },
  {
    type: 'pro',
    name: 'Pro',
    price: 29,
    features: ['高级匹配', '无限标签', '每日20次搜索', '兼容性分析'],
    limits: {
      tags_per_month: -1, // unlimited
      searches_per_day: 20,
      matches_per_day: 50
    }
  },
  {
    type: 'premium',
    name: 'Premium',
    price: 99,
    features: ['顶级匹配', '无限功能', '优先支持', '个性化推荐'],
    limits: {
      tags_per_month: -1, // unlimited
      searches_per_day: -1, // unlimited
      matches_per_day: -1 // unlimited
    }
  }
]

export const subscriptionService = {
  // 获取用户当前订阅
  async getCurrentSubscription(): Promise<{ success: boolean; data?: SubscriptionType; message?: string }> {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      const { data: profile, error } = await supabase
        .from('user_profile')
        .select('subscription_type')
        .eq('auth_user_id', user.id)
        .single()

      if (error) throw error

      return {
        success: true,
        data: profile.subscription_type as SubscriptionType
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message
      }
    }
  },

  // 更新用户订阅
  async updateSubscription(newSubscription: SubscriptionType): Promise<{ success: boolean; message: string }> {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      const { error } = await supabase
        .from('user_profile')
        .update({ 
          subscription_type: newSubscription,
          updated_at: new Date().toISOString()
        })
        .eq('auth_user_id', user.id)

      if (error) throw error

      return {
        success: true,
        message: `订阅已成功更新为 ${newSubscription}`
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '更新订阅失败'
      }
    }
  },

  // 检查功能限制
  async checkUsageLimit(feature: 'tags' | 'searches' | 'matches'): Promise<{ allowed: boolean; remaining?: number }> {
    try {
      const subscriptionResult = await this.getCurrentSubscription()
      if (!subscriptionResult.success || !subscriptionResult.data) {
        return { allowed: false }
      }

      const plan = subscriptionPlans.find(p => p.type === subscriptionResult.data)
      if (!plan) return { allowed: false }

      // 简化版本：免费用户有限制，付费用户无限制
      if (plan.type === 'free') {
        // 这里可以添加实际的使用量统计逻辑
        switch (feature) {
          case 'tags':
            return { allowed: true, remaining: plan.limits.tags_per_month }
          case 'searches':
            return { allowed: true, remaining: plan.limits.searches_per_day }
          case 'matches':
            return { allowed: true, remaining: plan.limits.matches_per_day }
          default:
            return { allowed: true }
        }
      }

      // 付费用户无限制
      return { allowed: true }
    } catch (error) {
      return { allowed: false }
    }
  },

  // 获取所有订阅计划
  getPlans(): SubscriptionPlan[] {
    return subscriptionPlans
  },

  // 获取特定计划信息
  getPlan(type: SubscriptionType): SubscriptionPlan | undefined {
    return subscriptionPlans.find(p => p.type === type)
  }
} 