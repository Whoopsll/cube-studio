# BattleDamageAssessment 模板

一个用于演示目标毁伤评估流程的轻量级 Flask Web 应用。前端页面可以选择不同场景、上传毁伤后的图片，并展示场景图、毁伤图、识别结果图及文本说明。本项目主要用于演示，在后台不会真正执行模型推理，而是从预置的 `scenes/`、`unidentified/`、`identified/` 目录中读取示例图片返回。

## 目录结构

```
BattleDamageAssessment/
├── app.py                 # Flask 应用入口
├── templates/index.html   # Web 页面
├── scenes/                # 场景图片（毁伤前）
├── unidentified/          # 毁伤图片（上传后效果）
├── identified/            # 识别结果
├── requirements.txt       # Python 依赖
├── Dockerfile             # 镜像构建文件
├── build.sh               # 构建并推送镜像脚本
└── README.md
```

## 本地运行

```bash
cd job-template/job/BattleDamageAssessment
python -m venv venv && source venv/bin/activate  # Windows 使用 venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

默认监听地址：<http://127.0.0.1:8080>

环境变量：

| 变量名      | 默认值  | 说明                |
|-------------|---------|---------------------|
| `HOST`      | 0.0.0.0 | 服务绑定地址        |
| `PORT`      | 8080    | 服务端口            |
| `SERVER_IP` | 0.0.0.0 | 与 HOST 同义（兼容）|
| `SERVER_PORT` | 8080  | 与 PORT 同义（兼容）|
| `FLASK_DEBUG` | 0     | 设置为 1 可开启调试 |

## 构建镜像

```bash
cd job-template/job/BattleDamageAssessment
chmod +x build.sh
./build.sh
```

镜像地址：`47.116.204.159:8089/cube/battle-damage-assessment:20251119`

## 部署到 Cube Studio

推荐使用 **deploy-service** 模板，镜像及参数示例：

```
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
      "default": "BattleDamageAssessment",
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
      "default": "battle-damage-assessment",
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
    },
    "--model_path": {
      "type": "str",
      "item_type": "str",
      "label": "模型地址",
      "require": 0,
      "choice": [],
      "range": "",
      "default": "",
      "placeholder": "",
      "describe": "模型地址（可留空）",
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
      "default": "47.116.204.159:8089/cube/battle-damage-assessment:20251119",
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


