<template>
  <div class="hero-section flex-grow-1 d-flex align-items-center py-5 position-relative">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>

    <div class="container text-center z-10 position-relative">
      <div class="badge-glow mb-4 mx-auto">v2.0 Architecture Online</div>

      <h1 class="display-3 fw-black text-white mb-3 text-shadow">
        Stop Taking Notes.<br />
        <span class="text-gradient">Start Building an Engine of Thought.</span>
      </h1>
      <p class="lead text-light mb-5 mx-auto opacity-75" style="max-width: 650px">
        NeuralFortress autonomously ingests, categorizes, and connects your research into a
        hyper-intelligent knowledge matrix. No folders. No friction. Just pure recall.
      </p>

      <div class="input-card glass-panel mx-auto rounded-4 p-2 text-start transition-hover">
        <div class="p-3 border-bottom border-light-subtle d-flex align-items-center">
          <div class="live-indicator me-2"></div>
          <span class="text-white opacity-75 small fw-medium font-monospace"
            >SYSTEM_READY // AWAITING_INPUT</span
          >
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
    <div class="input-card glass-panel mx-auto rounded-4 p-4 mt-5 text-start">
        <h4 class="text-white mb-3 mt-0 fs-5 font-monospace">_QUERY_THE_MATRIX</h4>
        <div class="d-flex gap-2 mb-3">
          <input 
            v-model="searchQuery" 
            @keyup.enter="handleSearch"
            type="text" 
            class="form-control bg-transparent border-light-subtle text-white" 
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
      <div class="mt-5 pt-5 border-top border-secondary border-opacity-25 w-100">
        <h3 class="text-white mb-4 font-monospace text-start ps-2">
          <span class="text-info">></span> _THE_MATRIX_ARCHIVE
        </h3>
        
        <div v-if="isLoadingDocs" class="text-info pulsing-text font-monospace text-start ps-2">
          >> Decrypting neural pathways...
        </div>
        
        <div v-else class="row g-4 text-start">
          <div v-for="doc in documents" :key="doc.id" class="col-md-6 col-lg-4">
            <div class="input-card glass-panel h-100 p-4 rounded-4 transition-hover d-flex flex-column">
              <div class="d-flex justify-content-between align-items-start mb-3 border-bottom border-secondary border-opacity-25 pb-2">
                <span class="text-info small font-monospace">DOC_{{ doc.id }}</span>
                <span class="text-secondary small">{{ doc.date }}</span>
              </div>
              
              <p class="text-white fw-medium mb-3 flex-grow-1 fs-6">
                {{ doc.summary }}
              </p>
              
              <div class="mb-3 d-flex flex-wrap gap-2">
                <span v-for="(tag, index) in doc.tags" :key="index" class="badge bg-dark border border-info text-info font-monospace fw-normal p-2">
                  #{{ tag }}
                </span>
              </div>
              
              <div class="mt-auto pt-2">
                <p class="text-white opacity-50 small mb-0 text-truncate font-monospace" :title="doc.rawText">
                  > {{ doc.rawText }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

// Reactive variables to hold the text and UI state
const rawText = ref('');
const isProcessing = ref(false);
const systemMessage = ref('');

// The function that fires when you click the button
const handleIngest = async () => {
  if (!rawText.value.trim()) {
    systemMessage.value = "Please enter data to ingest.";
    return;
  }

  isProcessing.value = true;
  systemMessage.value = "Neural Core processing: Generating vectors and summaries...";

  try {
    // Send the text to the FastAPI backend
    const response = await api.ingestData(rawText.value);
    
    // Success handling
    systemMessage.value = `Success! Document ID ${response.data.document_id} assimilated into the Matrix.`;
    rawText.value = ''; // Clear the input box
    await fetchDocuments();
    
    // Hide the success message after 4 seconds
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
// --- RETRIEVAL STATE ---
const searchQuery = ref('');
const isSearching = ref(false);
const displayedResponse = ref(''); // Holds the text currently being "typed"
let typingInterval = null;

// The Typewriter Animation Engine
const typeWriterEffect = (text) => {
  displayedResponse.value = '';
  clearInterval(typingInterval);
  let i = 0;
  
  // Types one character every 15 milliseconds
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
  displayedResponse.value = ''; // Clear previous answer
  clearInterval(typingInterval); // Stop any ongoing typing
  
  try {
    const response = await api.searchNotes(searchQuery.value);
    // Instead of showing it all at once, feed it to the typewriter
    typeWriterEffect(response.data.answer);
  } catch (error) {
    typeWriterEffect("CRITICAL ERROR: Could not retrieve data from the Neural Matrix.");
  } finally {
    isSearching.value = false;
  }
};

// --- THE MEMORY BROWSER (MATRIX) ---
const documents = ref([]);
const isLoadingDocs = ref(true);

const fetchDocuments = async () => {
  try {
    const response = await api.getAllDocuments();
    
    // Parse the raw database text into clean UI objects
    documents.value = response.data.documents.map(doc => {
      let raw = doc.content;
      let summary = "No summary available.";
      let tags = [];
      
      // Separate the raw text from the AI Analysis
      if (raw.includes('AI_ANALYSIS:')) {
        const parts = raw.split('AI_ANALYSIS:\n');
        raw = parts[0].replace('RAW_TEXT:\n', '').trim();
        const aiPart = parts[1] || '';
        
        // Extract the Summary using Regex
        const summaryMatch = aiPart.match(/Summary:\s*(.*?)(?=\nTags:|$)/s);
        if (summaryMatch) summary = summaryMatch[1].trim();
        
        // Extract the Tags using Regex
        const tagsMatch = aiPart.match(/Tags:\s*\[(.*?)\]/);
        if (tagsMatch) {
          tags = tagsMatch[1].split(',').map(t => t.trim());
        }
      }
      
      return {
        id: doc.id,
        date: new Date(doc.created_at).toLocaleDateString(),
        rawText: raw,
        summary: summary,
        tags: tags
      };
    });
  } catch (error) {
    console.error("Failed to fetch the matrix:", error);
  } finally {
    isLoadingDocs.value = false;
  }
};

// Automatically fetch the notes when the page loads
onMounted(() => {
  fetchDocuments();
});
</script>

<style scoped>
.fw-black {
  font-weight: 900;
  letter-spacing: -1.5px;
  line-height: 1.1;
}
.text-shadow {
  text-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.text-gradient {
  background: -webkit-linear-gradient(0deg, #00d2ff, #ff007f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.badge-glow {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 50px;
  background: rgba(0, 210, 255, 0.1);
  border: 1px solid rgba(0, 210, 255, 0.4);
  color: #00d2ff;
  font-weight: bold;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  box-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
}

.input-card {
  max-width: 800px;
  border-color: rgba(255, 255, 255, 0.2);
}

.transition-hover {
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}
.transition-hover:hover {
  transform: translateY(-5px);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.4),
    0 0 30px rgba(255, 0, 127, 0.2);
}

.custom-textarea {
  outline: none !important;
  resize: none;
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
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

/* Neon Action Button */
.btn-action {
  background: linear-gradient(90deg, #ff007f, #6441a5);
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 50px;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-action:hover {
  box-shadow: 0 0 25px rgba(255, 0, 127, 0.6);
  transform: scale(1.05);
}

/* Floating Orbs for deep background movement */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.5;
  animation: drift 20s infinite alternate;
}
.orb-1 {
  width: 400px;
  height: 400px;
  background: #ff007f;
  top: -100px;
  left: -100px;
}
.orb-2 {
  width: 500px;
  height: 500px;
  background: #00d2ff;
  bottom: -150px;
  right: -100px;
  animation-delay: -5s;
}

@keyframes drift {
  0% {
    transform: translate(0, 0) scale(1);
  }
  100% {
    transform: translate(100px, 150px) scale(1.2);
  }
}
.custom-textarea {
  outline: none !important;
  resize: none;
  color: #ffffff !important;
}
.custom-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}
.custom-textarea:focus {
  box-shadow: none;
  color: white;
}

.input-card {
  max-width: 800px;
  border-color: rgba(0, 210, 255, 0.3); /* Gives the input box a subtle cyan border */
  background: rgba(10, 10, 18, 0.7); /* Darker glass for better text readability */
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

/* --- Terminal UI Styles --- */
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
  white-space: pre-wrap; /* Ensures AI line breaks look correct */
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
