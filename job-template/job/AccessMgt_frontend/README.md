# AccessMgt 前端服务

AccessMgt 评估管理系统的前端应用，基于 Vue 3 + Vite + Element Plus 构建。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue 状态管理
- **Axios** - HTTP 客户端
- **ECharts** - 数据可视化图表库
- **AntV G6** - 图可视化引擎

## 目录结构

```
AccessMgt_frontend/
├── public/              # 静态资源目录
│   ├── config.js        # 接口配置文件（打包后可修改）
│   └── favicon.ico      # 网站图标
├── src/                 # 源代码目录
│   ├── api/            # API 接口定义
│   ├── assets/         # 资源文件（CSS、图片等）
│   ├── components/     # Vue 组件
│   ├── router/         # 路由配置
│   ├── stores/         # Pinia 状态管理
│   ├── utils/          # 工具函数
│   ├── views/          # 页面视图
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── Dockerfile          # Docker 镜像构建文件
├── build.sh            # 构建并推送镜像脚本
├── package.json        # 项目依赖配置
└── vite.config.js      # Vite 配置文件
```

## 本地开发

### 1. 安装依赖

```bash
cd job-template/job/AccessMgt_frontend
npm install
```

### 2. 配置后端接口地址

编辑 `public/config.js` 文件，修改后端 API 地址：

```javascript
window.appConfig = {
  baseURL: 'http://127.0.0.1:10086', // 修改为实际的后端地址
  timeout: 5000,
};
```

### 3. 启动开发服务器

```bash
npm run dev
```

默认访问地址：`http://localhost:8000`

### 4. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

## Docker 部署

### 构建镜像

```bash
cd job-template/job/AccessMgt_frontend
chmod +x build.sh
./build.sh
```

### 手动构建

```bash
docker build --network=host -t 47.116.204.159:8089/cube/accessmgt_frontend:20251121 -f Dockerfile .
docker push 47.116.204.159:8089/cube/accessmgt_frontend:20251121
```

### 运行容器

```bash
# 方式1：使用环境变量配置后端地址（推荐）
docker run -d \
  -p 8000:80 \
  -e API_BASE_URL=http://accessmgt-backend-service:10086 \
  47.116.204.159:8089/cube/accessmgt_frontend:20251121

# 方式2：如果后端在同一主机，使用主机网络
docker run -d \
  -p 8000:80 \
  -e API_BASE_URL=http://host.docker.internal:10086 \
  47.116.204.159:8089/cube/accessmgt_frontend:20251121

# 方式3：Kubernetes 环境，使用 Service 名称
docker run -d \
  -p 8000:80 \
  -e API_BASE_URL=http://accessmgt-backend-service.default.svc.cluster.local:10086 \
  47.116.204.159:8089/cube/accessmgt_frontend:20251121
```

## 环境变量配置

### 运行时环境变量（推荐）

容器启动时通过环境变量配置，无需重新构建镜像：

- `API_BASE_URL` - 后端 API 地址（默认: `http://accessmgt-backend:10086`）
- `API_TIMEOUT` - 请求超时时间，单位毫秒（默认: `5000`）

### Cube Studio 配置说明

在 Cube Studio 中部署时，后端服务监听在 `0.0.0.0:10086`，前端需要通过 Kubernetes Service 名称访问：

1. **查找后端服务名称**：
   - 在 Cube Studio 中查看后端服务的 Service 名称
   - 通常格式为：`<任务名>-service` 或 `<任务名>`
   - 例如：如果后端任务名为 `accessmgt-backend`，Service 名称通常也是 `accessmgt-backend`

2. **配置前端环境变量**：
   ```yaml
   env:
     - name: API_BASE_URL
       value: "http://<后端服务名>:10086"  # 例如：http://accessmgt-backend:10086
   ```

3. **同一命名空间**：如果前后端在同一命名空间，直接使用服务名即可
4. **不同命名空间**：使用完整域名 `http://<服务名>.<命名空间>.svc.cluster.local:10086`

**示例：**

```bash
# Kubernetes Deployment 配置（Cube Studio）
env:
  - name: API_BASE_URL
    value: "http://accessmgt-backend:10086"  # 使用后端服务的 Service 名称
  - name: API_TIMEOUT
    value: "5000"
```

### 构建时环境变量

- `VITE_API_BASE_URL` - 后端 API 地址（构建时注入，不推荐，建议使用运行时环境变量）

## 部署到 Cube Studio

### 服务配置示例

```json
{
  "模型信息": {
    "--label": {
      "type": "str",
      "label": "中文描述",
      "default": "AccessMgt 前端服务",
      "describe": "评估管理系统前端"
    },
    "--model_name": {
      "type": "str",
      "label": "服务名",
      "default": "accessmgt_frontend",
      "describe": "前端服务名称"
    }
  },
  "资源配置": {
    "cpu": "1",
    "memory": "1Gi",
    "gpu": "0"
  },
  "环境变量": {
    "API_BASE_URL": {
      "type": "str",
      "label": "后端API地址",
      "default": "http://127.0.0.1:10086",
      "describe": "后端服务的访问地址"
    }
  }
}
```

## 功能模块

- **仪表盘** - 数据概览和统计
- **分析视图** - 数据分析与可视化
- **结果管理** - 评估结果查看和管理
- **报告生成** - 报告创建和导出
- **用户管理** - 用户信息管理
- **工作流** - 工作流程配置
- **推理数据** - 数据推理和分析

## 接口配置

前端通过环境变量在容器启动时动态配置后端 API 地址：

1. **运行时配置（推荐）**：通过 `API_BASE_URL` 环境变量配置，容器启动时自动生成 `config.js`
2. **构建时配置**：修改 `public/config.js` 后重新构建（不推荐，灵活性差）

### Kubernetes 配置示例

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: accessmgt-frontend
spec:
  template:
    spec:
      containers:
      - name: frontend
        image: 47.116.204.159:8089/cube/accessmgt_frontend:20251121
        ports:
        - containerPort: 80
        env:
        - name: API_BASE_URL
          value: "http://accessmgt-backend-service:10086"
        - name: API_TIMEOUT
          value: "5000"
```

### 后端服务地址说明

在 Cube Studio/Kubernetes 环境中：

1. **后端服务监听地址**：`0.0.0.0:10086`（容器内部）
2. **前端访问地址**：使用 Kubernetes Service 名称

**查找 Service 名称的方法**：
```bash
# 在 Cube Studio 中查看后端服务的 Service
kubectl get svc -n <命名空间> | grep accessmgt

# 或者查看后端任务的详细信息，Service 名称通常在任务配置中
```

**常见配置**：
- **同一命名空间**：`http://<后端服务名>:10086`
- **不同命名空间**：`http://<后端服务名>.<命名空间>.svc.cluster.local:10086`
- **默认命名空间**：`http://<后端服务名>.default.svc.cluster.local:10086`

**示例**：
- 如果后端 Service 名为 `accessmgt-backend`：`http://accessmgt-backend:10086`
- 如果后端 Service 名为 `admin-pipeline-xxx-accessmgt-backend`：`http://admin-pipeline-xxx-accessmgt-backend:10086`

## 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 注意事项

1. **跨域问题**：确保后端服务已配置 CORS，允许前端域名访问
2. **API 地址**：生产环境建议使用环境变量或配置文件动态设置
3. **静态资源**：构建后的静态资源通过 Nginx 提供服务
4. **路由模式**：使用 History 模式，需要 Nginx 配置支持

## 故障排查

### 接口请求失败

1. 检查 `public/config.js` 中的 `baseURL` 配置
2. 确认后端服务正常运行
3. 检查浏览器控制台的网络请求错误

### 页面空白

1. 检查 Nginx 配置是否正确
2. 查看浏览器控制台是否有 JavaScript 错误
3. 确认静态资源路径正确

## 相关链接

- [Vue 3 文档](https://cn.vuejs.org/)
- [Vite 文档](https://cn.vitejs.dev/)
- [Element Plus 文档](https://element-plus.org/zh-CN/)
- [后端服务 README](../AccessMgt_backend/README.md)
