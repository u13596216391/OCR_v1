# api/serializers.py
from rest_framework import serializers
from .models import OcrDocument

class OcrDocumentSerializer(serializers.ModelSerializer):
    """
    Serializes the OcrDocument model to and from JSON format.
    Includes the new fields for raw and corrected JSON data.
    """
    class Meta:
        model = OcrDocument
        # 确保所有需要的字段都包含在内，以便前端可以访问它们
        fields = (
            'id', 
            'original_pdf_path', 
            'mineru_json_path', 
            'status', 
            'created_at', 
            'raw_ocr_json', 
            'corrected_label_studio_json'
        )
