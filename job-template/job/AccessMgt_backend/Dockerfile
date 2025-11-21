FROM python:3.9

ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

# 更新系统并安装必要的系统依赖
RUN apt update -y && \
    apt install -y vim wget python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# 安装Python依赖包
RUN pip install fastapi>=0.104.0 \
                uvicorn[standard]>=0.24.0 \
                sqlalchemy>=2.0.0 \
                pymysql>=1.1.0 \
                pyyaml>=6.0 \
                python-docx>=1.1.0 \
                python-multipart>=0.0.6 \
                numexpr>=2.8.0 \
                numpy>=1.24.0 \
                pandas>=2.0.0 \
                scipy>=1.11.0 \
                scikit-learn>=1.3.0 \
                pysnooper \
                psutil \
                requests \
                --index-url https://mirrors.aliyun.com/pypi/simple

# 复制项目文件（从当前构建上下文）
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/WordDir

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 10086

# 设置入口点（支持环境变量配置）
ENTRYPOINT ["python3", "main.py"]

