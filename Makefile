# Impromptu 匹配系统 Makefile

.PHONY: help install setup train demo api web test clean check backend frontend dev-all stop status logs

help: ## 显示帮助信息
	@echo "Impromptu - AI社交匹配算法系统"
	@echo "================================"
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

check: ## 检查环境配置
	@echo "🔍 检查环境配置..."
	python scripts/setup/check_environment.py

install: ## 安装项目依赖
	@echo "📦 安装项目依赖..."
	bash scripts/setup/install.sh

setup: install ## 完整项目设置
	@echo "✅ 项目设置完成"

train: ## 训练模型
	@echo "🧠 开始模型训练..."
	python scripts/train/train_models.py

demo: ## 运行命令行演示
	@echo "📱 启动命令行演示..."
	python scripts/demo/main.py

# ===================
# 后端服务命令
# ===================
backend: ## 启动后端API服务 (FastAPI)
	@echo "🌐 启动后端API服务..."
	bash scripts/setup/start_backend.sh

api: backend ## 启动API服务（backend的别名）

backend-simple: ## 启动简单后端服务
	@echo "🔧 启动简单后端服务..."
	cd backend && python main.py simple

# ===================
# 前端服务命令  
# ===================
frontend: ## 启动前端服务 (Next.js)
	@echo "💻 启动前端服务..."
	bash scripts/setup/start_frontend.sh

web: frontend ## 启动Web界面（frontend的别名）

frontend-build: ## 构建前端生产版本
	@echo "🏗️ 构建前端..."
	cd frontend && npm run build

frontend-prod: ## 启动前端生产服务
	@echo "🚀 启动前端生产服务..."
	cd frontend && npm run start

# ===================
# 开发模式命令
# ===================
dev-all: ## 开发模式 - 同时启动前端和后端 (自动清理端口)
	@echo "🚀 开发模式启动 - 前端和后端"
	@echo "🧹 自动清理端口冲突..."
	@bash scripts/setup/manage_ports.sh clean || true
	@sleep 1
	@echo "正在启动后端服务 (后台运行)..."
	@bash scripts/setup/start_backend.sh &
	@sleep 5
	@echo "正在启动前端服务..."
	@bash scripts/setup/start_frontend.sh

dev: ## 开发模式（自动清理端口+启动服务）
	@echo "⚡ 开发模式快速启动（含端口清理）"
	@make clean-ports
	@make dev-all

dev-backend: ## 仅开发模式启动后端 (含端口清理)
	@echo "🌐 开发模式 - 仅后端（含端口清理）..."
	@bash scripts/setup/manage_ports.sh clean || true
	@sleep 1
	@bash scripts/setup/start_backend.sh

dev-frontend: ## 仅开发模式启动前端 (含端口清理)
	@echo "💻 开发模式 - 仅前端（含端口清理）..."
	@bash scripts/setup/manage_ports.sh clean || true
	@sleep 1  
	@bash scripts/setup/start_frontend.sh

# ===================
# 测试命令
# ===================
test: ## 运行测试
	@echo "🧪 运行测试..."
	python -m pytest tests/ -v

test-api: ## 测试API接口
	@echo "🔍 测试API接口..."
	python scripts/demo/test_api_client.py

# ===================
# 管理命令
# ===================
clean-ports: ## 清理端口冲突（安全方式）
	@echo "🧹 清理端口冲突..."
	@bash scripts/setup/manage_ports.sh clean
	@echo "✅ 端口清理完成"

stop: ## 停止所有服务
	@echo "🛑 停止所有服务..."
	@pkill -f "uvicorn.*main_api" || true
	@pkill -f "python.*backend.*main" || true
	@pkill -f "next.*dev" || true
	@pkill -f "node.*next.*dev" || true
	@pkill -f "npm.*run.*dev" || true
	@echo "✅ 服务已停止"

kill-ports: ## 强制清理所有相关端口（危险操作）
	@echo "💥 强制清理所有开发端口..."
	@echo "⚠️  这将终止3000、5000、8000、8001端口的所有进程"
	@lsof -ti :3000 2>/dev/null | xargs kill -9 2>/dev/null || true
	@lsof -ti :8000 2>/dev/null | xargs kill -9 2>/dev/null || true  
	@lsof -ti :8001 2>/dev/null | xargs kill -9 2>/dev/null || true
	@echo "✅ 强制清理完成"

status: ## 检查服务状态
	@echo "📊 服务状态检查..."
	@bash scripts/setup/manage_ports.sh status

logs: ## 查看日志
	@echo "📋 最近日志:"
	@find . -name "*.log" -type f -exec ls -lt {} + 2>/dev/null | head -5 || echo "  无日志文件"

clean: ## 清理临时文件
	@echo "🧹 清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf frontend/.next/
	rm -rf frontend/node_modules/.cache/

# ===================
# 快速命令
# ===================
quick-start: ## 快速启动（检查+安装+清理端口+开发模式）
	@echo "⚡ 快速启动流程..."
	@make check
	@make install
	@make dev

restart: ## 重启所有服务（含端口清理）
	@echo "🔄 重启所有服务..."
	@make clean-ports
	@sleep 2
	@make dev-all

force-restart: ## 强制重启（清理所有+重新启动）
	@echo "💪 强制重启所有服务..."
	@make stop
	@make clean-ports
	@sleep 3
	@make dev-all

.DEFAULT_GOAL := help 