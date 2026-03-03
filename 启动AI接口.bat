@echo off
chcp 65001 >nul
title TODO系统 - AI接口服务

echo ========================================
echo    TODO系统 AI工具接口服务
echo ========================================
echo.

:: 启动AI接口服务
echo 🚀 启动AI接口服务 (端口 8001)...
cd /d "%~dp0"
start "TODO AI Interface" cmd /k "python ai_interface.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    服务启动完成！
echo ========================================
echo.
echo 🌐 AI接口地址: http://localhost:8001/ai
echo.
echo 📱 测试命令:
echo    python test_ai_interface.py
echo.
echo 💡 提示:
echo    - API文档：http://localhost:8001/docs
echo    - 按 Ctrl+C 可停止此窗口
echo    - 关闭窗口不会影响AI服务运行
echo.
echo 按任意键退出...
pause >nul