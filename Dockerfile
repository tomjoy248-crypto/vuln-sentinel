# 漏洞哨兵 11-S - 生产环境 Dockerfile（多阶段构建）
#
# 构建：docker build -t vuln-sentinel .
# 运行：docker run -p 8000:8000 -e JWT_SECRET=xxx vuln-sentinel

# ---------- 阶段 1：构建前端 ----------
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# 仅复制依赖描述文件以最大化利用缓存
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# 复制前端源码并构建
COPY frontend/ ./
RUN npm run build


# ---------- 阶段 2：Python 后端 ----------
FROM python:3.11-slim AS backend

# 安全：创建非 root 运行用户
RUN groupadd --gid 1000 vulnuser && \
    useradd --uid 1000 --gid vulnuser --create-home --shell /bin/bash vulnuser

WORKDIR /app

# 安装系统依赖与健康检查工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建持久化数据目录并授权给非 root 用户
RUN mkdir -p /data && chown -R vulnuser:vulnuser /data

# 先复制依赖文件，利用 Docker 缓存层
COPY --chown=vulnuser:vulnuser requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 复制应用代码（.dockerignore 已排除不需要的文件）
COPY --chown=vulnuser:vulnuser . .

# 用构建好的前端产物覆盖 static/ 目录
COPY --from=frontend-builder --chown=vulnuser:vulnuser /frontend/dist/ ./static/

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/vulnuser/.local/bin:${PATH}" \
    PORT=8000

# 切换到非 root 用户
USER vulnuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:${PORT}/health/ready || exit 1

# 生产环境使用 Gunicorn + Uvicorn Worker
CMD ["sh", "-c", "gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile -"]
