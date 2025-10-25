# OCR-RAG 文档处理流水线

该系统通过 Docker Compose 进行容器化编排，集成了后端 API、异步任务处理、前端界面以及第三方标注工具 Label Studio。

## ✨ 最新改进 (2025-10)

### 🚀 核心优化

1. **Docker 构建优化**：利用层缓存机制，预下载 MinerU 模型，大幅加快后续构建速度
2. **自动导入 Label Studio**：支持批量自动导入 OCR 结果，无需手动下载上传
3. **Nginx 反向代理**：统一入口管理所有服务，无需在代码中硬编码 IP 地址
4. **GPU 加速支持**：支持 NVIDIA GPU 加速 OCR 识别，提升处理速度

## 核心特性

* **PDF 上传**: 通过 Web 界面上传 PDF 文档进行处理。
* **自动化 OCR**: 使用 `mineru` 工具作为核心 OCR 引擎，在后台异步处理 PDF。
* **GPU 加速**: 支持 NVIDIA GPU 加速，显著提升识别速度。
* **数据持久化**: 所有文档信息、状态和处理结果都存储在 PostgreSQL 数据库中。
* **智能标注集成**:
    * 自动批量导入 OCR 结果到 `Label Studio`。
    * 支持手动下载和上传 JSON 文件（向后兼容）。
    * 支持上传由 `Label Studio` 校对和修正后的 JSON 数据。
* **RAG 格式导出**: 将校对后的数据一键转换为 RAGFlow 等 RAG 系统兼容的 JSON 格式。
* **反向代理架构**: 通过 Nginx 统一管理，单一入口访问所有服务。
* **完整的容器化环境**: 所有服务（数据库、缓存、后端、前端等）都通过 Docker 统一管理，实现一键启动。

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- （可选）NVIDIA Docker Runtime（如需 GPU 加速）

### 一键启动

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 LABEL_STUDIO_API_TOKEN 等

# 2. 启动所有服务
docker-compose up -d --build
```

就这么简单！所有服务都会自动启动。

### 启用 GPU 加速（可选）

如果您有 NVIDIA GPU：

1. 验证 GPU：
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

2. 编辑 `docker-compose.yml`，在 celery 服务中取消 GPU deploy 部分的注释

3. 重启服务：
```bash
docker-compose up -d --build
```

## 📍 访问地址

所有服务通过统一的 Nginx 入口访问：

- **前端应用**: `http://localhost/` 或 `http://your-server-ip/`
- **后端 API**: `http://localhost/api/` 或 `http://your-server-ip/api/`
- **Label Studio**: `http://localhost/label-studio/` 或 `http://your-server-ip/label-studio/`
- **健康检查**: `http://localhost/health`

> 💡 首次启动会下载模型文件，可能需要几分钟时间。

## 📝 使用工作流

### 推荐方式：自动导入

1. **上传 PDF**: 访问前端界面，上传一个或多个 PDF 文档
2. **等待处理**: 文档状态变为 `processed`
3. **自动导入**: 调用 API 批量导入到 Label Studio
   ```bash
   curl -X POST http://localhost/api/documents/auto-import-to-label-studio/ \
     -H "Content-Type: application/json" \
     -d '{"doc_ids": [1, 2, 3], "project_id": "1"}'
   ```
4. **校对标注**: 在 Label Studio 中校对 OCR 结果
5. **导出并上传**: 导出校对结果并上传到系统
6. **生成 RAG 文件**: 下载 RAGFlow 格式文件

### 传统方式：手动导入（向后兼容）

1. 上传 PDF
2. 下载原始 OCR JSON
3. 手动导入 Label Studio
4. 后续步骤同上

## ⚙️ 配置说明

### Label Studio 配置

1. 访问 `http://localhost/label-studio/`
2. 创建账号并登录
3. 生成 API Token（Account & Settings → Access Token）
4. 更新 `.env` 文件：
   ```bash
   LABEL_STUDIO_API_TOKEN=your_token_here
   LABEL_STUDIO_PROJECT_ID=1
   ```
5. 重启服务：`docker-compose restart backend celery`

### GPU 配置

1. 安装 [NVIDIA Docker Runtime](https://github.com/NVIDIA/nvidia-docker)
2. 验证安装：
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```
3. 编辑 `docker-compose.yml`，在 celery 服务中取消 deploy 部分的注释
4. 重启服务：`docker-compose up -d --build`

## 📚 详细文档

完整的部署和配置指南请参阅：[DEPLOYMENT.md](DEPLOYMENT.md)

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

## 🏗️ 架构说明

```
┌─────────────┐
│   Nginx     │  ← 统一入口 (端口 80)
│  (反向代理)  │
└──────┬──────┘
       │
   ────┼────────────────────────
   │   │                       │
   ▼   ▼                       ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐
│ Frontend│  │ Backend  │  │ Label Studio │
│  (Vue)  │  │ (Django) │  │              │
└─────────┘  └────┬─────┘  └──────────────┘
                  │
         ─────────┼─────────
         │        │        │
         ▼        ▼        ▼
     ┌─────┐  ┌──────┐  ┌──────┐
     │ DB  │  │Redis │  │Celery│
     └─────┘  └──────┘  └──────┘
```

## 📞 支持

如有问题，请查看：
- [详细部署文档](DEPLOYMENT.md)
- 项目日志：`docker-compose logs`
- GitHub Issues
