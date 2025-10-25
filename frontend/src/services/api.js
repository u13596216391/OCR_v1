import axios from 'axios';
import API_BASE_URL from '../config';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

export default {
    getDocuments() {
        return apiClient.get('/documents/');
    },
    uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);
        return apiClient.post('/documents/upload/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },
    getLabelStudioTasks(docId) {
        return apiClient.get(`/documents/${docId}/to-label-studio/`);
    },
    // 新增：批量自动导入到Label Studio
    autoImportToLabelStudio(docIds, projectId) {
        return apiClient.post('/documents/auto-import-to-label-studio/', {
            doc_ids: docIds,
            project_id: projectId
        });
    },
    ingestToRagflow(docId, correctedData) {
        return apiClient.post(`/documents/${docId}/ingest-to-ragflow/`, correctedData);
    }
};