#!/bin/bash

echo "🚀 启动 Impromptu 后端API服务 (FastAPI)"
echo "======================================"

# 检查是否在项目根目录
if [ ! -f "setup.py" ]; then
    echo "❌ 错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 虚拟环境不存在，正在创建..."
    bash scripts/setup/install.sh
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "🔍 检查依赖..."
echo "📦 安装项目包（开发模式）..."
pip install -e . --no-deps --timeout 30 || {
    echo "⚠️  项目包安装失败，尝试仅安装requirements.txt依赖..."
    pip install -r requirements.txt --timeout 30
}

# 安装FastAPI相关依赖
echo "📦 确保安装FastAPI依赖..."
pip install fastapi uvicorn --timeout 30

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 检查端口5000是否可用
echo "🔍 检查端口5000是否可用..."
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口5000已被占用，尝试终止占用进程..."
    kill -9 $(lsof -Pi :5000 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 2
fi

# 启动FastAPI服务器
echo "🌐 启动FastAPI服务器 (端口 5000)..."
echo "访问地址: http://localhost:5000"
echo "API文档: http://localhost:5000/docs"
echo "前端界面: http://localhost:3000 (需要单独启动前端服务器)"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

cd backend/services
python main_api.py 