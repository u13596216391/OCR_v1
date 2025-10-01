from django.urls import path
from .views import (
    DocumentListView, 
    DocumentDetailView, 
    DocumentUploadView, 
    LabelStudioTaskView,
    SubmitCorrectionView,
    GenerateRAGFlowPayloadView # 1. 导入新视图
)

urlpatterns = [
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    
    path('documents/<int:pk>/to-label-studio/', LabelStudioTaskView.as_view(), name='download_raw_ocr'),
    
    path('documents/<int:pk>/submit-correction/', SubmitCorrectionView.as_view(), name='submit_correction'),

    # 2. 新增 RAGFlow 转换和下载的端点
    path('documents/<int:pk>/to-ragflow/', GenerateRAGFlowPayloadView.as_view(), name='generate_ragflow_payload'),
]
