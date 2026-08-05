.PHONY: help install test test-frontend lint format security-check dependency-audit baseline-check build build-static clean run docker-build docker-up docker-up-prod docker-down

PYTHON := python3
PIP := $(PYTHON) -m pip

help:
	@echo "漏洞哨兵 11-S 常用命令"
	@echo "  make install          安装 Python 依赖"
	@echo "  make test             运行完整测试套件"
	@echo "  make lint             运行 ruff 代码质量检查"
	@echo "  make format           自动格式化代码"
	@echo "  make security-check   运行安全基线与依赖审计"
	@echo "  make dependency-audit 扫描依赖已知漏洞"
	@echo "  make baseline-check   检查生产环境安全配置"
	@echo "  make build            构建前端静态资源"
	@echo "  make build-static     构建前端并复制到 static/ 目录"
	@echo "  make test-frontend    运行前端测试"
	@echo "  make run              启动开发服务器"
	@echo "  make docker-build     构建 Docker 镜像"
	@echo "  make docker-up        启动本地 docker compose"
	@echo "  make docker-up-prod   启动生产 docker compose"
	@echo "  make docker-down      停止 docker compose"
	@echo "  make clean            清理构建产物与缓存"

install:
	$(PIP) install -r requirements.txt

test:
	pytest -q

test-frontend:
	cd frontend && npm install && npm test

lint:
	ruff check .

format:
	ruff check --fix .
	@ruff format . 2>/dev/null || echo "ruff format 不可用，跳过自动格式化"

security-check: baseline-check dependency-audit

baseline-check:
	$(PYTHON) scripts/security_baseline_check.py

dependency-audit:
	$(PYTHON) scripts/dependency_security_scan.py

build:
	cd frontend && npm install && npm run build

build-static: build
	rm -rf static/assets
	cp -r frontend/dist/assets static/assets
	cp -r frontend/dist/* static/ 2>/dev/null || true
	@echo "静态资源已复制到 static/ 目录"

run:
	$(PYTHON) main.py

docker-build:
	docker build -t vuln-sentinel:latest .

docker-up:
	docker compose up --build -d

docker-up-prod:
	docker compose -f docker-compose.prod.yml up --build -d

docker-down:
	docker compose down
	docker compose -f docker-compose.prod.yml down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf frontend/dist 2>/dev/null || true
	rm -rf static/assets 2>/dev/null || true
	rm -rf htmlcov 2>/dev/null || true
	rm -f .coverage 2>/dev/null || true
