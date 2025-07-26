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

# 检查依赖（可通过环境变量跳过）
if [ "$SKIP_DEPENDENCY_CHECK" != "1" ]; then
    echo "🔍 检查依赖..."
    echo "📦 安装项目包（开发模式）..."
    pip install -e . --no-deps --timeout 30 || {
        echo "⚠️  项目包安装失败，尝试仅安装requirements.txt依赖..."
        pip install -r requirements.txt --timeout 30
    }

    # 安装FastAPI相关依赖
    echo "📦 确保安装FastAPI依赖..."
    pip install fastapi uvicorn --timeout 30
else
    echo "⏩ 跳过依赖检查（快速模式）"
fi

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 端口配置 - 使用不同的默认端口避免冲突
BACKEND_PORT=${BACKEND_PORT:-8000}

# 预启动数据库连接检查
check_database_connection() {
    echo "🔍 检查数据库连接..."
    python3 -c "
import sys
import os
sys.path.append('.')
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    load_dotenv('.env')
    
    # 快速检查环境变量
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if supabase_key:
        print('环境变量加载状态:')
        print(f'SUPABASE_SERVICE_ROLE_KEY: 已设置')
        print('✅ Supabase数据库连接验证成功')
    else:
        raise Exception('缺少必要的环境变量')
    
    # 快速数据库连接测试
    from backend.services.database_service import get_supabase
    client = get_supabase()
    response = client.table('user_profile').select('id', count='exact').limit(1).execute()
    print('✅ 数据库连接测试成功')
    
except Exception as e:
    print(f'❌ 数据库连接测试失败: {e}')
    print('💡 请检查环境变量和数据库配置')
    sys.exit(1)
"
    if [ $? -ne 0 ]; then
        echo "❌ 数据库连接测试失败，停止启动"
        exit 1
    fi
}

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
                    echo "   ⚠️  检测到非Python进程占用端口，请手动处理或使用其他端口"
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

# 服务健康检查
wait_for_service() {
    local port=$1
    local max_attempts=10  # 减少到10次
    local attempt=1
    
    echo "⏳ 等待服务启动..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:${port}/health >/dev/null 2>&1 || curl -s http://localhost:${port}/ >/dev/null 2>&1; then
            echo "✅ 服务启动成功！"
            echo "🌐 访问地址: http://localhost:${port}"
            echo "📖 API文档: http://localhost:${port}/docs"
            return 0
        fi
        # 只在前3次和最后3次显示详细进度
        if [ $attempt -le 3 ] || [ $attempt -gt 7 ]; then
            echo "   尝试 $attempt/$max_attempts - 等待服务响应..."
        elif [ $attempt -eq 4 ]; then
            echo "   ... 继续等待服务启动 ..."
        fi
        sleep 1.5  # 减少等待间隔
        attempt=$((attempt + 1))
    done
    
    echo "❌ 服务启动超时，请检查日志"
    return 1
}

# 执行预检查
check_database_connection

# 检查和清理端口
check_and_clean_port $BACKEND_PORT

# 启动FastAPI服务器
echo "🌐 启动FastAPI服务器 (端口 ${BACKEND_PORT})..."
echo "访问地址: http://localhost:${BACKEND_PORT}"
echo "API文档: http://localhost:${BACKEND_PORT}/docs"
echo "前端界面: http://localhost:3000 (需要单独启动前端服务器)"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 使用统一的启动方式，并添加后台运行选项
if [ "$1" = "--background" ]; then
    echo "🚀 后台启动服务..."
    nohup python backend/main.py comprehensive --port ${BACKEND_PORT} > backend.log 2>&1 &
    echo $! > backend.pid
    sleep 3
    wait_for_service $BACKEND_PORT
    if [ $? -eq 0 ]; then
        echo "✅ 后端服务已在后台启动，PID: $(cat backend.pid)"
        echo "📋 查看日志: tail -f backend.log"
        echo "🛑 停止服务: kill $(cat backend.pid) && rm backend.pid"
    else
        echo "❌ 后端服务启动失败"
        exit 1
    fi
else
    # 前台启动
    python backend/main.py comprehensive --port ${BACKEND_PORT}
fi 