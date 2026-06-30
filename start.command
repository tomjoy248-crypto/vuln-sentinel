#!/bin/bash
cd "$(dirname "$0")"
clear
echo "============================================"
echo "   漏洞哨兵 11-S - 一键启动"
echo "============================================"
echo ""
echo "提示：双击 static/index.html 也可直接离线演示"
echo "     （免启动后端，账号 demo / demo123）"
echo ""
echo "正在安装依赖..."
pip3 install -r requirements.txt --quiet --break-system-packages 2>/dev/null || pip3 install -r requirements.txt --quiet
echo "启动后端服务..."
echo ""
echo "============================================"
echo " 浏览器打开: http://localhost:8000"
echo " 测试账号:  demo / demo123"
echo " 离线演示:  直接双击 static/index.html"
echo " 按 Ctrl+C 停止"
echo "============================================"
echo ""
python3 main.py
