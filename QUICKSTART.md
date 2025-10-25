# OCR 项目快速开始指南

## 📦 一键启动

### 步骤1：配置环境变量

```bash
cd OCR_v1
cp .env.example .env
```

编辑 `.env` 文件，必须配置：
```bash
LABEL_STUDIO_API_TOKEN=your_token_here
LABEL_STUDIO_PROJECT_ID=1
```

### 步骤2：启动所有服务

```bash
docker-compose up -d --build
```

### 步骤3：访问服务

- 前端：http://localhost/
- API：http://localhost/api/
- Label Studio：http://localhost/label-studio/

---

## 🚀 启用 GPU 加速（可选）

### 前提条件

安装 NVIDIA Docker Runtime 并验证：
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### 启用步骤

1. 编辑 `docker-compose.yml`
2. 找到 `celery` 服务的 GPU 配置部分（约第 97-102 行）
3. 取消这些行的注释：
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: all
             capabilities: [gpu]
   ```
4. 保存并重启：
   ```bash
   docker-compose up -d --build
   ```

---

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f celery

# 重启服务
docker-compose restart

# 停止所有服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

---

## 📝 Label Studio 配置

首次使用需要配置 Label Studio：

1. 访问：http://localhost/label-studio/
2. 注册账号并登录
3. 点击右上角头像 → Account & Settings
4. 找到 Access Token → Create Token
5. 复制 Token 并更新 `.env`：
   ```bash
   LABEL_STUDIO_API_TOKEN=刚才复制的token
   ```
6. 创建项目并记录项目 ID（URL中的数字）
7. 更新 `.env`：
   ```bash
   LABEL_STUDIO_PROJECT_ID=1
   ```
8. 重启 backend 和 celery：
   ```bash
   docker-compose restart backend celery
   ```

---

## ✅ 验证安装

### 健康检查
```bash
curl http://localhost/health
# 应返回: healthy
```

### 测试上传
1. 访问前端：http://localhost/
2. 上传一个 PDF 文件
3. 等待状态变为 `processed`
4. 查看 celery 日志确认处理：
   ```bash
   docker-compose logs -f celery
   ```

---

## 🆘 常见问题

### 1. 端口被占用
如果 80 端口被占用，编辑 `docker-compose.yml` 中 nginx 的端口映射：
```yaml
nginx:
  ports:
    - "8080:80"  # 改为 8080 或其他可用端口
```

### 2. 模型下载慢
首次启动会下载模型，国内用户已默认使用 modelscope 镜像。
查看下载进度：
```bash
docker-compose logs -f celery
```

### 3. GPU 不可用
确保：
- 已安装 NVIDIA Docker Runtime
- docker-compose.yml 中已取消 GPU 配置的注释
- 运行验证命令成功

---

## 📚 更多信息

- 详细部署文档：`DEPLOYMENT.md`
- 完整 README：`README_NEW.md`
- 环境变量说明：`.env.example`
