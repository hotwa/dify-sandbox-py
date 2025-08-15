#!/bin/bash
# 激活 micromamba 环境
eval "$(micromamba shell hook --shell bash)"
micromamba activate base

# 检查并安装动态依赖
if [ -f "/dependencies/python-requirements.txt" ]; then
    echo "Dependency file found, starting to install additional dependencies..."
    micromamba install -y -n base -c conda-forge --file /dependencies/python-requirements.txt || true
    micromamba run -n base pip install -r /dependencies/python-requirements.txt || true
fi

# 启动应用
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8194

