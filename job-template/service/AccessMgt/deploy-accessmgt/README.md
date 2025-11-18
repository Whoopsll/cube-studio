# deploy-accessmgt 模板

用于在 Cube-Studio 中一键部署 AccessMgt 后端和两个前端服务。

镜像：`ccr.ccs.tencentyun.com/cube-studio/deploy-accessmgt:20250101`

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
            "default": "ccr.ccs.tencentyun.com/cube-studio/accessmgt-backend:1.0.0",
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
            "default": "ccr.ccs.tencentyun.com/cube-studio/accessmgt-fe-pgjg:1.0.0",
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
            "default": "ccr.ccs.tencentyun.com/cube-studio/accessmgt-fe-zbdj:1.0.0",
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

1. 先构建并推送三个镜像（后端 + 两个前端）
2. 在 Cube-Studio 中注册这个模板
3. 运行模板任务，填写参数
4. 模板会自动创建三个 InferenceService 并部署

部署完成后，服务会出现在「模型中心」→「部署服务」页面中。

