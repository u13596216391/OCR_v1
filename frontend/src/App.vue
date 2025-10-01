<template>
  <div id="app">
    <h1>OCR Pipeline</h1>

    <input type="file" @change="handleFileUpload" />
    <button @click="submitFile">Upload & Process</button>

    <h2>Processed Documents</h2>
    <ul>
      <li v-for="doc in documents" :key="doc.id">
        {{ doc.original_pdf_path }} - <strong>{{ doc.status }}</strong>
        <button @click="generateLSTasks(doc.id)" v-if="doc.status === 'processed'">
          Get Label Studio Tasks
        </button>
      </li>
    </ul>
  </div>
</template>

<script>
import api from './services/api';

export default {
  name: 'App',
  data() {
    return {
      documents: [],
      fileToUpload: null,
    };
  },
  methods: {
    async fetchDocuments() {
      const response = await api.getDocuments();
      this.documents = response.data;
    },
    handleFileUpload(event) {
      this.fileToUpload = event.target.files[0];
    },
    async submitFile() {
      if (!this.fileToUpload) return;
      try {
        await api.uploadDocument(this.fileToUpload);
        alert('File uploaded! Processing in the background.');
        this.fetchDocuments(); // Refresh list
      } catch (error) {
        console.error('Upload failed:', error);
      }
    },
    async generateLSTasks(docId) {
        try {
            const response = await api.getLabelStudioTasks(docId);
            // In a real app, you would download this JSON or use it to auto-import
            console.log('Label Studio Task JSON:', response.data);
            alert('Check the console for Label Studio Task JSON.');
        } catch (error) {
            console.error('Failed to generate tasks:', error);
        }
    }
  },
  mounted() {
    this.fetchDocuments();
  }
};
</script>