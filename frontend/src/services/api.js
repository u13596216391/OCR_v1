import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://10.4.34.108:8010/api',
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
    ingestToRagflow(docId, correctedData) {
        return apiClient.post(`/documents/${docId}/ingest-to-ragflow/`, correctedData);
    }
};