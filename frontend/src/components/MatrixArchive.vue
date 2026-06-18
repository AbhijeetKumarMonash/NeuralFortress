<template>
  <div class="mt-5 pt-5 border-top border-secondary border-opacity-25 w-100 text-start">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2 ps-2">
      <h3 class="text-white mb-0 font-monospace">
        <span class="text-info">></span> _THE_MATRIX_ARCHIVE
        <span class="text-secondary fs-6 ms-2">[{{ filteredDocs.length }}/{{ documents.length }} memories]</span>
      </h3>
      <input
        v-model="filterText"
        type="text"
        class="form-control form-control-sm bg-transparent border-light-subtle text-white font-monospace filter-input"
        placeholder="filter memories..."
      />
    </div>

    <div v-if="isLoadingDocs" class="text-info pulsing-text font-monospace ps-2">
      >> Decrypting neural pathways...
    </div>

    <div v-else class="archive-bank glass-panel rounded-4 p-2">
      <div v-if="filteredDocs.length === 0" class="text-secondary font-monospace p-3">
        >> No memories match this filter.
      </div>

      <div v-for="doc in filteredDocs" :key="doc.id" class="memory-row rounded-3 mb-1"
           :class="{ expanded: expandedId === doc.id }">
        <!-- Compact row (always visible, click to expand) -->
        <div class="d-flex align-items-center gap-3 p-2 px-3 row-header" @click="toggleExpand(doc.id)">
          <span class="text-info small font-monospace flex-shrink-0">DOC_{{ doc.id }}</span>
          <span class="text-white small flex-grow-1 text-truncate">{{ doc.summary }}</span>
          <span class="d-none d-md-flex gap-1 flex-shrink-0">
            <span v-for="(tag, i) in doc.tags.slice(0, 2)" :key="i"
                  class="badge bg-dark border border-info text-info font-monospace fw-normal">#{{ tag }}</span>
          </span>
          <span class="text-secondary small flex-shrink-0 d-none d-sm-inline">{{ doc.date }}</span>
          <span class="text-info small flex-shrink-0">{{ expandedId === doc.id ? '▾' : '▸' }}</span>
        </div>

        <!-- Expanded detail -->
        <div v-if="expandedId === doc.id" class="p-3 pt-0">
          <div v-if="doc.insight && doc.insight !== 'New neural pathway created. No prior related memories found.'"
               class="p-2 mb-2 rounded bg-info bg-opacity-10 border-start border-info border-3">
            <p class="text-info opacity-75 small mb-0 font-monospace">
              <i class="bi bi-link-45deg"></i> {{ doc.insight }}
            </p>
          </div>
          <div class="mb-2 d-flex flex-wrap gap-2">
            <span v-for="(tag, i) in doc.tags" :key="i"
                  class="badge bg-dark border border-info text-info font-monospace fw-normal p-2">#{{ tag }}</span>
          </div>
          <p class="text-white opacity-50 small mb-2 font-monospace raw-text">> {{ doc.rawText }}</p>
          <button class="btn btn-sm btn-outline-danger rounded-pill px-3 font-monospace"
                  :disabled="deletingId === doc.id" @click.stop="handleDelete(doc.id)">
            {{ deletingId === doc.id ? 'Purging...' : 'Purge Memory' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/api';

const emit = defineEmits(['archive-changed']);

const documents = ref([]);
const isLoadingDocs = ref(true);
const filterText = ref('');
const expandedId = ref(null);
const deletingId = ref(null);

const filteredDocs = computed(() => {
  const q = filterText.value.trim().toLowerCase();
  if (!q) return documents.value;
  return documents.value.filter(d =>
    d.summary.toLowerCase().includes(q) ||
    d.rawText.toLowerCase().includes(q) ||
    d.tags.some(t => t.toLowerCase().includes(q))
  );
});

const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id;
};

const handleDelete = async (id) => {
  if (!confirm(`Permanently purge DOC_${id} from the matrix?`)) return;
  deletingId.value = id;
  try {
    await api.deleteDocument(id);
    documents.value = documents.value.filter(d => d.id !== id);
    expandedId.value = null;
    emit('archive-changed'); // lets HomeView re-map the graph
  } catch (error) {
    console.error('Failed to purge memory:', error);
  } finally {
    deletingId.value = null;
  }
};

const focusDoc = (id) => {
     filterText.value = '';
     expandedId.value = id;
   };

const fetchDocuments = async () => {
  isLoadingDocs.value = true;
  try {
    const response = await api.getAllDocuments();
    documents.value = response.data.documents.map(doc => {
      let raw = doc.content;
      let summary = 'No summary available.';
      let tags = [];
      let insight = '';

      if (raw.includes('AI_ANALYSIS:')) {
        const parts = raw.split('AI_ANALYSIS:\n');
        raw = parts[0].replace('RAW_TEXT:\n', '').trim();
        const aiPart = parts[1] || '';

        const summaryMatch = aiPart.match(/Summary:\s*(.*?)(?=\nTags:|$)/s);
        if (summaryMatch) summary = summaryMatch[1].trim();

        const tagsMatch = aiPart.match(/Tags:\s*\[(.*?)\]/);
        if (tagsMatch) tags = tagsMatch[1].split(',').map(t => t.trim());

        if (aiPart.includes('SYNTHESIS_INSIGHT:\n')) {
          insight = aiPart.split('SYNTHESIS_INSIGHT:\n')[1].trim();
        }
      }

      return {
        id: doc.id,
        date: new Date(doc.created_at).toLocaleDateString(),
        rawText: raw,
        summary,
        tags,
        insight
      };
    });
  } catch (error) {
    console.error('Failed to fetch the matrix:', error);
  } finally {
    isLoadingDocs.value = false;
  }
};

onMounted(fetchDocuments);

defineExpose({ fetchDocuments, focusDoc });
</script>

<style scoped>
.archive-bank {
  max-height: 450px;
  overflow-y: auto;
  border: 1px solid rgba(0, 210, 255, 0.3);
  background: rgba(10, 10, 18, 0.7);
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 210, 255, 0.4) transparent;
}

.filter-input {
  max-width: 220px;
  box-shadow: none !important;
}
.filter-input:focus { border-color: #00d2ff !important; }
.filter-input::placeholder { color: rgba(255, 255, 255, 0.35); }

.memory-row {
  border: 1px solid transparent;
  transition: background 0.2s ease, border-color 0.2s ease;
}
.memory-row:hover { background: rgba(0, 210, 255, 0.05); }
.memory-row.expanded {
  background: rgba(0, 210, 255, 0.07);
  border-color: rgba(0, 210, 255, 0.3);
}
.row-header { cursor: pointer; }

.raw-text {
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.pulsing-text { animation: pulse 1.5s infinite; }
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>