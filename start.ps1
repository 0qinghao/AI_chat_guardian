# AI Chat Guardian 快速启动脚本 (PowerShell)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "AI Chat Guardian 快速启动" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python是否安装
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "错误: 未找到Python，请先安装Python 3.7+" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Python版本:" -ForegroundColor Green
python --version
Write-Host ""

# 检查依赖
Write-Host "检查依赖..." -ForegroundColor Yellow
$needInstall = $false

try {
    python -c "import colorama" 2>$null
} catch {
    $needInstall = $true
}

try {
    python -c "import yaml" 2>$null
} catch {
    $needInstall = $true
}

if ($needInstall) {
    Write-Host "需要安装依赖包..." -ForegroundColor Yellow
    Write-Host "正在安装基础依赖..." -ForegroundColor Yellow
    pip install colorama pyyaml
    Write-Host ""
}

# 显示菜单
Write-Host "请选择启动模式:" -ForegroundColor Cyan
Write-Host "1. 命令行模式 (CLI)" -ForegroundColor White
Write-Host "2. 图形界面模式 (GUI)" -ForegroundColor White
Write-Host "3. 运行测试" -ForegroundColor White
Write-Host "4. 退出" -ForegroundColor White
Write-Host ""

$choice = Read-Host "请输入选项 (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "启动命令行模式..." -ForegroundColor Green
        python main.py
    }
    "2" {
        Write-Host ""
        Write-Host "启动图形界面..." -ForegroundColor Green
        python gui.py
    }
    "3" {
        Write-Host ""
        Write-Host "运行测试..." -ForegroundColor Green
        python tests/test_basic.py
    }
    "4" {
        Write-Host "再见！" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "无效选项" -ForegroundColor Red
    }
}

Write-Host ""
pause
