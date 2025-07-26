# Linker 前端部署指南

## 问题解决

你之前遇到的问题已经修复：

### 1. ✅ 修复了 `next export` 废弃命令
- 移除了 `package.json` 中的 `export` 脚本
- 使用了 Next.js 14 推荐的 `output: 'export'` 配置

### 2. ✅ 修复了 Zeabur 配置
- 将配置从 Python 后端改为静态网站部署
- 设置了正确的构建命令和输出目录

### 3. ✅ 优化了 API 配置
- 添加了生产环境 API URL 支持
- 支持环境变量配置

## 部署步骤

### Zeabur 部署

1. **环境变量配置**
   在 Zeabur 项目设置中添加以下环境变量：
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api-domain.com
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

2. **推送代码**
   ```bash
   git add .
   git commit -m "Fix frontend deployment configuration"
   git push origin main
   ```

3. **Zeabur 会自动部署**
   - 配置文件：`.zeabur/config.json`
   - 构建命令：`cd frontend && npm ci && npm run build`
   - 输出目录：`frontend/out`

### 本地测试

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建静态文件
npm run build

# 检查输出文件
ls -la out/
```

## 文件结构

部署后的静态文件结构：
```
frontend/out/
├── _next/          # Next.js 静态资源
├── admin/          # 管理页面
├── chat/           # 聊天页面
├── home/           # 主页
├── login/          # 登录页面
├── profile/        # 个人资料页面
├── index.html      # 根页面 (你的 page.tsx)
└── ...
```

## 重要配置文件

- `frontend/next.config.js` - Next.js 配置
- `frontend/package.json` - 项目依赖和脚本
- `.zeabur/config.json` - Zeabur 部署配置

## 故障排除

如果部署仍有问题：

1. **检查构建日志**
   - 在 Zeabur 控制台查看构建日志
   - 确认构建命令执行成功

2. **检查环境变量**
   - 确认 `NEXT_PUBLIC_API_URL` 设置正确
   - 确认后端 API 可访问

3. **检查路由**
   - 所有页面都应该可以直接访问
   - 例如：`/home/`, `/login/`, `/profile/`

## 联系支持

如果仍有问题，请提供：
- Zeabur 构建日志
- 错误信息截图
- 访问的具体 URL 