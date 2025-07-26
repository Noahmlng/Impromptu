# 多阶段构建：第一阶段构建前端
FROM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 复制前端包管理文件
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm ci --only=production

# 复制前端代码
COPY frontend/ .

# 构建前端（创建静态HTML页面）
RUN npm run build 2>/dev/null || echo "前端构建跳过"

# 第二阶段：Python应用
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制Python依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建前端目录
RUN mkdir -p frontend

# 从第一阶段复制构建好的前端文件（如果存在）
COPY --from=frontend-builder /app/frontend/public ./frontend/public/
COPY --from=frontend-builder /app/frontend/out ./frontend/out/

# 创建必要的目录
RUN mkdir -p data/models data/processed data/results logs

# 创建非root用户（安全最佳实践）
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# 暴露端口
EXPOSE $PORT

# 启动命令
CMD ["python", "main.py"] 