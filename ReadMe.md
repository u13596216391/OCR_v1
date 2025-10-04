# OCR-RAG 文档处理流水线

该系统通过 Docker Compose 进行容器化编排，集成了后端 API、异步任务处理、前端界面以及第三方标注工具 Label Studio。

## 核心特性

* **PDF 上传**: 通过 Web 界面上传 PDF 文档进行处理。
* **自动化 OCR**: 使用 `mineru` 工具作为核心 OCR 引擎，在后台异步处理 PDF。
* **数据持久化**: 所有文档信息、状态和处理结果都存储在 PostgreSQL 数据库中。
* **人工校对接口**:
    * 为 `Label Studio` 提供可直接导入的原始 OCR 结果（JSON 格式）。
    * 支持上传由 `Label Studio` 校对和修正后的 JSON 数据。
* **RAG 格式导出**: 将校对后的数据一键转换为 RAGFlow 等 RAG 系统兼容的 JSON 格式。
* **完整的容器化环境**: 所有服务（数据库、缓存、后端、前端等）都通过 Docker 统一管理，实现一键启动。

### 配置

项目通过 `docker-compose.yml` 文件管理大部分配置。关键的环境变量如下，请确保它们在 `docker-compose.yml` 的 `backend` 和 `celery` 服务中配置正确：

* `LOCAL_DATA_PATH=/`: 定义了应用内部数据存储的根路径。
* `POSTGRES_*` and `REDIS_HOST`: 用于连接数据库和 Redis 服务。

如何使用：
1、访问服务

 前端应用**: `http://localhost:8080`
 后端 API**: `http://localhost:8000/api/`
 label Studio**: `http://localhost:8081`

2、工作流

1.  上传 PDF: 访问前端界面 (`http://localhost:8080`)，上传一个或多个 PDF 文档。
2.  后台处理: 上传后，系统会自动触发一个 Celery 异步任务。您可以在列表中看到文档状态变为 `processing`。
3.  处理完成: 任务成功后，状态变为 `processed`。
4.  下载原始 OCR JSON: 在前端点击对应文档的“下载原始 JSON”按钮。
5.  导入 Label Studio: 访问 Label Studio (`http://localhost:8081`)，创建一个新项目，并导入上一步下载的 JSON 文件进行人工校对和修正。        
6.  上传校对后 JSON: 校对完成后，从 Label Studio 导出数据。在前端界面点击“上传校对后 JSON”按钮，提交修正后的文件。文档状态变为 `corrected`。
7.  生成 RAGFlow Payload: 点击“生成 RAG 文件”按钮，系统将下载一个为 RAGFlow 定制的 JSON 文件，文档状态变为 `ingested`。
