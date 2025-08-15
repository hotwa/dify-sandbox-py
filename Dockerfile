FROM mambaorg/micromamba:debian12-slim

# 安装Node.js
USER root
RUN apt-get update && \
    apt-get install -y curl git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 切换回 micromamba 用户
USER $MAMBA_USER

# 复制依赖文件
COPY requirements.txt .

# 创建并激活环境
RUN micromamba install -y -n base python=3.12 && \
    micromamba install -y -n base -c conda-forge fastapi uvicorn && \
    micromamba install -y -n base -c conda-forge --file requirements.txt && \
    git clone https://github.com/sichang824/mcp-terminal && \
    micromamba run -n base pip install -e mcp-terminal && \
    micromamba clean --all --yes

# 复制应用代码
COPY app/ ./app/
COPY start.sh .

USER root
RUN mkdir -p /dependencies && \
    chmod +x start.sh

EXPOSE 8194

# 确保使用 micromamba 环境启动
CMD ["micromamba", "run", "-n", "base", "./start.sh"]
