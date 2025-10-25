# OCR 项目部署指南

## 📋 改进说明

本项目已实现以下改进：

### 1. ⚡ Docker 构建优化 - MinerU 模型缓存
- 添加模型预下载脚本 `backend/download_models.py`
- 利用 Docker 层缓存机制，避免每次构建都重新下载模型
- 首次构建后，只要 requirements.txt 不变，模型层会被缓存

### 2. 🔄 自动导入 Label Studio
- 新增 API 端点：`POST /api/documents/auto-import-to-label-studio/`
- 支持批量导入多个文档的 OCR 结果到 Label Studio
- 不再需要手动下载和上传 JSON 文件

### 3. 🌐 Nginx 反向代理统一管理
- 使用 Nginx 作为统一入口，管理所有服务
- 前端、后端、Label Studio 都通过同一个域名/IP 访问
- 无需在代码中硬编码 IP 地址
- 访问方式：
  - 前端：`http://your-server/`
  - 后端 API：`http://your-server/api/`
  - Label Studio：`http://your-server/label-studio/`

### 4. 🚀 GPU 加速支持
- 支持 NVIDIA GPU 加速 OCR 识别
- 提供独立的 GPU 配置文件 `docker-compose.gpu.yml`
- 自动检测 GPU 可用性，无 GPU 时自动降级到 CPU

---

## 🚀 快速开始

### 前置要求

1. **Docker** 和 **Docker Compose** 已安装
2. （可选）如需 GPU 加速，需安装 [NVIDIA Docker Runtime](https://github.com/NVIDIA/nvidia-docker)

### 部署步骤

#### 1. 克隆项目并配置环境变量

```bash
cd OCR_v1
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下内容：

```bash
# Label Studio API Token（在 Label Studio 中生成）
LABEL_STUDIO_API_TOKEN=your_token_here

# Label Studio 默认项目 ID（可选）
LABEL_STUDIO_PROJECT_ID=1
```

#### 2. （可选）启用 GPU 加速

如果您有 NVIDIA GPU 并希望加速 OCR 处理：

1. 验证 GPU 可用：
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

2. 编辑 `docker-compose.yml`，在 `celery` 服务中找到 GPU 配置部分，取消注释：
```yaml
celery:
  # ... 其他配置 ...
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all  # 使用所有GPU，或指定数量如 count: 1
            capabilities: [gpu]
```

#### 3. 一键启动所有服务

```bash
docker-compose up -d --build
```

就这么简单！所有服务（数据库、Redis、后端、前端、Celery、Label Studio、Nginx）都会自动启动。

#### 4. 访问服务

启动完成后，通过以下地址访问：

- **前端界面**：http://your-server-ip/ 或 http://localhost/
- **后端 API**：http://your-server-ip/api/ 或 http://localhost/api/
- **Label Studio**：http://your-server-ip/label-studio/ 或 http://localhost/label-studio/
- **健康检查**：http://your-server-ip/health

> 💡 **提示**：首次启动会下载 MinerU 模型，可能需要几分钟时间。

---

## 🔧 配置说明

### Nginx 反向代理

Nginx 配置文件位于 `nginx/nginx.conf`，已预配置：

- 前端：`/` → `frontend:8082`
- 后端：`/api/` → `backend:8010/api/`
- Label Studio：`/label-studio/` → `label-studio:8081/`
- 静态文件：`/data/` → 数据目录（用于 Label Studio 访问图片）

**自定义域名：**

编辑 `nginx/nginx.conf`，修改 `server_name`：

```nginx
server {
    listen 80;
    server_name ocr.example.com;  # 改为你的域名
    # ...
}
```

**HTTPS 配置（推荐）：**

```nginx
server {
    listen 443 ssl http2;
    server_name ocr.example.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... 其他配置保持不变
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name ocr.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Label Studio 配置

1. 首次访问 Label Studio：`http://your-server/label-studio/`
2. 创建账号并登录
3. 生成 API Token：
   - 点击右上角头像 → Account & Settings
   - 找到 Access Token → 点击 Create Token
   - 复制 Token 并添加到 `.env` 文件：
     ```bash
     LABEL_STUDIO_API_TOKEN=your_token_here
     ```
4. 创建项目并记录项目 ID（URL 中的数字）
5. 更新 `.env`：
   ```bash
   LABEL_STUDIO_PROJECT_ID=1
   ```

6. 重启服务以应用配置：
   ```bash
   docker-compose restart backend celery
   ```

---

## 📝 使用工作流

### 方案一：自动导入（推荐）

1. **上传 PDF**：访问前端 → 上传一个或多个 PDF 文档
2. **等待处理**：文档状态从 `pending` → `processing` → `processed`
3. **自动导入 Label Studio**：
   - 调用 API（或在前端添加按钮）：
   ```bash
   curl -X POST http://your-server/api/documents/auto-import-to-label-studio/ \
     -H "Content-Type: application/json" \
     -d '{
       "doc_ids": [1, 2, 3],
       "project_id": "1"
     }'
   ```
4. **校对标注**：访问 Label Studio → 打开项目 → 校对 OCR 结果
5. **导出校对结果**：Label Studio → Export → JSON
6. **上传校对结果**：前端 → 上传校对后的 JSON
7. **生成 RAG 文件**：前端 → 下载 RAGFlow 格式文件

### 方案二：手动导入（向后兼容）

1. **下载原始 JSON**：文档列表 → 点击"下载原始 JSON"
2. **导入 Label Studio**：Label Studio → Import → 上传 JSON
3. 后续步骤同方案一的第 4-7 步

---

## 🐛 调试模式

如需直接访问各服务端口（不通过 Nginx），可以取消 docker-compose.yml 中的端口注释：

```yaml
backend:
  ports:
    - "8010:8010"  # 取消此注释

frontend:
  ports:
    - "8082:8082"  # 取消此注释

label-studio:
  ports:
    - "8081:8081"  # 取消此注释
```

然后重启服务：
```bash
docker-compose up -d
```

---

## 📊 监控和日志

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f nginx
```

### Nginx 访问日志
```bash
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

---

## 🔄 更新和维护

### 重新构建镜像
```bash
docker-compose up -d --build
```

### 清理旧数据
```bash
# 停止所有服务
docker-compose down

# 清理数据库和缓存（谨慎操作！）
docker volume rm ocr_v1_postgres_data

# 重新启动
docker-compose up -d
```

### 数据库迁移
```bash
# 创建新的迁移
docker-compose exec backend python manage.py makemigrations

# 应用迁移
docker-compose exec backend python manage.py migrate
```

---

## ⚠️ 常见问题

### 1. 模型下载失败或速度慢
在 `.env` 中设置国内镜像源：
```bash
MINERU_MODEL_SOURCE=modelscope
```

### 2. GPU 不可用
检查 NVIDIA Docker Runtime 安装：
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### 3. Label Studio 无法访问图片
确保 Nginx 配置中的 `/data/` 路径正确挂载。

### 4. 前端无法连接后端
检查浏览器控制台，确认 API 请求地址是 `/api/` 而不是完整 URL。

---

## 📦 生产环境建议

1. **使用域名和 HTTPS**
2. **配置防火墙**：只开放 80/443 端口
3. **备份数据库**：定期备份 PostgreSQL 数据
4. **日志轮转**：配置 Nginx 和应用日志轮转
5. **资源限制**：在 docker-compose.yml 中添加 CPU/内存限制
6. **监控告警**：集成 Prometheus + Grafana 监控

---

## 📞 技术支持

如有问题，请查看：
- 项目日志：`docker-compose logs`
- GitHub Issues
- 项目文档：`ReadMe.md`
