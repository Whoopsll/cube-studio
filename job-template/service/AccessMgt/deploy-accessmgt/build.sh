#!/bin/bash

set -ex

# 构建 deploy-accessmgt 镜像
docker build --network=host -t 47.106.243.150:8089/cube/deploy-accessmgt:20250101 -f service/AccessMgt/deploy-accessmgt/Dockerfile .
docker push 47.106.243.150:8089/cube/deploy-accessmgt:20250101

# docker buildx build --platform linux/amd64,linux/arm64 -t ccr.ccs.tencentyun.com/cube-studio/deploy-accessmgt:20250101 -f service/AccessMgt/deploy-accessmgt/Dockerfile . --push

