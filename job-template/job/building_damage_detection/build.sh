#!/bin/bash

set -ex

# 进入脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 镜像名称和标签（可以根据需要修改）
IMAGE_NAME=47.116.204.159:8089/cube/building-damage-detection:20251122

# 构建 Docker 镜像
docker build --network=host -t "$IMAGE_NAME" -f Dockerfile .

# 推送镜像到仓库
docker push "$IMAGE_NAME"

# 如果需要构建多平台镜像（amd64 和 arm64），可以使用下面的命令
# docker buildx build --platform linux/amd64,linux/arm64 -t "$IMAGE_NAME" -f Dockerfile . --push

