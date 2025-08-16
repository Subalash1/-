#!/bin/bash

echo "===== 中文四字词语猜词游戏 ====="
echo

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv
    echo "虚拟环境创建完成！"
    echo
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install flask pypinyin
echo

# 启动游戏
echo "启动游戏服务器..."
echo "游戏地址: http://localhost:5000"
echo "按 Ctrl+C 停止游戏"
echo
python app.py