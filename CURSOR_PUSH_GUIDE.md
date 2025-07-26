# Cursor Push Routes - 自动化Git推送流程

## 概述
基于之前的push经验，创建了自动化的Git推送流程脚本，简化日常开发中的代码提交和推送操作。

## 功能特性
- ✅ 自动检查Git状态
- ✅ 智能处理远程分支同步
- ✅ 自动解决简单合并冲突
- ✅ 彩色输出，清晰的状态提示
- ✅ 错误处理和回滚指导
- ✅ 支持Shell和Python两种版本

## 使用方法

### Python版本（推荐）
```bash
# 基本使用
python scripts/cursor_push.py "your commit message"

# 示例
python scripts/cursor_push.py "fix: update login page styling"
python scripts/cursor_push.py "feat: add new loading modal with kapi images"
python scripts/cursor_push.py "new product feature 01"
```

### Shell版本
```bash
# 首先给脚本执行权限
chmod +x scripts/cursor_push.sh

# 使用脚本
./scripts/cursor_push.sh "your commit message"
```

## 工作流程

脚本会按以下步骤执行：

1. **状态检查** - 检查当前Git状态，确认有更改需要提交
2. **添加更改** - 自动执行 `git add .`
3. **提交更改** - 使用提供的消息提交更改
4. **同步检查** - 检查远程分支状态，判断是否需要合并
5. **自动合并** - 如果落后远程分支，自动尝试合并
6. **推送代码** - 推送到远程仓库
7. **完成反馈** - 显示最新提交信息和成功状态

## 冲突处理

当遇到合并冲突时，脚本会：
1. 停止执行并显示错误信息
2. 提供手动解决冲突的指导步骤：
   ```bash
   git add .
   git commit -m "Merge remote changes and resolve conflicts"
   git push origin main
   ```

## 常见使用场景

### 日常开发提交
```bash
python scripts/cursor_push.py "fix: resolve login authentication issue"
```

### 功能开发完成
```bash
python scripts/cursor_push.py "feat: implement user profile management"
```

### 紧急修复
```bash
python scripts/cursor_push.py "hotfix: critical security vulnerability"
```

### UI/UX更新
```bash
python scripts/cursor_push.py "ui: update dashboard layout and styling"
```

## 提交信息规范

建议使用以下格式：
- `feat:` - 新功能
- `fix:` - 修复bug
- `ui:` - UI/样式更新
- `refactor:` - 代码重构
- `docs:` - 文档更新
- `test:` - 测试相关
- `chore:` - 构建过程或辅助工具的变动

## 安全特性

- 🔒 自动检查Git仓库有效性
- 🔒 在执行前确认有更改需要提交
- 🔒 提供详细的错误信息和恢复指导
- 🔒 支持用户中断操作（Ctrl+C）

## 故障排除

### 脚本执行权限问题
```bash
chmod +x scripts/cursor_push.sh
```

### Python环境问题
确保使用Python 3.6+：
```bash
python3 scripts/cursor_push.py "your message"
```

### 合并冲突
手动解决冲突后：
```bash
git add .
git commit -m "Merge remote changes and resolve conflicts"
git push origin main
```

## 扩展功能

可以根据需要扩展脚本功能：
- 添加分支选择支持
- 集成代码检查工具
- 添加自动化测试触发
- 支持多仓库操作

## 注意事项

⚠️ **重要提醒**：
- 脚本会自动执行 `git add .`，请确保只提交需要的文件
- 建议在使用前先查看 `git status` 确认更改内容
- 对于重要更改，建议先在测试分支验证

## 版本历史

- v1.0 - 基础功能实现，支持自动提交和推送
- v1.1 - 添加冲突检测和处理
- v1.2 - 优化错误处理和用户体验 