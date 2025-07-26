#!/bin/bash

echo "🔧 Impromptu 端口管理工具"
echo "========================"

# 检查端口占用情况
check_port_status() {
    echo "📊 当前端口占用情况："
    echo "端口 3000 (前端):"
    lsof -i :3000 | grep LISTEN || echo "  ❌ 未占用"
    
    echo "端口 5000 (API备用):"
    lsof -i :5000 | grep LISTEN || echo "  ❌ 未占用"
    
    echo "端口 8000 (后端主):"
    lsof -i :8000 | grep LISTEN || echo "  ❌ 未占用"
    
    echo ""
}

# 检查服务健康状态
check_service_health() {
    echo "🏥 服务健康检查："
    
    # 检查后端API
    if curl -s http://localhost:8000/ >/dev/null 2>&1; then
        API_STATUS=$(curl -s http://localhost:8000/ | jq -r .message 2>/dev/null || echo "运行中")
        echo "✅ 后端API (8000): $API_STATUS"
    else
        echo "❌ 后端API (8000): 无响应"
    fi
    
    # 检查前端
    if curl -s http://localhost:3000/ >/dev/null 2>&1; then
        echo "✅ 前端应用 (3000): 正常运行"
    else
        echo "❌ 前端应用 (3000): 无响应"
    fi
    
    echo ""
}

# 智能清理冲突进程
clean_conflicts() {
    local port=$1
    echo "🧹 清理端口 $port 的冲突进程..."
    
    local pids=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        for pid in $pids; do
            # 获取更详细的进程信息
            local process_info=$(ps -p $pid -o pid,ppid,comm,command --no-headers 2>/dev/null)
            local process_cmd=$(ps -p $pid -o command --no-headers 2>/dev/null)
            
            if [ ! -z "$process_info" ]; then
                echo "  发现进程: PID $pid"
                echo "    命令: $process_cmd"
                
                # 改进的进程匹配逻辑
                if echo "$process_cmd" | grep -qE "(uvicorn|fastapi|main_api|backend.*main|next.*dev|npm.*run.*dev|node.*next)" || \
                   echo "$process_cmd" | grep -qE "python.*Impromptu.*backend|python.*main\.py" || \
                   echo "$process_cmd" | grep -qE "Impromptu.*frontend|Impromptu.*npm"; then
                    echo "    🔄 识别为应用进程，正在安全终止..."
                    kill -TERM $pid 2>/dev/null
                    sleep 2
                    if kill -0 $pid 2>/dev/null; then
                        echo "    ⚠️  优雅终止失败，强制终止进程 $pid..."
                        kill -9 $pid 2>/dev/null
                    fi
                    echo "    ✅ 进程 $pid 已终止"
                elif echo "$process_cmd" | grep -qE "ControlCenter|AirPlay|Bluetooth" || \
                     [ $(ps -p $pid -o ppid --no-headers 2>/dev/null) -eq 1 ]; then
                    echo "    ⚠️  跳过系统进程 $pid (安全考虑)"
                else
                    echo "    ❓ 未知进程类型，手动处理建议:"
                    echo "       kill $pid  # 如果确认是你的进程"
                    echo "    💡 或使用强制清理: make force-restart"
                fi
            fi
        done
    else
        echo "  ✅ 端口 $port 无冲突"
    fi
}

# 启动服务
start_services() {
    echo "🚀 启动服务..."
    
    # 检查是否已有后端运行
    if curl -s http://localhost:8000/ >/dev/null 2>&1; then
        echo "✅ 后端服务已在运行，跳过启动"
    else
        echo "🔄 启动后端服务..."
        cd "$(dirname "$0")/../.." && python backend/main.py comprehensive --port 8000 &
        sleep 3
    fi
    
    # 检查是否已有前端运行
    if curl -s http://localhost:3000/ >/dev/null 2>&1; then
        echo "✅ 前端服务已在运行，跳过启动"
    else
        echo "🔄 启动前端服务..."
        cd "$(dirname "$0")/../../frontend" && npm run dev &
        sleep 3
    fi
}

# 主菜单
case "${1:-status}" in
    "status")
        check_port_status
        check_service_health
        ;;
    "clean")
        echo "🧹 清理所有端口冲突..."
        clean_conflicts 3000
        clean_conflicts 5000
        clean_conflicts 8000
        echo "✅ 清理完成"
        ;;
    "start")
        start_services
        echo "✅ 启动完成"
        check_service_health
        ;;
    "restart")
        echo "🔄 重启所有服务..."
        clean_conflicts 3000
        clean_conflicts 8000
        sleep 2
        start_services
        echo "✅ 重启完成"
        ;;
    "help")
        echo "用法: $0 [命令]"
        echo "命令:"
        echo "  status   - 检查端口和服务状态 (默认)"
        echo "  clean    - 清理端口冲突"
        echo "  start    - 启动服务"
        echo "  restart  - 重启所有服务"
        echo "  help     - 显示帮助"
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo "使用 '$0 help' 查看帮助"
        exit 1
        ;;
esac 