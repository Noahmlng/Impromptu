# Impromptu 匹配系统 Makefile

.PHONY: help install setup train demo api web test clean check

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

api: ## 启动API服务
	@echo "🌐 启动API服务..."
	bash scripts/setup/start_api.sh

web: ## 启动Web界面
	@echo "💻 启动Web界面..."
	bash scripts/setup/start_web.sh

test: ## 运行测试
	@echo "🧪 运行测试..."
	python -m pytest tests/ -v

test-api: ## 测试API接口
	@echo "🔍 测试API接口..."
	python scripts/demo/test_api_client.py

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

dev: ## 开发模式 - 启动API和Web服务
	@echo "🚀 开发模式启动..."
	@echo "启动API服务 (后台运行)..."
	@bash scripts/setup/start_api.sh &
	@sleep 3
	@echo "启动Web界面..."
	@bash scripts/setup/start_web.sh

stop: ## 停止所有服务
	@echo "🛑 停止所有服务..."
	@pkill -f "python.*api_server" || true
	@pkill -f "python.*http.server" || true
	@echo "✅ 服务已停止"

status: ## 检查服务状态
	@echo "📊 服务状态检查..."
	@echo "API服务 (端口5000):"
	@lsof -Pi :5000 -sTCP:LISTEN >/dev/null && echo "  ✅ 运行中" || echo "  ❌ 未运行"
	@echo "Web服务 (端口8000):"
	@lsof -Pi :8000 -sTCP:LISTEN >/dev/null && echo "  ✅ 运行中" || echo "  ❌ 未运行"

logs: ## 查看日志
	@echo "📋 最近日志:"
	@find . -name "*.log" -type f -exec ls -lt {} + 2>/dev/null | head -5 || echo "  无日志文件"

.DEFAULT_GOAL := help 