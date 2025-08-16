@echo off
echo ===== 中文四字词语猜词游戏 =====
echo.

:: 检查虚拟环境是否存在
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建完成！
    echo.
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

:: 安装依赖
echo 检查并安装依赖...
pip install flask pypinyin
echo.

:: 启动游戏
echo 启动游戏服务器...
echo 游戏地址: http://localhost:5000
echo 按 Ctrl+C 停止游戏
echo.
python app.py

pause