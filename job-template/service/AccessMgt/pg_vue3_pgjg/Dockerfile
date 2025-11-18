# 构建阶段
FROM node:18-alpine AS build

WORKDIR /src

# 复制依赖文件
COPY package*.json ./
RUN npm ci

# 复制源代码
COPY . .

# 构建前端
RUN npm run build

# 运行阶段
FROM nginx:1.25-alpine

# 复制构建产物
COPY --from=build /src/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

