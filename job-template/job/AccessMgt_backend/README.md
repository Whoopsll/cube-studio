# BattleDamageAssessment 模板

## 构建镜像

```bash
cd job-template/job/AccessMgt_backend
chmod +x build.sh
./build.sh
```

镜像地址：`47.116.204.159:8089/cube/accessmgt_backend:20251121`

## 部署到 Cube Studio

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
      "default": "AccessMgt_backend",
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
      "default": "AccessMgt_backend",
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
      "default": "v2025.11.21",
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
      "default": "47.116.204.159:8089/cube/accessmgt_backend:20251121",
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
      "default": "PORT=8080\nHOST=http://192.168.126.150",
      "placeholder": "",
      "describe": "每行一个 KEY=VALUE，例如 PORT=8080\nHOST=http://192.168.126.150",
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
    "--volume_mount": {
      "type": "str",
      "item_type": "str",
      "label": "挂载",
      "require": 0,
      "choice": [],
      "range": "",
      "default": "",
      "placeholder": "",
      "describe": "格式：pvc_name(pvc):/path",
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
    "--metrics": {
      "type": "str",
      "item_type": "str",
      "label": "指标采集接口",
      "require": 0,
      "choice": [],
      "range": "",
      "default": "",
      "placeholder": "",
      "describe": "格式：端口:URL 例如 8080:/metrics",
      "editable": 1
    },
    "--health": {
      "type": "str",
      "item_type": "str",
      "label": "健康检查",
      "require": 0,
      "choice": [],
      "range": "",
      "default": "",
      "placeholder": "",
      "describe": "格式：端口:URL 例如 8080:/health",
      "editable": 1
    }
  }
}
```

部署成功后即可通过服务暴露的域名访问 Web 页面。

## 注意事项

1. 应用使用预置图片进行演示，不会真正执行模型推理。
2. 如需替换示例图片，可将新的图片放置在 `scenes/`、`unidentified/`、`identified/` 目录下，并保持相同的文件名（例如 `1.png`、`2.png`）。
3. 如果在容器内运行，需要保证这些目录在镜像构建阶段已复制进去（Dockerfile 已默认处理）。


