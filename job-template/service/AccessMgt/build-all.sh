#!/bin/bash

set -ex

# 构建后端镜像
echo "构建后端镜像..."
cd AccessMgtServer
docker build -t ccr.ccs.tencentyun.com/cube-studio/accessmgt-backend:1.0.0 .
docker push ccr.ccs.tencentyun.com/cube-studio/accessmgt-backend:1.0.0
cd ..

# 构建前端1镜像
echo "构建前端1镜像 (pg_vue3_pgjg)..."
cd pg_vue3_pgjg
docker build -t ccr.ccs.tencentyun.com/cube-studio/accessmgt-fe-pgjg:1.0.0 .
docker push ccr.ccs.tencentyun.com/cube-studio/accessmgt-fe-pgjg:1.0.0
cd ..

# 构建前端2镜像
echo "构建前端2镜像 (pg_vue3_zbdj)..."
cd pg_vue3_zbdj
docker build -t ccr.ccs.tencentyun.com/cube-studio/accessmgt-fe-zbdj:1.0.0 .
docker push ccr.ccs.tencentyun.com/cube-studio/accessmgt-fe-zbdj:1.0.0
cd ..

# 构建部署模板镜像
echo "构建部署模板镜像..."
cd deploy-accessmgt
docker build -t ccr.ccs.tencentyun.com/cube-studio/deploy-accessmgt:20250101 -f Dockerfile ../../..
docker push ccr.ccs.tencentyun.com/cube-studio/deploy-accessmgt:20250101
cd ..

echo "所有镜像构建完成！"

