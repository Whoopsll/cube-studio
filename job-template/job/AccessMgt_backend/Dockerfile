FROM ccr.ccs.tencentyun.com/cube-studio/ubuntu-gpu:cuda11.8.0-cudnn8-python3.9

# 设置工作目录
WORKDIR /app

# 更新系统并安装必要的依赖
RUN apt update -y && \
    apt-get install -y python3.9-dev && \
    rm -rf /var/lib/apt/lists/*

# 安装Python依赖包
RUN pip install fastapi>=0.104.0 \
                uvicorn[standard]>=0.24.0 \
                sqlalchemy>=2.0.0 \
                pymysql>=1.1.0 \
                pyyaml>=6.0 \
                python-docx>=1.1.0 \
                numexpr>=2.8.0 \
                numpy>=1.24.0 \
                pandas>=2.0.0 \
                scipy>=1.11.0 \
                scikit-learn>=1.3.0 \
                --index-url https://mirrors.aliyun.com/pypi/simple

# 复制项目文件（从构建上下文根目录）
COPY AccessMgtServer/ /app/

# 创建必要的目录
RUN mkdir -p /app/WordDir

# 设置环境变量
ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app:/src/:/github/
ENV NODE_PATH=$NODE_HOME/lib/node_modules:${PATH:-}
ENV PATH=$NODE_HOME/bin:${PATH:-}

# 修复Python3链接
RUN rm -rf /usr/bin/python3 && ln -s /usr/bin/python /usr/bin/python3

# 暴露端口
EXPOSE 10086

# 设置入口点（优先使用launcher.py，支持环境变量配置）
ENTRYPOINT ["python", "launcher.py"]

