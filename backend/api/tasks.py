import subprocess
import os
import time
import uuid
import json
from celery import shared_task
from .models import OcrDocument
from django.conf import settings
from pathlib import Path
import logging
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

DATA_ROOT = settings.DATA_ROOT_PATH
BASE_OUTPUT_DIR = DATA_ROOT / 'data' / 'mineru_output'
POPPLER_PATH = os.getenv('POPPLER_PATH', None)
MINERU_COMMAND = 'mineru'

# GPU检测和配置
def check_gpu_available():
    """检测GPU是否可用"""
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"✓ GPU可用: {gpu_count} 个设备, 主设备: {gpu_name}")
            return True
        else:
            logger.info("✗ GPU不可用，将使用CPU模式")
            return False
    except Exception as e:
        logger.warning(f"GPU检测失败: {e}，将使用CPU模式")
        return False

@shared_task
def process_pdf_with_mineru(doc_id):
    doc = None
    try:
        # 检测GPU可用性
        gpu_available = check_gpu_available()
        if gpu_available:
            logger.info(f"文档 {doc_id} 将使用GPU加速处理")
        else:
            logger.info(f"文档 {doc_id} 将使用CPU处理")
        
        doc = OcrDocument.objects.get(id=doc_id)
        doc.status = 'processing'
        doc.save(update_fields=['status'])

        pdf_path = Path(doc.original_pdf_path)
        unique_folder_name = uuid.uuid4().hex[:12]
        task_output_dir = BASE_OUTPUT_DIR / unique_folder_name
        os.makedirs(task_output_dir, exist_ok=True)

        command_str = f'"{MINERU_COMMAND}" -p "{str(pdf_path)}" -o "{str(task_output_dir)}"'

        logger.info(f"Executing command: {command_str}")
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True, timeout=3600)

        # ==================== 核心修改开始 ====================
        
        # 无论成功与否，都先记录 stdout 和 stderr，便于调试
        if result.stdout:
            logger.info(f"MinerU STDOUT for Doc ID {doc_id}:\n{result.stdout}")
        if result.stderr:
            # 将 stderr 记录为警告，即使命令没有失败
            logger.warning(f"MinerU STDERR for Doc ID {doc_id}:\n{result.stderr}")

        if result.returncode != 0:
            # 如果返回码不为0，说明是明确的失败
            raise RuntimeError(f"MinerU execution failed with return code {result.returncode}.")

        mineru_created_dir = task_output_dir / pdf_path.stem
        json_path = mineru_created_dir / "auto" / f"{pdf_path.stem}_middle.json"
        
        time.sleep(1)
        
        if not os.path.exists(json_path):
            # 如果文件依然不存在，抛出错误，此时日志中已有详细的 stdout/stderr
            raise FileNotFoundError(f"'_middle.json' not found at expected path: {json_path}. MinerU did not produce the expected output.")
            
        # ===================== 核心修改结束 =====================

        logger.info(f"Found OCR JSON file at: {json_path}. Reading content.")
        with open(json_path, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        doc.raw_ocr_json = ocr_data
        doc.save(update_fields=['raw_ocr_json'])
        logger.info(f"Successfully saved raw_ocr_json to database for Doc ID {doc_id}.")
        
        logger.info(f"Converting PDF pages to images for Doc ID {doc_id}.")
        pages_dir = task_output_dir / "pages"
        os.makedirs(pages_dir, exist_ok=True)
        
        pil_images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH, thread_count=4, fmt='jpeg')
        for i, image in enumerate(pil_images):
            page_num = i + 1
            filename = f"page-{str(page_num).zfill(4)}.jpg"
            image.save(pages_dir / filename, 'JPEG')
        
        logger.info(f"Successfully converted and saved {len(pil_images)} images.")

        doc.mineru_json_path = str(json_path)
        doc.status = 'processed'
        doc.save(update_fields=['mineru_json_path', 'status'])
        
        logger.info(f"Celery Task fully succeeded for Doc ID {doc_id}.")
        return f"Success: {str(json_path)}"

    except Exception as e:
        if doc:
            doc.status = 'failed'
            doc.save(update_fields=['status'])
        # 错误日志现在会包含更丰富的信息
        logger.error(f"Error in Celery task for doc ID {doc_id if 'doc_id' in locals() else 'unknown'}: {e}", exc_info=True)
        raise e