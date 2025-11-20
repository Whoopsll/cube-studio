FROM python:3.10-slim

WORKDIR /app

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . /app

ENV PORT=8080 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

# 使用 gunicorn 启动 FastAPI 应用
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 4 --worker-class uvicorn.workers.UvicornWorker app:app"]
