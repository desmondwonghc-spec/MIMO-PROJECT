@echo off
chcp 65001 >nul 2>&1
title HR智能简历筛选系统
echo.
echo  ╔══════════════════════════════════════╗
echo  ║    HR智能简历筛选系统 - 启动中...    ║
echo  ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0backend"

echo [1/3] 检查 MongoDB...
mongod --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ⚠ 未检测到 MongoDB，请确保 MongoDB 已启动
    echo.
) else (
    echo  ✓ MongoDB 已就绪
)

echo [2/3] 检查前端构建产物...
if not exist "%~dp0frontend\dist\index.html" (
    echo  ⚠ 前端未构建，正在构建...
    cd /d "%~dp0frontend"
    call npm run build
    cd /d "%~dp0backend"
)
echo  ✓ 前端已就绪

echo [3/3] 启动应用...
echo.
echo  ┌────────────────────────────────────┐
echo  │  应用启动中，请稍候...             │
echo  │  窗口将在几秒后自动弹出            │
echo  │  按 Ctrl+C 可关闭                  │
echo  └────────────────────────────────────┘
echo.

set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe main.py

pause
