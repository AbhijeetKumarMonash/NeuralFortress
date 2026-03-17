<template>
  <div class="input-card glass-panel mx-auto rounded-4 p-4 mt-5 text-start">
    <h4 class="text-white mb-3 mt-0 fs-5 font-monospace">_QUERY_THE_MATRIX</h4>
    <div class="d-flex gap-2 mb-3">
      <input 
        v-model="searchQuery" 
        @keyup.enter="handleSearch"
        type="text" 
        class="form-control bg-transparent border-light-subtle text-white custom-input" 
        placeholder="Ask your notes anything..."
        :disabled="isSearching"
      />
      <button @click="handleSearch" :disabled="isSearching" class="btn btn-outline-info rounded-pill px-4">
        {{ isSearching ? 'Searching...' : 'Search' }}
      </button>
    </div>
    
    <div v-if="isSearching || displayedResponse" class="terminal-container p-4 mt-4 rounded-3 position-relative overflow-hidden">
      <div class="scanline"></div>
      
      <div class="terminal-header d-flex align-items-center mb-3 pb-2 border-bottom border-secondary border-opacity-50">
        <div class="terminal-dot bg-danger"></div>
        <div class="terminal-dot bg-warning"></div>
        <div class="terminal-dot bg-success"></div>
        <span class="ms-3 text-secondary small font-monospace">sys.vidya@neural-core:~$ run retrieval_agent.sh</span>
      </div>
      
      <div class="terminal-body font-monospace">
        <span v-if="isSearching" class="pulsing-text text-info">>> Accessing high-dimensional vector space...</span>
        <span v-else class="text-success">{{ displayedResponse }}</span>
        <span class="cursor" v-if="!isSearching">_</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import api from '@/api';

const searchQuery = ref('');
const isSearching = ref(false);
const displayedResponse = ref(''); 
let typingInterval = null;

const typeWriterEffect = (text) => {
  displayedResponse.value = '';
  clearInterval(typingInterval);
  let i = 0;
  
  typingInterval = setInterval(() => {
    if (i < text.length) {
      displayedResponse.value += text.charAt(i);
      i++;
    } else {
      clearInterval(typingInterval);
    }
  }, 15); 
};

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;
  
  isSearching.value = true;
  displayedResponse.value = ''; 
  clearInterval(typingInterval); 
  
  try {
    const response = await api.searchNotes(searchQuery.value);
    typeWriterEffect(response.data.answer);
  } catch (error) {
    typeWriterEffect("CRITICAL ERROR: Could not retrieve data from the Neural Matrix.");
  } finally {
    isSearching.value = false;
  }
};

// Clean up the interval if the component is destroyed
onUnmounted(() => {
  if (typingInterval) clearInterval(typingInterval);
});
</script>

<style scoped>
.input-card {
  max-width: 800px;
  border-color: rgba(0, 210, 255, 0.3);
  background: rgba(10, 10, 18, 0.7);
}

.custom-input {
  outline: none !important;
  box-shadow: none !important;
}

.custom-input:focus {
  border-color: #00d2ff !important;
}

/* Terminal UI Styles */
.terminal-container {
  background-color: #050508;
  border: 1px solid rgba(0, 210, 255, 0.2);
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8);
}

.terminal-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
}

.terminal-body {
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap; 
}

.cursor {
  display: inline-block;
  width: 10px;
  height: 1.1em;
  background-color: #00ffcc;
  vertical-align: bottom;
  margin-left: 2px;
  animation: cursor-blink 1s step-end infinite;
}

.scanline {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: rgba(0, 210, 255, 0.2);
  opacity: 0.5;
  animation: scan 6s linear infinite;
  pointer-events: none;
}

.pulsing-text {
  animation: pulse 1.5s infinite;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@keyframes scan {
  0% { top: -5px; }
  100% { top: 100%; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>