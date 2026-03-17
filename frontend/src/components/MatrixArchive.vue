<template>
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
          <div v-if="doc.insight && doc.insight !== 'New neural pathway created. No prior related memories found.'" class="p-2 mb-3 rounded bg-info bg-opacity-10 border-start border-info border-3">
            <p class="text-info opacity-75 small mb-0 font-monospace">
              <i class="bi bi-link-45deg"></i> {{ doc.insight }}
            </p>
          </div>
          
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
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';

const documents = ref([]);
const isLoadingDocs = ref(true);

const fetchDocuments = async () => {
  isLoadingDocs.value = true;
  try {
    const response = await api.getAllDocuments();
    
    documents.value = response.data.documents.map(doc => {
      // Inside fetchDocuments mapping:
      let raw = doc.content;
      let summary = "No summary available.";
      let tags = [];
      let insight = ""; // New variable
      
      if (raw.includes('AI_ANALYSIS:')) {
        const parts = raw.split('AI_ANALYSIS:\n');
        raw = parts[0].replace('RAW_TEXT:\n', '').trim();
        const aiPart = parts[1] || '';
        
        // Extract Summary
        const summaryMatch = aiPart.match(/Summary:\s*(.*?)(?=\nTags:|$)/s);
        if (summaryMatch) summary = summaryMatch[1].trim();
        
        // Extract Tags
        const tagsMatch = aiPart.match(/Tags:\s*\[(.*?)\]/);
        if (tagsMatch) {
          tags = tagsMatch[1].split(',').map(t => t.trim());
        }
        
        // Extract Synthesis Insight
        if (aiPart.includes('SYNTHESIS_INSIGHT:\n')) {
            insight = aiPart.split('SYNTHESIS_INSIGHT:\n')[1].trim();
        }
      }
      
      return {
        id: doc.id,
        date: new Date(doc.created_at).toLocaleDateString(),
        rawText: raw,
        summary: summary,
        tags: tags,
        insight: insight // Pass it to the template
      };
    });
  } catch (error) {
    console.error("Failed to fetch the matrix:", error);
  } finally {
    isLoadingDocs.value = false;
  }
};

onMounted(() => {
  fetchDocuments();
});

// Expose this function so HomeView can trigger a refresh when a new note is uploaded
defineExpose({
  fetchDocuments
});
</script>

<style scoped>
.input-card {
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

.pulsing-text {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>