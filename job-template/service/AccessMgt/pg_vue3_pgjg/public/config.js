; // 接口配置（打包后可直接编辑此文件修改地址）
// 使用相对路径，通过 Istio VirtualService 路由到后端服务
// 部署模板会自动创建 /api/accessmgt 路径的路由
window.appConfig = {
  baseURL: '/api/accessmgt',  // 相对路径，指向后端 API
  timeout: 5000, // 请求超时时间（毫秒）
};


