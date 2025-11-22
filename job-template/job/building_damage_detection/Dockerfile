FROM python:3.9

ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 安装系统依赖（OpenCV 需要）
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件（包括模型）
COPY app.py .
COPY models/ ./models/

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:${PYTHONPATH:-} \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

# 暴露端口（Gradio 默认端口 7860）
EXPOSE 7860

# 启动应用
CMD ["python", "app.py"]

