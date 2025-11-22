FROM python:3.9

ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY app.py .
COPY templates/ ./templates/

# 设置环境变量
ENV PORT=8080 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:${PYTHONPATH:-}

EXPOSE 8080

# 使用 gunicorn + uvicorn workers 启动 FastAPI 应用（生产环境推荐）
# 也可以直接使用 uvicorn（开发环境）：CMD ["python", "app.py"]
CMD ["sh", "-c", "gunicorn --bind ${HOST:-0.0.0.0}:${PORT:-8080} --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 app:app"]

