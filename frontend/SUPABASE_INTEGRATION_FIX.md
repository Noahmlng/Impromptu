# Supabase集成修复

## 问题描述

前端在请求 `127.0.0.1:5003/api/profile/metadata` 时返回404错误，原因是metadata数据存储在Supabase中，但前端却在调用后端API。

## 解决方案

### 1. 数据存储架构调整

**之前：** 所有操作都调用后端API → 后端再操作Supabase  
**现在：** 直接操作Supabase（metadata/tags读取） + 后端API（AI功能）

### 2. API客户端修改 (`lib/api.ts`)

#### 直接使用Supabase的操作：
- ✅ `createMetadata()` - 创建/更新用户元数据
- ✅ `getUserMetadata()` - 获取用户元数据  
- ✅ `batchUpdateMetadata()` - 批量更新元数据
- ✅ `getUserTags()` - 获取用户标签

#### 仍使用后端API的操作：
- 🔧 `generateTags()` - AI标签生成
- 🔧 `searchMatches()` - AI匹配搜索
- 🔧 `analyzeCompatibility()` - 兼容性分析

### 3. 用户注册流程改进

现在注册时会自动创建 `user_profile` 记录：
```typescript
const userId = `user_${Date.now()}`
await supabase.from('user_profile').insert({
  user_id: userId,
  auth_user_id: data.user.id,
  email: data.user.email!,
  display_name: displayName,
  avatar_url: avatarUrl,
  status: 'active'
})
```

### 4. 数据库表结构

#### user_profile
- `auth_user_id` - 关联Supabase认证用户
- `user_id` - 业务用户ID
- `display_name`, `email`, `avatar_url` 等基本信息

#### user_metadata  
- `user_id` - 关联到user_profile
- `section_type` - 数据分类 (如: 'profile', 'user_request')
- `section_key` - 具体子分类 (如: 'personal', 'professional')
- `content` - JSONB格式的具体内容

#### user_tags
- `user_id` - 关联到user_profile  
- `tag_name` - 标签名称
- `confidence_score` - 置信度评分
- `tag_source` - 标签来源

### 5. RLS安全策略

Supabase已配置正确的行级安全策略：
- 用户只能访问自己的数据
- 通过 `auth.uid()` 验证身份
- 通过 `user_profile.auth_user_id` 关联权限

## 优势

### 性能改进
- ✅ 减少不必要的网络跳转
- ✅ 直接数据库访问，响应更快
- ✅ 减少后端服务器负载

### 架构清晰
- 🎯 数据操作 → Supabase直连
- 🤖 AI功能 → 后端API
- 🔐 认证授权 → Supabase Auth

### 开发体验
- 🔧 实时数据同步
- 🛡️ 自动的安全策略
- 📊 内置的查询优化

## 测试验证

现在可以测试以下功能：

1. **用户注册** → 应该自动创建user_profile
2. **填写基本信息** → 数据应该保存到user_metadata表
3. **生成标签** → 调用后端API，结果保存到user_tags表
4. **搜索匹配** → 调用后端API进行AI匹配

## 注意事项

1. **后端API依然需要运行** - 用于AI功能（标签生成、匹配搜索）
2. **环境变量** - 确保Supabase URL和密钥正确配置
3. **用户权限** - 新注册用户需要确保user_profile记录创建成功

## 错误处理

- 加强了Supabase操作的错误捕获
- 注册时profile创建失败不会阻塞整个注册流程
- 提供详细的错误信息用于调试

## 下一步

可以考虑进一步优化：
- 使用Supabase实时功能同步数据变更
- 缓存常用的标签和元数据
- 实现离线数据同步机制 