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

# 端口配置 - 使用不同的默认端口避免冲突
BACKEND_PORT=${BACKEND_PORT:-8000}

# 检查服务是否已经运行
check_service_running() {
    local port=$1
    if curl -s http://localhost:${port}/ >/dev/null 2>&1; then
        echo "✅ 服务已在端口${port}运行，无需重复启动"
        echo "🌐 访问地址: http://localhost:${port}"
        echo "📖 API文档: http://localhost:${port}/docs"
        echo ""
        echo "💡 如需重启服务，请先停止现有服务："
        echo "   bash scripts/setup/manage_ports.sh clean"
        echo "   然后重新运行此脚本"
        exit 0
    fi
}

# 检查服务是否已运行
check_service_running $BACKEND_PORT

# 改进的端口检查和清理逻辑
check_and_clean_port() {
    local port=$1
    echo "🔍 检查端口${port}是否可用..."
    
    # 查找占用端口的进程
    local pids=$(lsof -ti :${port} 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo "⚠️  警告: 端口${port}被以下进程占用:"
        for pid in $pids; do
            local process_info=$(ps -p $pid -o pid,ppid,comm,args --no-headers 2>/dev/null)
            if [ ! -z "$process_info" ]; then
                echo "   PID: $pid - $process_info"
                # 只终止Python相关进程，避免误杀系统进程
                if echo "$process_info" | grep -q "python\|uvicorn\|main_api"; then
                    echo "   🔄 正在终止进程 $pid..."
                    kill -TERM $pid 2>/dev/null
                    sleep 2
                    # 如果进程仍然存在，强制终止
                    if kill -0 $pid 2>/dev/null; then
                        echo "   ⚠️  强制终止进程 $pid..."
                        kill -9 $pid 2>/dev/null
                    fi
                else
                    echo "   ⚠️  检测到非Python进程占用端口，请手动处理"
                    echo "   💡 或者使用不同的端口: BACKEND_PORT=8001 $0"
                    exit 1
                fi
            fi
        done
        
        # 等待端口释放
        echo "⏳ 等待端口释放..."
        for i in {1..10}; do
            if ! lsof -ti :${port} >/dev/null 2>&1; then
                echo "✅ 端口${port}已释放"
                break
            fi
            sleep 1
            if [ $i -eq 10 ]; then
                echo "❌ 端口${port}释放超时，请手动处理"
                exit 1
            fi
        done
    else
        echo "✅ 端口${port}可用"
    fi
}

# 检查和清理端口
check_and_clean_port $BACKEND_PORT

# 启动FastAPI服务器
echo "🌐 启动FastAPI服务器 (端口 ${BACKEND_PORT})..."
echo "访问地址: http://localhost:${BACKEND_PORT}"
echo "API文档: http://localhost:${BACKEND_PORT}/docs"
echo "前端界面: http://localhost:3000 (需要单独启动前端服务器)"
echo ""
echo "💡 使用不同端口: BACKEND_PORT=8001 $0"
echo "按 Ctrl+C 停止服务"
echo ""

# 使用统一的启动方式
python backend/main.py comprehensive --port ${BACKEND_PORT} 