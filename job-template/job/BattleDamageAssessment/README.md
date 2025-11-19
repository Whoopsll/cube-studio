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

镜像地址：`ccr.ccs.tencentyun.com/cube-studio/battle-damage-assessment:20250101`

## 部署到 Cube Studio

推荐使用 **deploy-service** 模板，镜像及参数示例：

```
{
  "服务配置": {
    "--project_name": "public",
    "--label": "BattleDamageAssessment",
    "--model_name": "battle-damage-assessment",
    "--model_version": "v1.0.0",
    "--service_type": "serving",
    "--images": "ccr.ccs.tencentyun.com/cube-studio/battle-damage-assessment:20250101",
    "--working_dir": "/app",
    "--command": "python app.py",
    "--env": "PORT=8080",
    "--ports": "8080",
    "--replicas": "1",
    "--resource_memory": "1G",
    "--resource_cpu": "1",
    "--resource_gpu": "0",
    "--volume_mount": ""
  }
}
```

部署成功后即可通过服务暴露的域名访问 Web 页面。

## 注意事项

1. 应用使用预置图片进行演示，不会真正执行模型推理。
2. 如需替换示例图片，可将新的图片放置在 `scenes/`、`unidentified/`、`identified/` 目录下，并保持相同的文件名（例如 `1.png`、`2.png`）。
3. 如果在容器内运行，需要保证这些目录在镜像构建阶段已复制进去（Dockerfile 已默认处理）。

