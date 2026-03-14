import axios from 'axios';

// Create a central Axios instance pointing to your Python backend
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // Your FastAPI address
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  // Ping the server to check status
  checkStatus() {
    return apiClient.get('/status');
  },
  
  // Send text to be processed and saved
  ingestData(textSource) {
    return apiClient.post('/ingest', {
      text: textSource,
      source: 'vue_frontend'
    });
  },
  
  // Ask the AI a question about your notes
  searchNotes(question) {
    return apiClient.post('/search', {
      query: question
    });
  },
  // Fetch all saved memories from the database
  getAllDocuments() {
    return apiClient.get('/documents');
  }
  
};