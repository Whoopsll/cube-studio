# 多阶段构建：第一阶段构建 Vue 应用
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install --registry=https://registry.npmmirror.com

# 复制源代码
COPY . .

# 构建应用（环境变量可在构建时注入）
ARG VITE_API_BASE_URL=http://127.0.0.1:10086
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# 第二阶段：使用 Nginx 提供静态文件服务
FROM nginx:alpine

# 复制构建产物到 Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 创建 Nginx 配置文件
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # 支持 Vue Router History 模式 \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # 静态资源缓存 \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    \
    # 允许跨域访问 config.js（用于动态配置） \
    location /config.js { \
        add_header Access-Control-Allow-Origin *; \
        add_header Access-Control-Allow-Methods "GET, OPTIONS"; \
    } \
}' > /etc/nginx/conf.d/default.conf

# 设置权限
RUN chmod -R 755 /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 使用启动脚本（支持环境变量配置）
ENTRYPOINT ["/entrypoint.sh"]

