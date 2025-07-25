#!/bin/bash

echo "🚀 Impromptu 匹配系统安装脚本"
echo "================================"

# 检查Python版本
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "Python版本: $python_version"

if [[ $(python3 -c "import sys; print(sys.version_info >= (3, 8))") == "False" ]]; then
    echo "❌ 错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装项目依赖..."
pip install -r requirements.txt

# 安装项目
echo "📦 安装项目..."
pip install -e .

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data/raw/profiles
mkdir -p data/processed/user_vectors
mkdir -p data/models
mkdir -p data/results
mkdir -p temp_uploads

echo "✅ 安装完成！"
echo ""
echo "使用方法："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 运行演示: python scripts/demo/main.py"
echo "3. 启动API服务: bash scripts/setup/start_api.sh"
echo "4. 访问Web界面: http://localhost:8000" 