# 部署配置说明

## 📋 配置总览

系统现在使用 **Nginx 反向代理** 统一处理所有请求，前端使用相对路径，可以在任何IP的服务器上部署。

## 🏗️ 架构

```
客户端浏览器
    ↓
Nginx (端口 80)
    ↓
    ├─→ / (根路径) → Frontend (内部端口 8082)
    ├─→ /api       → Backend (内部端口 8010)
    └─→ /label-studio → Label Studio (内部端口 8081)
```

## 🚀 部署步骤

### 1. 启动所有服务
```bash
docker-compose up -d --build
```

### 2. 访问应用
只需要访问服务器的 **80 端口**（HTTP默认端口）：
- 主应用：`http://your-server-ip/`
- API：`http://your-server-ip/api/`
- Label Studio：`http://your-server-ip/label-studio/`

**示例：**
- `http://192.168.1.100/`
- `http://10.4.34.108/`
- `http://example.com/` (如果配置了域名)

### 3. 检查服务状态
```bash
# 查看所有容器
docker-compose ps

# 查看 Nginx 日志
docker-compose logs nginx

# 查看后端日志
docker-compose logs backend
```

## 🔧 配置文件说明

### 1. `nginx/nginx.conf`
- 将 `/` 请求代理到前端服务
- 将 `/api` 请求代理到后端服务
- 设置文件上传大小限制为 100MB
- 配置超时时间适应 OCR 长时间处理

### 2. `docker-compose.yml`
- 添加了 `nginx` 服务作为入口
- Frontend 和 Backend 不再直接暴露端口（使用 `expose`）
- 所有流量通过 Nginx 统一管理

### 3. `backend/backend/settings.py`
- `ALLOWED_HOSTS = ['*']` 允许任何主机访问
- 生产环境建议改为具体域名：`ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']`

## ⚙️ 端口使用

| 服务 | 外部端口 | 内部端口 | 说明 |
|------|---------|---------|------|
| Nginx | 80 | 80 | 统一入口 |
| Backend | - | 8010 | 仅内部访问 |
| Frontend | - | 8082 | 仅内部访问 |
| Label Studio | - | 8081 | 通过 Nginx 访问 |
| PostgreSQL | 5432 | 5432 | 数据库 |
| Redis | 6379 | 6379 | 消息队列 |

## 🔒 生产环境建议

### 1. 安全配置
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.getenv('SECRET_KEY')  # 使用环境变量
```

### 2. HTTPS 配置
修改 `nginx/nginx.conf` 添加 SSL：
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... 其他配置
}

server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

### 3. 环境变量
创建 `.env` 文件管理敏感信息：
```env
SECRET_KEY=your-secret-key
POSTGRES_PASSWORD=secure-password
DEBUG=False
```

## 🐛 故障排查

### 问题1：无法访问页面
```bash
# 检查 Nginx 是否运行
docker-compose ps nginx

# 查看 Nginx 错误日志
docker-compose logs nginx --tail=50
```

### 问题2：API 请求失败
```bash
# 检查后端是否运行
docker-compose ps backend

# 查看后端日志
docker-compose logs backend --tail=50
```

### 问题3：502 Bad Gateway
- 检查 backend 服务是否正常运行
- 检查容器之间的网络连接
```bash
docker-compose exec nginx ping backend
```

## 📝 迁移到新服务器

1. 复制整个项目目录到新服务器
2. 确保 Docker 和 Docker Compose 已安装
3. 运行 `docker-compose up -d --build`
4. 完成！无需修改任何 IP 配置

## 🔄 更新配置后重启

```bash
# 重启 Nginx（配置更改后）
docker-compose restart nginx

# 重启后端（代码更改后）
docker-compose restart backend

# 重启所有服务
docker-compose restart
```
