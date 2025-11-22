FROM python:3.9

ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY main.py .
COPY config.yml .
COPY accessdb.sql .
COPY Model/ ./Model/
COPY Utiles/ ./Utiles/
COPY WebAPI/ ./WebAPI/
COPY frontend_dist/ ./frontend_dist/
COPY WordDir/ ./WordDir/

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:${PYTHONPATH:-} \
    MYSQL_HOST=mysql-service.infra \
    MYSQL_PORT=3306 \
    MYSQL_USER=root \
    MYSQL_PASSWORD=admin \
    MYSQL_DATABASE=AccessDB \
    SERVER_IP=0.0.0.0 \
    SERVER_PORT=10086 \
    CURRENT_DIR=/app

# 暴露端口（默认 10086，可通过环境变量 SERVER_PORT 配置）
EXPOSE 10086

# 启动应用
CMD ["python", "main.py"]

