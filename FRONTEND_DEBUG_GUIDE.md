 # 前端认证错误调试指南

## 问题症状
- `401 UNAUTHORIZED` 错误在访问 `/api/profile/metadata`
- `400 Bad Request` 错误从 Supabase Auth

## 修复步骤

### 1. 确认 Supabase 配置 ✅
已修复 `frontend/lib/supabase.ts` 中的配置问题。

### 2. 确认后端认证装饰器 ✅
已修复 `backend/services/comprehensive_api.py` 中的JWT解码逻辑。

### 3. 启动后端服务
在项目根目录运行：
```bash
python backend/services/comprehensive_api.py
```

### 4. 运行调试脚本
```bash
# 检查服务状态
python scripts/check_service.py

# 调试认证流程
python scripts/debug_auth_flow.py

# 完整认证测试
python scripts/test_supabase_auth.py
```

## 调试步骤

### Step 1: 检查 Supabase 连接
在浏览器开发者工具中检查：
1. 是否能正常访问 `https://anxbbsrnjgmotxzysqwf.supabase.co`
2. 网络请求是否返回正确的 200 状态

### Step 2: 检查认证流程
1. **注册新用户**：
   - 打开浏览器开发者工具
   - 尝试注册一个新用户
   - 检查 Network 面板中的请求和响应

2. **登录测试**：
   - 尝试登录刚注册的用户
   - 查看是否获得有效的 access_token

### Step 3: 检查 Token 传递
在登录成功后，检查：
1. `localStorage` 中是否有 `auth_token`
2. 后续 API 请求是否包含 `Authorization: Bearer <token>` 头

### Step 4: 数据库检查
确认数据库中有相应的用户记录：
1. `auth.users` 表中有用户记录
2. `user_profile` 表中有对应的档案记录

## 常见问题解决

### Q1: Supabase 400 错误
**原因**: Supabase 配置错误或请求格式不正确
**解决**: 确认 `frontend/lib/supabase.ts` 中的 URL 和 Key 正确

### Q2: 401 认证错误
**原因**: Token 无效或未传递
**解决**: 
1. 检查用户是否已登录
2. 检查 token 是否正确传递
3. 检查后端 auth_required 装饰器

### Q3: 用户档案不存在
**原因**: 数据库触发器未生效或用户档案未创建
**解决**:
1. 检查数据库迁移是否完成
2. 手动创建用户档案记录

## 测试用户
⚠️ **重要**: Supabase 不接受 `@example.com` 等测试域名，必须使用真实邮箱域名！

建议的测试邮箱格式：
- 邮箱: `test_TIMESTAMP@gmail.com` （时间戳确保唯一性）
- 密码: `testpassword123`

或者使用其他真实域名：`@outlook.com`, `@yahoo.com` 等

## 支持工具
- `scripts/check_service.py` - 服务状态检查
- `scripts/quick_auth_test.py` - **快速认证测试（推荐先运行）**
- `scripts/test_supabase_connection.py` - Supabase连接测试
- `scripts/debug_auth_flow.py` - 认证流程调试
- `scripts/test_supabase_auth.py` - 完整认证测试 