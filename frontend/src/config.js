// 从环境变量中读取API基础URL
// 使用 Nginx 反向代理时，使用相对路径 '/api'
// 这样前端可以通过同一个域名访问后端，无需配置具体IP
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api';

export default API_BASE_URL;
