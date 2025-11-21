#!/bin/bash

set -ex

# 进入脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

IMAGE_NAME=47.116.204.159:8089/cube/access-mgt-server:20251119

docker build --network=host -t "$IMAGE_NAME" -f Dockerfile .
docker push "$IMAGE_NAME"

# docker buildx build --platform linux/amd64,linux/arm64 -t "$IMAGE_NAME" -f Dockerfile . --push

