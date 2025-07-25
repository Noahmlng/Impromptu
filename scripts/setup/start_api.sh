#!/bin/bash

echo "🚀 启动 Impromptu 匹配系统 API 服务"
echo "================================="

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

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export FLASK_APP=src.services.api_server
export FLASK_ENV=development

# 启动API服务器
echo "🌐 启动API服务器 (端口 5000)..."
echo "访问地址: http://localhost:5000"
echo "Web界面: http://localhost:8000 (需要单独启动web服务器)"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

cd "$(dirname "$0")/../.."
python -m src.services.api_server 