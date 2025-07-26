#!/bin/bash

echo "🌐 启动 Impromptu Web 前端界面"
echo "=============================="

# 检查是否在项目根目录
if [ ! -f "setup.py" ]; then
    echo "❌ 错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 检查frontend目录
if [ ! -d "frontend" ]; then
    echo "❌ 错误: frontend目录不存在"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js"
    echo "💡 建议使用: brew install node (macOS) 或访问 https://nodejs.org/"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到npm"
    exit 1
fi

# 进入前端目录
cd frontend

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 未找到package.json文件"
    exit 1
fi

# 安装依赖（如果node_modules不存在）
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 检查端口3000是否可用
echo "🔍 检查端口3000是否可用..."
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口3000已被占用，尝试终止占用进程..."
    kill -9 $(lsof -Pi :3000 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 2
fi

echo "🚀 启动Next.js开发服务器 (端口 3000)..."
echo "访问地址: http://localhost:3000"
echo "确保API服务已启动: bash scripts/setup/start_api.sh"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev 