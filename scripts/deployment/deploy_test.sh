#!/bin/bash

# API 部署测试脚本
# 用于在部署前后进行自动化测试验证

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 默认配置
API_URL="http://localhost:5003"
ENV="development"
SKIP_LOAD_TEST=false
SKIP_MONITORING=false
TIMEOUT=300
PYTHON_CMD="python3"
VENV_PATH="venv"

# 显示使用帮助
show_help() {
    cat << EOF
API 部署测试脚本

用法: $0 [选项]

选项:
    -u, --url URL           API服务器地址 (默认: http://localhost:5003)
    -e, --env ENV           环境名称 (默认: development)
    -t, --timeout SECONDS  测试超时时间 (默认: 300秒)
    --skip-load            跳过负载测试
    --skip-monitoring      跳过性能监控
    --python PYTHON        Python命令 (默认: python3)
    --venv PATH            虚拟环境路径 (默认: venv)
    -h, --help             显示此帮助信息

示例:
    $0                                    # 使用默认配置
    $0 -u http://api.example.com -e prod # 测试生产环境
    $0 --skip-load --skip-monitoring     # 快速测试
EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            API_URL="$2"
            shift 2
            ;;
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --skip-load)
            SKIP_LOAD_TEST=true
            shift
            ;;
        --skip-monitoring)
            SKIP_MONITORING=true
            shift
            ;;
        --python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        --venv)
            VENV_PATH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python
    if ! command -v $PYTHON_CMD &> /dev/null; then
        log_error "Python ($PYTHON_CMD) 未安装"
        exit 1
    fi
    
    # 检查curl
    if ! command -v curl &> /dev/null; then
        log_error "curl 未安装"
        exit 1
    fi
    
    # 检查jq (JSON处理)
    if ! command -v jq &> /dev/null; then
        log_warning "jq 未安装，将跳过JSON响应验证"
    fi
    
    log_success "系统依赖检查完成"
}

# 激活虚拟环境
activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        log_info "激活虚拟环境: $VENV_PATH"
        source "$VENV_PATH/bin/activate"
        log_success "虚拟环境已激活"
    else
        log_warning "虚拟环境不存在: $VENV_PATH"
    fi
}

# 检查API基础连通性
check_api_connectivity() {
    log_info "检查API连通性: $API_URL"
    
    local max_retries=5
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -f -s -m 10 "$API_URL/api/system/health" > /dev/null; then
            log_success "API连通性正常"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_warning "连接失败，重试 $retry_count/$max_retries..."
        sleep 5
    done
    
    log_error "API连通性检查失败"
    return 1
}

# 验证API响应
verify_api_response() {
    log_info "验证API基础响应..."
    
    local health_response
    health_response=$(curl -s -m 10 "$API_URL/api/system/health")
    
    if [ $? -ne 0 ]; then
        log_error "无法获取健康检查响应"
        return 1
    fi
    
    # 如果有jq，验证JSON格式
    if command -v jq &> /dev/null; then
        if echo "$health_response" | jq . > /dev/null 2>&1; then
            local status
            status=$(echo "$health_response" | jq -r '.status // "unknown"')
            if [ "$status" = "healthy" ]; then
                log_success "API健康状态正常"
            else
                log_warning "API健康状态: $status"
            fi
        else
            log_error "API响应不是有效的JSON格式"
            return 1
        fi
    else
        log_info "跳过JSON格式验证（jq未安装）"
    fi
    
    return 0
}

# 运行功能测试
run_functional_tests() {
    log_info "运行功能测试..."
    
    local test_args=("--url" "$API_URL")
    
    if $PYTHON_CMD tests/test_api_stability.py "${test_args[@]}"; then
        log_success "功能测试通过"
        return 0
    else
        log_error "功能测试失败"
        return 1
    fi
}

# 运行安全测试
run_security_tests() {
    log_info "运行安全测试..."
    
    if $PYTHON_CMD tests/test_security.py --url "$API_URL"; then
        log_success "安全测试通过"
        return 0
    else
        log_error "安全测试失败"
        return 1
    fi
}

# 运行负载测试
run_load_tests() {
    if $SKIP_LOAD_TEST; then
        log_info "跳过负载测试（--skip-load）"
        return 0
    fi
    
    log_info "运行负载测试..."
    
    # 检查locust是否安装
    if ! $PYTHON_CMD -c "import locust" 2>/dev/null; then
        log_warning "Locust未安装，跳过负载测试"
        log_info "安装方法: pip install locust"
        return 0
    fi
    
    # 运行简短的负载测试
    if locust -f tests/test_load_performance.py \
              --host "$API_URL" \
              --users 5 \
              --spawn-rate 1 \
              --run-time 30s \
              --headless \
              --csv=load_test_results; then
        log_success "负载测试完成"
        
        # 如果有CSV结果文件，显示摘要
        if [ -f "load_test_results_stats.csv" ]; then
            log_info "负载测试结果摘要:"
            tail -n 1 load_test_results_stats.csv | awk -F',' '{
                printf "  - 平均响应时间: %s ms\n", $7
                printf "  - 请求总数: %s\n", $3
                printf "  - 失败请求: %s\n", $4
            }'
        fi
        
        return 0
    else
        log_error "负载测试失败"
        return 1
    fi
}

# 运行性能监控
run_performance_monitoring() {
    if $SKIP_MONITORING; then
        log_info "跳过性能监控（--skip-monitoring）"
        return 0
    fi
    
    log_info "运行性能监控测试（60秒）..."
    
    if timeout $TIMEOUT $PYTHON_CMD tests/test_performance_monitor.py \
                                   --url "$API_URL" \
                                   --duration 60; then
        log_success "性能监控测试完成"
        return 0
    else
        log_error "性能监控测试失败"
        return 1
    fi
}

# 运行完整测试套件
run_complete_test_suite() {
    log_info "运行完整测试套件..."
    
    local test_args=("--url" "$API_URL")
    
    if $SKIP_LOAD_TEST; then
        test_args+=("--quick")
    else
        test_args+=("--load-test")
    fi
    
    if ! $SKIP_MONITORING; then
        test_args+=("--monitoring")
    fi
    
    if timeout $TIMEOUT $PYTHON_CMD tests/test_runner.py "${test_args[@]}"; then
        log_success "完整测试套件通过"
        return 0
    else
        log_error "完整测试套件失败"
        return 1
    fi
}

# 收集测试报告
collect_test_reports() {
    log_info "收集测试报告..."
    
    local report_dir="test_reports_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$report_dir"
    
    # 移动所有测试报告文件
    find . -maxdepth 1 -name "*test*report*.md" -exec mv {} "$report_dir/" \; 2>/dev/null || true
    find . -maxdepth 1 -name "*test*results*.json" -exec mv {} "$report_dir/" \; 2>/dev/null || true
    find . -maxdepth 1 -name "*test*report*.csv" -exec mv {} "$report_dir/" \; 2>/dev/null || true
    find . -maxdepth 1 -name "load_test_results*" -exec mv {} "$report_dir/" \; 2>/dev/null || true
    find . -maxdepth 1 -name "performance_metrics*" -exec mv {} "$report_dir/" \; 2>/dev/null || true
    
    # 创建测试摘要
    cat > "$report_dir/test_summary.txt" << EOF
API 部署测试摘要

测试时间: $(date)
测试环境: $ENV
API地址: $API_URL
超时设置: ${TIMEOUT}秒

测试配置:
- 跳过负载测试: $SKIP_LOAD_TEST
- 跳过性能监控: $SKIP_MONITORING

详细报告请查看此目录下的其他文件。
EOF
    
    log_success "测试报告已收集到: $report_dir"
    return 0
}

# 部署前测试
pre_deployment_test() {
    log_info "=== 部署前测试 ==="
    
    local failed_tests=0
    
    # 基础连通性测试
    if ! check_api_connectivity; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if ! verify_api_response; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # 功能和安全测试
    if ! run_functional_tests; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if ! run_security_tests; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if [ $failed_tests -eq 0 ]; then
        log_success "部署前测试全部通过"
        return 0
    else
        log_error "部署前测试有 $failed_tests 项失败"
        return 1
    fi
}

# 部署后测试
post_deployment_test() {
    log_info "=== 部署后测试 ==="
    
    local failed_tests=0
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 重新检查连通性
    if ! check_api_connectivity; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if ! verify_api_response; then
        failed_tests=$((failed_tests + 1))
    fi
    
    # 运行完整测试
    if ! run_complete_test_suite; then
        failed_tests=$((failed_tests + 1))
    fi
    
    if [ $failed_tests -eq 0 ]; then
        log_success "部署后测试全部通过"
        return 0
    else
        log_error "部署后测试有 $failed_tests 项失败"
        return 1
    fi
}

# 主函数
main() {
    log_info "开始API部署测试"
    log_info "目标API: $API_URL"
    log_info "测试环境: $ENV"
    log_info "超时设置: ${TIMEOUT}秒"
    echo "================================"
    
    # 检查依赖
    check_dependencies
    
    # 激活虚拟环境
    activate_venv
    
    local test_mode="${1:-full}"
    local exit_code=0
    
    case $test_mode in
        "pre")
            pre_deployment_test || exit_code=1
            ;;
        "post")
            post_deployment_test || exit_code=1
            ;;
        "full"|*)
            pre_deployment_test || exit_code=1
            if [ $exit_code -eq 0 ]; then
                post_deployment_test || exit_code=1
            fi
            ;;
    esac
    
    # 收集报告
    collect_test_reports
    
    echo "================================"
    if [ $exit_code -eq 0 ]; then
        log_success "所有测试通过！API可以安全部署。"
    else
        log_error "测试失败！请检查问题后重新测试。"
    fi
    
    exit $exit_code
}

# 如果作为脚本直接运行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 