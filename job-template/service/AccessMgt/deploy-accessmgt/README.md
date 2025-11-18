# deploy-accessmgt 模板

用于在 Cube-Studio 中一键部署 AccessMgt 后端和两个前端服务。

镜像：`47.106.243.150:8089/cube/deploy-accessmgt:20250101`

## 工作原理

1. **自动部署三个服务**：后端 + 前端1 + 前端2
2. **自动创建 VirtualService**：将 `/api/accessmgt` 路径路由到后端服务
3. **前端使用相对路径**：前端通过 `/api/accessmgt` 访问后端，无需知道后端具体地址

## 启动参数

```json
{
    "项目信息": {
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
        }
    },
    "后端服务": {
        "--backend_service_name": {
            "type": "str",
            "item_type": "str",
            "label": "后端服务名",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "accessmgt-backend",
            "placeholder": "",
            "describe": "后端服务名",
            "editable": 1
        },
        "--backend_model_version": {
            "type": "str",
            "item_type": "str",
            "label": "后端版本号",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "v2025.01.01.1",
            "placeholder": "",
            "describe": "后端版本号",
            "editable": 1
        },
        "--backend_images": {
            "type": "str",
            "item_type": "str",
            "label": "后端镜像",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "47.106.243.150:8089/cube/accessmgt-backend:1.0.0",
            "placeholder": "",
            "describe": "后端镜像地址",
            "editable": 1
        },
        "--backend_resource_memory": {
            "type": "str",
            "item_type": "str",
            "label": "后端内存",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "2G",
            "placeholder": "",
            "describe": "后端服务内存",
            "editable": 1
        },
        "--backend_resource_cpu": {
            "type": "str",
            "item_type": "str",
            "label": "后端CPU",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "2",
            "placeholder": "",
            "describe": "后端服务CPU",
            "editable": 1
        },
        "--backend_ports": {
            "type": "str",
            "item_type": "str",
            "label": "后端端口",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "10086",
            "placeholder": "",
            "describe": "后端服务端口",
            "editable": 1
        }
    },
    "前端1服务(PGJG)": {
        "--frontend1_service_name": {
            "type": "str",
            "item_type": "str",
            "label": "前端1服务名",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "accessmgt-fe-pgjg",
            "placeholder": "",
            "describe": "前端1服务名",
            "editable": 1
        },
        "--frontend1_images": {
            "type": "str",
            "item_type": "str",
            "label": "前端1镜像",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "47.106.243.150:8089/cube/accessmgt-fe-pgjg:1.0.0",
            "placeholder": "",
            "describe": "前端1镜像地址",
            "editable": 1
        },
        "--frontend1_resource_memory": {
            "type": "str",
            "item_type": "str",
            "label": "前端1内存",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "512Mi",
            "placeholder": "",
            "describe": "前端1服务内存",
            "editable": 1
        },
        "--frontend1_resource_cpu": {
            "type": "str",
            "item_type": "str",
            "label": "前端1CPU",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "0.5",
            "placeholder": "",
            "describe": "前端1服务CPU",
            "editable": 1
        }
    },
    "前端2服务(ZBDJ)": {
        "--frontend2_service_name": {
            "type": "str",
            "item_type": "str",
            "label": "前端2服务名",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "accessmgt-fe-zbdj",
            "placeholder": "",
            "describe": "前端2服务名",
            "editable": 1
        },
        "--frontend2_images": {
            "type": "str",
            "item_type": "str",
            "label": "前端2镜像",
            "require": 1,
            "choice": [],
            "range": "",
            "default": "47.106.243.150:8089/cube/accessmgt-fe-zbdj:1.0.0",
            "placeholder": "",
            "describe": "前端2镜像地址",
            "editable": 1
        },
        "--frontend2_resource_memory": {
            "type": "str",
            "item_type": "str",
            "label": "前端2内存",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "512Mi",
            "placeholder": "",
            "describe": "前端2服务内存",
            "editable": 1
        },
        "--frontend2_resource_cpu": {
            "type": "str",
            "item_type": "str",
            "label": "前端2CPU",
            "require": 0,
            "choice": [],
            "range": "",
            "default": "0.5",
            "placeholder": "",
            "describe": "前端2服务CPU",
            "editable": 1
        }
    }
}
```

## 使用方法

### 1. 准备数据库

```bash
# 端口转发 MySQL
kubectl port-forward -n infra svc/mysql-service 3306:3306

# 导入 AccessDB（在另一个终端）
mysql -h127.0.0.1 -P3306 -uroot -padmin < job-template/service/AccessMgt/AccessMgtServer/accessdb.sql
```

### 2. 构建并推送镜像

```bash
cd job-template/service/AccessMgt
chmod +x build-all.sh
./build-all.sh
```

### 3. 在 Cube-Studio 中注册模板

1. 登录 Cube-Studio 平台
2. 进入「训练」→「任务模板」→「添加」
3. 填写模板信息：
   - 模板名称：`deploy-accessmgt`
   - 镜像：`47.106.243.150:8089/cube/deploy-accessmgt:20250101`
   - 启动命令：`python3 launcher.py`
   - 启动参数：复制上面的 JSON 配置

### 4. 运行模板任务部署服务

1. 在 Cube-Studio 中创建新任务
2. 选择 `deploy-accessmgt` 模板
3. 填写参数（镜像地址等）
4. 提交任务

### 5. 查看部署结果

部署完成后：
- 在「模型中心」→「部署服务」页面可以看到三个服务
- 模板会自动创建 VirtualService，将 `/api/accessmgt` 路由到后端
- 前端通过相对路径 `/api/accessmgt` 访问后端

## 访问方式

- **前端1 (PGJG)**：通过前端1服务的访问地址访问
- **前端2 (ZBDJ)**：通过前端2服务的访问地址访问
- **后端API**：通过 `/api/accessmgt/...` 路径访问（由 VirtualService 自动路由）

前端会自动通过 `/api/accessmgt` 调用后端 API，无需手动配置。

## 注意事项

1. **VirtualService 自动创建**：部署模板会在部署后端服务后自动创建 VirtualService
2. **如果自动创建失败**：可以手动创建，参考下面的 YAML
3. **前端配置**：前端已配置为使用相对路径 `/api/accessmgt`，无需修改

## 手动创建 VirtualService（备用方案）

如果自动创建失败，可以手动执行：

```bash
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: accessmgt-api-route
  namespace: service
spec:
  gateways:
  - kubeflow/kubeflow-gateway
  hosts:
  - "*"
  http:
  - match:
    - uri:
        prefix: /api/accessmgt
    rewrite:
      uri: /
    route:
    - destination:
        host: accessmgt-backend.service.svc.cluster.local
        port:
          number: 10086
EOF
```
