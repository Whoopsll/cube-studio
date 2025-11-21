#!/bin/sh

# 从环境变量获取 API 地址，如果没有设置则使用默认值
API_BASE_URL=${API_BASE_URL:-http://127.0.0.1:10086}
API_TIMEOUT=${API_TIMEOUT:-5000}

# 生成 config.js 文件
cat > /usr/share/nginx/html/config.js <<EOF
; // 接口配置（运行时动态生成）
window.appConfig = {
  baseURL: '${API_BASE_URL}',
  timeout: ${API_TIMEOUT},
};
EOF

echo "API Base URL configured: ${API_BASE_URL}"
echo "API Timeout configured: ${API_TIMEOUT}ms"

# 启动 Nginx
exec nginx -g 'daemon off;'

