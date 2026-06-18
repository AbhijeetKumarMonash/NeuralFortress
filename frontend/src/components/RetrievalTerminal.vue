<template>
  <div class="input-card glass-panel mx-auto rounded-4 p-4 mt-4 text-start">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h4 class="text-white mb-0 fs-5 font-monospace">_QUERY_THE_MATRIX</h4>

      <!-- MODE TOGGLE: classic RAG pipeline vs autonomous agent -->
      <div class="mode-toggle d-inline-flex p-1 rounded-pill">
        <button
          class="mode-btn font-monospace"
          :class="{ active: mode === 'rag' }"
          @click="mode = 'rag'"
        >
          RAG_MODE
        </button>
        <button
          class="mode-btn font-monospace"
          :class="{ active: mode === 'agent' }"
          @click="mode = 'agent'"
        >
          AGENT_MODE
        </button>
        <button class="mode-btn font-monospace" :class="{ active: mode === 'graph' }" @click="mode = 'graph'">
  GRAPH_MODE
</button>
      </div>
    </div>

    <p class="text-secondary small font-monospace mb-3">{{ modeBlurb }}</p>

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

    <div
      v-if="isSearching || displayedResponse"
      class="terminal-container p-4 mt-4 rounded-3 position-relative overflow-hidden"
    >
      <div class="scanline"></div>

      <div
        class="terminal-header d-flex align-items-center mb-3 pb-2 border-bottom border-secondary border-opacity-50"
      >
        <div class="terminal-dot bg-danger"></div>
        <div class="terminal-dot bg-warning"></div>
        <div class="terminal-dot bg-success"></div>
        <span class="ms-3 text-secondary small font-monospace">
          sys.vidya@neural-core:~$ run {{ mode === 'agent' ? 'autonomous_agent.sh' : 'rag_pipeline.sh' }}
        </span>
      </div>

      <div class="terminal-body font-monospace">
        <span v-if="isSearching" class="pulsing-text text-info">
          {{
            mode === 'agent'
              ? '>> Agent reasoning: selecting tools...'
              : '>> Accessing high-dimensional vector space...'
          }}
        </span>
        <span v-else class="text-success">{{ displayedResponse }}</span>
        <span class="cursor" v-if="!isSearching">_</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted , computed } from 'vue';
import api from '@/api';

const searchQuery = ref('');
const isSearching = ref(false);
const displayedResponse = ref('');
const mode = ref('agent'); // default to the showpiece
let typingInterval = null;
const emit = defineEmits(['graph-result']);

const modeBlurb = computed(() => ({
  agent: '>> Autonomous mode: Gemini decides which tools to call and may search multiple times.',
  graph: '>> GraphRAG mode: traverses entity relationships across documents — multi-hop, beyond vector distance.',
  rag: '>> Pipeline mode: fixed embed → retrieve top-3 → answer.'
}[mode.value]));

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
  }, 12);
};

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;

  isSearching.value = true;
  displayedResponse.value = '';
  clearInterval(typingInterval);

  try {
    let text;
    if (mode.value === 'agent') {
      const response = await api.askAgent(searchQuery.value);
      const steps = response.data.agent_steps || [];
      text = steps.length
        ? `[AGENT TOOL CALLS: ${steps.join(' → ')}]\n\n${response.data.answer}`
        : response.data.answer;
    }
     else if (mode.value === 'graph') {
  const r = await api.askGraphRAG(searchQuery.value);
  const path = r.data.reasoning_path || [];
  const hops = path.map(p => `${p.from} --${p.predicate}--> ${p.to}`).join('\n');
  text = hops ? `[GRAPH PATH · ${r.data.hops} hops · docs ${ (r.data.source_documents||[]).join(', ') }]\n${hops}\n\n${r.data.answer}` : r.data.answer;
  emit('graph-result', { entities: r.data.entities || [], path });
}
    else {
      const response = await api.searchNotes(searchQuery.value);
      text = response.data.answer;
    }
    typeWriterEffect(text);
  } catch (error) {
    console.error('Query error:', error);
    typeWriterEffect('CRITICAL ERROR: Could not retrieve data from the Neural Matrix.');
  } finally {
    isSearching.value = false;
  }
};

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

.mode-toggle {
  background: rgba(5, 5, 8, 0.8);
  border: 1px solid rgba(0, 210, 255, 0.25);
}

.mode-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  padding: 6px 16px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.mode-btn.active {
  background: rgba(0, 210, 255, 0.15);
  color: #00d2ff;
  border: 1px solid rgba(0, 210, 255, 0.5);
}

.custom-input {
  outline: none !important;
  box-shadow: none !important;
}

.custom-input:focus {
  border-color: #00d2ff !important;
}

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
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

@keyframes scan {
  0% {
    top: -5px;
  }
  100% {
    top: 100%;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>