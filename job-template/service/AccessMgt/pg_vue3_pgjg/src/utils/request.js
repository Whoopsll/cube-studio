// src/utils/request.js
import axios from 'axios';

const { baseURL, timeout } = window.appConfig || {
  baseURL: 'http://127.0.0.1:10086', // 兜底默认地址
  timeout: 5000
};
// 创建 axios 实例
const service = axios.create({
  // baseURL: 'http://192.168.3.25:10086', // 基础URL，根据环境变量配置
  baseURL: baseURL,
  timeout: timeout, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么，例如添加 token
    // if (store.getters.token) {
    //   config.headers['X-Token'] = getToken()
    // }
    return config;
  },
  error => {
    // 对请求错误做些什么
    console.log(error); // for debug
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对于需要访问响应头的请求，返回完整响应对象
    if (response.config.responseType === 'blob') {
      return response;
    }
    
    const res = response.data;
    // 根据返回的状态码进行一些操作，例如登录过期、错误提示等
    // if (res.code !== 1) {
      // 50008: 验证失败; 50012: 其他客户端登录; 50014: Token 过期;
      // if (res.code === 50008 || res.code === 50012 || res.code === 50014) {
      //   // 重新登录
      // }
      // return Promise.reject(new Error(res.message || 'Error'));
    // } else {
      // return res;
    // }
    return res;
  },
  error => {
    console.log('err' + error); // for debug
    return Promise.reject(error);
  }
);

export default service;
