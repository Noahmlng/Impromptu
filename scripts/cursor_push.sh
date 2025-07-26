#!/bin/bash

# Cursor Push Routes - 自动化Git推送流程
# 使用方法: ./scripts/cursor_push.sh "commit message"

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
if [ $# -eq 0 ]; then
    print_error "请提供提交信息"
    echo "使用方法: $0 \"your commit message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

print_status "开始 Cursor Push 流程..."
print_status "提交信息: $COMMIT_MESSAGE"

# 1. 检查当前状态
print_status "检查当前Git状态..."
git status

# 2. 添加所有更改
print_status "添加所有更改到暂存区..."
git add .

# 3. 检查是否有更改需要提交
if git diff --cached --quiet; then
    print_warning "没有检测到需要提交的更改"
    exit 0
fi

# 4. 提交更改
print_status "提交更改..."
git commit -m "$COMMIT_MESSAGE"

# 5. 检查远程状态并尝试推送
print_status "检查远程分支状态..."
git fetch origin

# 检查是否需要合并
BEHIND=$(git rev-list --count HEAD..origin/main)
if [ "$BEHIND" -gt 0 ]; then
    print_warning "本地分支落后远程分支 $BEHIND 个提交，需要合并"
    
    # 尝试合并
    print_status "尝试合并远程更改..."
    if git pull origin main --no-rebase; then
        print_success "成功合并远程更改"
    else
        print_error "合并失败，存在冲突"
        print_status "请手动解决冲突，然后运行:"
        echo "  git add ."
        echo "  git commit -m \"Merge remote changes and resolve conflicts\""
        echo "  git push origin main"
        exit 1
    fi
fi

# 6. 推送到远程
print_status "推送到远程仓库..."
if git push origin main; then
    print_success "成功推送到远程仓库!"
    
    # 显示最新提交信息
    print_status "最新提交信息:"
    git log --oneline -1
    
    print_success "Push 流程完成!"
else
    print_error "推送失败"
    exit 1
fi 