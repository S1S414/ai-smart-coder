@echo off
chcp 65001 >nul
title AI代码助手 - Port 5001
cd /d "%~dp0"
echo ================================
echo   AI代码助手 - Flask后端服务
echo   访问地址: http://localhost:5001
echo ================================
echo.
python app.py
pause
