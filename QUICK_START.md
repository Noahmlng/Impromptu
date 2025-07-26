# 🚀 Impromptu 项目快速启动指南

这个文档提供了所有可用的启动命令，让你快速启动Impromptu社交匹配系统。

## 📋 快速概览

| 命令 | 功能 | 端口 |
|------|------|------|
| `make dev` | 同时启动前端和后端 | 前端:3000, 后端:5000 |
| `make backend` | 仅启动后端API | 5000 |
| `make frontend` | 仅启动前端 | 3000 |
| `make quick-start` | 完整安装+启动流程 | 前端:3000, 后端:5000 |

## 🎯 推荐启动流程

### 新用户 - 第一次运行
```bash
make quick-start
```
这个命令会：
1. ✅ 检查环境配置
2. 📦 安装所有依赖
3. 🚀 启动前端和后端服务

### 日常开发
```bash
make dev
```
同时启动前端和后端服务，适合日常开发。

## 🔧 单独启动服务

### 仅启动后端 API
```bash
make backend
# 或者
make api
```
- 🌐 访问地址: http://localhost:5000
- 📚 API文档: http://localhost:5000/docs

### 仅启动前端
```bash
make frontend
# 或者
make web
```
- 💻 访问地址: http://localhost:3000

## 🛠️ 其他有用命令

### 环境检查
```bash
make check
```

### 安装依赖
```bash
make install
```

### 服务状态检查
```bash
make status
```

### 停止所有服务
```bash
make stop
```

### 重启服务
```bash
make restart
```

### 清理临时文件
```bash
make clean
```

## 📁 传统启动脚本（向后兼容）

如果你习惯使用脚本文件：

### 后端启动
```bash
bash scripts/setup/start_api.sh
# 或者
bash scripts/setup/start_backend.sh
```

### 前端启动
```bash
bash scripts/setup/start_web.sh
# 或者
bash scripts/setup/start_frontend.sh
```

## 🔍 故障排除

### 端口被占用
如果遇到端口被占用的问题：
```bash
make stop  # 停止所有服务
make dev   # 重新启动
```

### 依赖问题
如果遇到依赖问题：
```bash
make clean    # 清理
make install  # 重新安装依赖
```

### 查看所有可用命令
```bash
make help
```

## 🌐 访问地址

启动成功后，你可以访问：

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/docs

## 💡 开发提示

1. **开发模式**: 使用`make dev`启动开发模式，支持热重载
2. **API测试**: 访问 http://localhost:5000/docs 查看和测试API
3. **生产构建**: 使用`make frontend-build`构建前端生产版本
4. **日志查看**: 使用`make logs`查看最近的日志文件

## ⚡ 快速命令总结

```bash
# 🚀 最快启动
make dev

# 🔍 检查状态  
make status

# 🛑 停止服务
make stop

# 🔄 重启服务
make restart

# �� 查看帮助
make help
``` 

## 常见问题解决方案

### 数据库初始化错误解决
如果遇到 "HTTP 500: Internal Server Error" 登录错误，通常是数据库连接初始化问题。我们的启动脚本已内置解决方案：

#### 自动解决方案
```bash
# 推荐：使用改进的开发模式（含健康检查）
make dev

# 快速启动（跳过依赖检查）
make dev-quick

# 仅启动后端（含数据库检查）
make dev-backend
```

#### 手动验证
```bash
# 检查服务健康状态
make health-check

# 查看详细状态
make status
```

#### 启动脚本改进
- ✅ **预启动数据库连接检查**：确保数据库连接正常后再启动服务
- ✅ **服务健康检查**：自动验证服务启动状态  
- ✅ **智能端口管理**：自动清理冲突端口
- ✅ **后台启动选项**：支持后台运行方式
- ✅ **快速模式**：跳过依赖检查以快速启动

#### 故障排除
如果问题仍然存在：
```bash
# 1. 强制清理并重启
make force-restart

# 2. 检查环境配置
make check

# 3. 查看详细日志
tail -f backend.log
``` 