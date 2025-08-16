@echo off
echo 激活虚拟环境...
if not exist "venv" (
    echo 虚拟环境不存在，正在创建...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo 虚拟环境已激活！
echo 可以运行: python app.py
cmd /k