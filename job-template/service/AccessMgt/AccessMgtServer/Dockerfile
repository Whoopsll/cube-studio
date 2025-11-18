FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 默认从环境变量读取 MySQL 配置；如未设置则回退到 config.yml 中的值
ENV MYSQL_HOST=mysql-service.infra \
    MYSQL_PORT=3306 \
    MYSQL_USER=root \
    MYSQL_PASSWORD=admin \
    MYSQL_DB=AccessDB \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=10086

EXPOSE 10086

CMD ["python", "main.py"]


