<template>
  <div class="input-card glass-panel mx-auto rounded-4 p-2 text-start transition-hover mb-5">
    <div class="p-3 border-bottom border-light-subtle d-flex align-items-center">
      <div class="live-indicator me-2"></div>
      <span class="text-white opacity-75 small fw-medium font-monospace">
        SYSTEM_READY // AWAITING_INPUT
      </span>
    </div>

    <div class="p-4">
      <textarea
        v-model="rawText"
        :disabled="isProcessing"
        class="custom-textarea form-control bg-transparent border-0 shadow-none fs-5 text-white"
        placeholder="Drop your scattered thoughts, project links, or raw data here..."
        rows="5"
      ></textarea>
    </div>

    <div class="d-flex justify-content-between align-items-center p-3 rounded-bottom mt-2">
      <span class="text-info small font-monospace">
        <i class="bi bi-cpu me-1"></i> 
        {{ systemMessage || 'AI Summarization Ready' }}
      </span>
      
      <button 
        @click="handleIngest" 
        :disabled="isProcessing"
        class="btn-action"
      >
        {{ isProcessing ? 'Assimilating...' : 'Initialize Upload' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api';

// Define the event so we can tell the parent (HomeView) to refresh the Matrix when a new note is saved
const emit = defineEmits(['document-ingested']);

const rawText = ref('');
const isProcessing = ref(false);
const systemMessage = ref('');

const handleIngest = async () => {
  if (!rawText.value.trim()) {
    systemMessage.value = "Please enter data to ingest.";
    return;
  }

  isProcessing.value = true;
  systemMessage.value = "Neural Core processing: Generating vectors and summaries...";

  try {
    const response = await api.ingestData(rawText.value);
    systemMessage.value = `Success! Document ID ${response.data.document_id} assimilated.`;
    rawText.value = ''; 
    
    // Tell the parent component to update the grid!
    emit('document-ingested');
    
    setTimeout(() => {
      systemMessage.value = '';
    }, 4000);

  } catch (error) {
    console.error("Ingestion error:", error);
    systemMessage.value = "CRITICAL ERROR: Failed to communicate with backend.";
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style scoped>
/* CSS specific only to the Ingestion Engine */
.input-card {
  max-width: 800px;
  border-color: rgba(0, 210, 255, 0.3);
  background: rgba(10, 10, 18, 0.7);
}

.transition-hover {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.transition-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 30px rgba(255, 0, 127, 0.2);
}

.custom-textarea {
  outline: none !important;
  resize: none;
  color: #ffffff !important;
}

.custom-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
  font-weight: 300;
}

.custom-textarea:focus {
  box-shadow: none;
  color: white;
}

.live-indicator {
  width: 10px;
  height: 10px;
  background-color: #00ffcc;
  border-radius: 50%;
  box-shadow: 0 0 10px #00ffcc;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.btn-action {
  background: linear-gradient(90deg, #ff007f, #6441a5);
  color: white;
  border: 1px solid rgba(255, 0, 127, 0.5);
  padding: 12px 28px;
  border-radius: 50px;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
}

.btn-action:hover {
  box-shadow: 0 0 30px rgba(255, 0, 127, 0.8);
  transform: scale(1.05);
}
</style>