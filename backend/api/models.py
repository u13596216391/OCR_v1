# api/models.py
from django.db import models

class OcrDocument(models.Model):
    """
    Represents a single document processing workflow.
    """
    original_pdf_path = models.CharField(max_length=1024)
    mineru_json_path = models.CharField(max_length=1024, blank=True, null=True)

    # FIX: 添加此字段以存储来自 MinerU 的原始 OCR JSON。
    # 这修复了 celery 任务中一个潜在的保存错误，并有助于调试。
    raw_ocr_json = models.JSONField(null=True, blank=True, verbose_name="原始OCR JSON")

    # NEW: 添加此字段以存储用户从 Label Studio 提交的、校对后的 JSON 数据。
    corrected_label_studio_json = models.JSONField(null=True, blank=True, verbose_name="校对后的JSON")

    # NEW: 添加Label Studio项目ID字段，用于追踪文档导入到哪个项目
    label_studio_project_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Label Studio项目ID")

    # UPDATED: 状态选项已更新，增加了 'corrected'。
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_pdf_path
