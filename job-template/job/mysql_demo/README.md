# FastAPI MySQL Demo 模板

一个使用 FastAPI 直接连接 MySQL 数据库的完整示例。展示了如何通过 FastAPI 进行实时数据库操作，包括 CRUD 操作和自定义 SQL 查询。

## 目录结构

```
mysql_demo/
├── app.py                 # FastAPI 应用入口
├── requirements.txt       # Python 依赖
├── Dockerfile             # 镜像构建文件
├── build.sh               # 构建并推送镜像脚本
└── README.md
```

## 功能特性

- ✅ FastAPI 直接连接 MySQL 数据库
- ✅ SQLAlchemy ORM 进行数据库操作
- ✅ 完整的 CRUD 操作（创建、读取、更新、删除）
- ✅ 用户管理 API
- ✅ 数据库连接健康检查
- ✅ 错误处理和异常提示
- ✅ 环境变量配置

## 本地运行

### 1. 安装依赖

```bash
cd job-template/job/mysql_demo
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=testdb
```

### 3. 启动应用

```bash
python app.py
```

默认监听地址：<http://127.0.0.1:8080>

访问说明：

- 根路径 `http://127.0.0.1:8080/`：展示内置的用户管理页面（无需前端代码）
- API 状态 `http://127.0.0.1:8080/api/status`：返回 JSON 状态信息

## API 接口

### 健康检查

```bash
GET /api/health
```

### 用户管理

- **创建用户**
  ```bash
  POST /api/users
  Body: {"name": "张三", "email": "zhangsan@example.com"}
  ```

- **获取用户列表**
  ```bash
  GET /api/users?skip=0&limit=100
  ```

- **根据 ID 获取用户**
  ```bash
  GET /api/users/{user_id}
  ```

- **根据邮箱获取用户**
  ```bash
  GET /api/users/email/{email}
  ```

- **更新用户**
  ```bash
  PUT /api/users/{user_id}
  Body: {"name": "李四", "email": "lisi@example.com"}
  ```

- **删除用户**
  ```bash
  DELETE /api/users/{user_id}
  ```

- **获取用户总数**
  ```bash
  GET /api/users/count
  ```

## 构建镜像

```bash
cd job-template/job/mysql_demo
chmod +x build.sh
./build.sh
```

镜像地址：`47.116.204.159:8089/cube/mysql-demo:20251119`

## 部署到 Cube Studio

### 方式 1：使用 deploy-service 模板

推荐使用 **deploy-service** 模板，镜像及参数示例：

```json
{
    "模型信息": {
        "--project_name": {
            "type": "str",
            "item_type": "str",
            "label": "项目组名称",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "public",
            "placeholder": "",
            "describe": "项目组名称",
            "editable": 1
        },
        "--label": {
            "type": "str",
            "item_type": "str",
            "label": "中文描述",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "FastAPI MySQL Demo",
            "placeholder": "",
            "describe": "推理服务描述",
            "editable": 1
        },
        "--model_name": {
            "type": "str",
            "item_type": "str",
            "label": "模型名",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "mysql-demo",
            "placeholder": "",
            "describe": "模型名",
            "editable": 1
        },
        "--model_version": {
            "type": "str",
            "item_type": "str",
            "label": "模型版本号",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "v1.0.0",
            "placeholder": "",
            "describe": "模型版本号",
            "editable": 1
        }
    },
    "部署信息": {
        "--service_type": {
            "type": "str",
            "item_type": "str",
            "label": "服务类型",
            "require": 1,
            "choice": [
                "serving",
                "ml-server",
                "tfserving",
                "torch-server",
                "onnxruntime",
                "triton-server",
                "vllm"
            ],
            "range": "",
            "default": "serving",
            "placeholder": "",
            "describe": "推理服务类型",
            "editable": 1
        },
        "--images": {
            "type": "str",
            "item_type": "str",
            "label": "镜像",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "47.116.204.159:8089/cube/mysql-demo:20251119",
            "placeholder": "",
            "describe": "推理服务镜像",
            "editable": 1
        },
        "--working_dir": {
            "type": "str",
            "item_type": "str",
            "label": "工作目录",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "/app",
            "placeholder": "",
            "describe": "推理容器工作目录",
            "editable": 1
        },
        "--command": {
            "type": "str",
            "item_type": "str",
            "label": "启动命令",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "python app.py",
            "placeholder": "",
            "describe": "推理容器启动命令",
            "editable": 1
        },
        "--env": {
            "type": "text",
            "item_type": "str",
            "label": "环境变量",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "MYSQL_HOST=mysql-service.infra\nMYSQL_PORT=3306\nMYSQL_USER=root\nMYSQL_PASSWORD=rootpassword\nMYSQL_DATABASE=testdb\nPORT=8080\nHOST=http://192.168.126.150",
            "placeholder": "",
            "describe": "每行一个 KEY=VALUE，例如 MYSQL_HOST=mysql-service.infra",
            "editable": 1
        },
        "--ports": {
            "type": "str",
            "item_type": "str",
            "label": "暴露端口",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "8080",
            "placeholder": "",
            "describe": "例如 8080",
            "editable": 1
        },
        "--replicas": {
            "type": "str",
            "item_type": "str",
            "label": "Pod 副本数",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "1",
            "placeholder": "",
            "describe": "副本数",
            "editable": 1
        },
        "--resource_memory": {
            "type": "str",
            "item_type": "str",
            "label": "内存",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "1G",
            "placeholder": "",
            "describe": "每个 Pod 占用内存",
            "editable": 1
        },
        "--resource_cpu": {
            "type": "str",
            "item_type": "str",
            "label": "CPU",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "1",
            "placeholder": "",
            "describe": "每个 Pod 占用 CPU",
            "editable": 1
        },
        "--resource_gpu": {
            "type": "str",
            "item_type": "str",
            "label": "GPU",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "0",
            "placeholder": "",
            "describe": "每个 Pod 占用 GPU",
            "editable": 1
        },
        "--host": {
            "type": "str",
            "item_type": "str",
            "label": "域名",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "",
            "placeholder": "",
            "describe": "部署域名，留空自动生成",
            "editable": 1
        },
        "--health": {
            "type": "str",
            "item_type": "str",
            "label": "健康检查",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "8080:/api/health",
            "placeholder": "",
            "describe": "格式：端口:URL 例如 8080:/api/health",
            "editable": 1
        }
    }
}
```

部署成功后即可通过服务暴露的域名访问 API 接口。

## 环境变量说明

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MYSQL_HOST` | mysql-service.infra | MySQL 服务器地址 |
| `MYSQL_PORT` | 3306 | MySQL 端口 |
| `MYSQL_USER` | root | MySQL 用户名 |
| `MYSQL_PASSWORD` | rootpassword | MySQL 密码 |
| `MYSQL_DATABASE` | testdb | 数据库名称 |
| `PORT` | 8080 | 应用监听端口 |
| `HOST` | 0.0.0.0 | 应用绑定地址 |

## 使用示例

### 访问地址说明

部署成功后，可以在 Cube Studio 的"推理服务"页面查看服务的访问地址：

1. **IP:Port 方式**（推荐，无需认证）
   - 格式：`http://<ExternalIP>:<Port>`
   - 例如：`http://192.168.126.150:30080`
   - 这种方式直接访问服务，不需要认证

2. **域名方式**（可能需要认证）
   - 格式：`http://<自动生成的域名>`
   - 如果遇到 401 错误，说明域名配置了认证，请使用 IP:Port 方式

### 服务状态（JSON）

```bash
curl "http://192.168.126.150:30080/api/status"
```

### 创建用户

```bash
# 使用 IP:Port 方式（推荐）
curl -X POST "http://192.168.126.150:30080/api/users" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"张三\", \"email\": \"zhangsan@example.com\"}"

# 或者使用域名方式（可能需要在 Cube Studio 中登录）
curl -X POST "http://your-domain/api/users" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"张三\", \"email\": \"zhangsan@example.com\"}"
```

### 获取用户列表

```bash
curl "http://192.168.126.150:30080/api/users"
```

### 获取单个用户

```bash
curl "http://192.168.126.150:30080/api/users/1"
```

### 更新用户

```bash
curl -X PUT "http://192.168.126.150:30080/api/users/1" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"李四\", \"email\": \"lisi@example.com\"}"
```

### 删除用户

```bash
curl -X DELETE "http://192.168.126.150:30080/api/users/1"
```

### 健康检查

```bash
curl "http://192.168.126.150:30080/api/health"
```

### 在浏览器中访问

也可以直接在浏览器中访问：
- 根路径：`http://<IP>:<Port>/`
- API 文档：`http://<IP>:<Port>/docs`（FastAPI 自动生成的 Swagger 文档）
- 健康检查：`http://<IP>:<Port>/api/health`

## 注意事项

1. **数据库连接**：确保 MySQL 数据库已创建，并且应用有权限访问
2. **表结构**：应用首次启动时会自动创建 `users` 表
3. **连接池**：使用 SQLAlchemy 连接池管理数据库连接，支持自动重连
4. **生产环境**：建议使用 gunicorn + uvicorn workers 部署（Dockerfile 已配置）
5. **401 错误处理**：
   - 如果通过域名访问遇到 401 错误，说明域名配置了认证
   - 解决方法：使用 IP:Port 方式直接访问（在推理服务页面查看 IP 和端口）
   - IP:Port 方式不需要认证，可以直接访问 API
6. **查看访问地址**：在 Cube Studio 的"推理服务"页面，点击服务名称，可以看到 IP 和端口信息

## 与 DataX 的区别

- **FastAPI（本模板）**：用于实时业务，API 直接连接数据库进行实时查询和写入
- **DataX**：用于批量数据处理，数据迁移，ETL 任务，适合大数据量离线处理

两者互补使用，不是替代关系。
