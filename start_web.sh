#!/bin/bash
# AI Chat Guardian Web服务启动脚本 (Linux/Mac)

echo "========================================"
echo "AI Chat Guardian Web服务启动"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查依赖
if [ ! -d "venv" ]; then
    echo "[信息] 首次运行，正在安装依赖..."
    pip3 install flask flask-cors requests pyyaml colorama
    echo ""
fi

# 启动Web服务
echo "[信息] 启动Web服务..."
echo "[信息] 访问地址: http://localhost:5000"
echo "[信息] 按 Ctrl+C 停止服务"
echo ""

python3 web_server.py --host 0.0.0.0 --port 5000
