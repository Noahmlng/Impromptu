#!/bin/bash

echo "🌐 启动 Impromptu Web 前端界面"
echo "=============================="

# 检查是否在项目根目录
if [ ! -f "setup.py" ]; then
    echo "❌ 错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 检查web目录
if [ ! -d "web" ]; then
    echo "❌ 错误: web目录不存在"
    exit 1
fi

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

echo "🔍 检查端口8000是否可用..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口8000已被占用，尝试终止占用进程..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 2
fi

echo "🚀 启动Web服务器 (端口 8000)..."
echo "访问地址: http://localhost:8000"
echo "确保API服务已启动: bash scripts/setup/start_api.sh"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

cd web
python3 -m http.server 8000 