@echo off
chcp 65001 >nul
echo ========================================
echo   AI Chat Guardian - 快速打包工具
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 激活虚拟环境...
call venv_pack\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败！
    pause
    exit /b 1
)

echo [2/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/5] 开始打包...
pyinstaller --clean --noconfirm AI_Chat_Guardian_Fixed.spec
if errorlevel 1 (
    echo ❌ 打包失败！
    pause
    exit /b 1
)

echo [4/5] 执行打包后处理...
python post_build.py
if errorlevel 1 (
    echo ❌ 后处理失败！
    pause
    exit /b 1
)

echo [5/5] 完成打包...

echo.
echo ========================================
echo ✅ 打包完成！
echo ========================================
echo.
echo 📦 可执行程序位置：
echo    dist\AI_Chat_Guardian\AI_Chat_Guardian.exe
echo.
echo 📂 目录结构：
echo    dist\AI_Chat_Guardian\
echo      ├── AI_Chat_Guardian.exe
echo      ├── config\              ← 配置文件（可编辑）
echo      ├── examples\            ← 示例文件
echo      ├── .env.example         ← API密钥模板
echo      ├── README.md
echo      └── _internal\           ← 依赖文件
echo.
echo 💡 下一步：
echo    1. 复制 .env.example 为 .env 并填入API密钥
echo    2. 测试运行 dist\AI_Chat_Guardian\AI_Chat_Guardian.exe
echo    3. 压缩 dist\AI_Chat_Guardian 文件夹分发
echo.
pause
