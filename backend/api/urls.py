from django.urls import path
from .views import (
    DocumentListView, 
    DocumentDetailView, 
    DocumentUploadView, 
    LabelStudioTaskView,
    AutoImportToLabelStudioView,  # 新增：自动导入视图
    SubmitCorrectionView,
    GenerateRAGFlowPayloadView
)

urlpatterns = [
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    
    path('documents/<int:pk>/to-label-studio/', LabelStudioTaskView.as_view(), name='download_raw_ocr'),
    
    # 新增：批量自动导入到Label Studio
    path('documents/auto-import-to-label-studio/', AutoImportToLabelStudioView.as_view(), name='auto_import_to_label_studio'),
    
    path('documents/<int:pk>/submit-correction/', SubmitCorrectionView.as_view(), name='submit_correction'),

    # RAGFlow 转换和下载的端点
    path('documents/<int:pk>/to-ragflow/', GenerateRAGFlowPayloadView.as_view(), name='generate_ragflow_payload'),
]
