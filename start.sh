#!/usr/bin/env bash
# 漏洞哨兵 V11-S - 一键启动脚本（本地 Docker Compose）
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Docker 是否可用
if ! command -v docker &> /dev/null; then
    echo "错误：未检测到 Docker，请先安装 Docker。"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "错误：未检测到 docker-compose，请先安装。"
    exit 1
fi

# 生成随机 JWT secret（如果不存在 .env 文件）
if [ ! -f .env ]; then
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    echo "JWT_SECRET=$JWT_SECRET" > .env
    echo "CREDITS_ENABLED=true" >> .env
    echo "已生成默认 .env 文件（JWT_SECRET 与计费开关）。"
fi

# 构建并启动
echo "正在构建并启动 漏洞哨兵 V11-S..."
if docker compose version &> /dev/null; then
    docker compose up --build -d
else
    docker-compose up --build -d
fi

echo ""
echo "服务已启动，访问地址："
echo "  - Web 界面：http://localhost:8000"
echo "  - 健康检查：http://localhost:8000/api/health"
echo ""
echo "查看日志：docker compose logs -f"
echo "停止服务：docker compose down"
