@echo off
REM AI Chat Guardian Web服务启动脚本 (Windows)
echo ========================================
echo AI Chat Guardian Web服务启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查是否需要安装依赖
if not exist "venv\" (
    echo [信息] 首次运行，正在安装依赖...
    pip install flask flask-cors requests pyyaml colorama
    echo.
)

REM 设置环境变量(避免OpenMP冲突)
set KMP_DUPLICATE_LIB_OK=TRUE

REM 启动Web服务
echo [信息] 启动Web服务...
echo [信息] 访问地址: http://localhost:5000
echo [信息] 按 Ctrl+C 停止服务
echo.

python web_server.py --host 0.0.0.0 --port 5000

pause
