<template>
  <div class="hero-section flex-grow-1 d-flex flex-column py-5 position-relative">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>

    <div class="container text-center z-10 position-relative">
      <div class="badge-glow mb-4 mx-auto">v2.0 Architecture Online</div>

      <h1 class="display-4 fw-black text-white mb-3 text-shadow">
        Stop Taking Notes.<br />
        <span class="text-gradient">Start Building an Engine of Thought.</span>
      </h1>
      <p class="lead text-light mb-4 mx-auto opacity-75" style="max-width: 650px">
        NeuralFortress autonomously ingests, categorizes, and connects your research into a
        hyper-intelligent knowledge matrix.
      </p>

      <!-- TAB NAVIGATION -->
      <div class="tab-bar d-inline-flex gap-1 mb-4 p-1 rounded-pill flex-wrap justify-content-center">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="tab-btn font-monospace"
          :class="{ active: activeTab === tab.id }"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- TAB PANELS (v-show keeps components alive so graph physics & data persist) -->
      <div v-show="activeTab === 'ingest'">
        <IngestionEngine @document-ingested="refreshAll" />
      </div>

      <div v-show="activeTab === 'query'">
  <RetrievalTerminal @graph-result="onGraphResult" />
</div>

<div v-show="activeTab === 'knowledge'">
  <EntityGraph ref="entityGraphRef" />
</div>

      <div v-show="activeTab === 'map'">
        <KnowledgeGraph ref="graphRef" @node-selected="openDocFromGraph" />
      </div>

      <div v-show="activeTab === 'archive'">
        <MatrixArchive ref="archiveRef" @archive-changed="refreshGraph" />
      </div>

      <div v-show="activeTab === 'watchers'">
  <AsyncWatchers @watcher-ingested="onWatcherIngested" />
</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch , nextTick } from 'vue';
import IngestionEngine from '@/components/IngestionEngine.vue';
import RetrievalTerminal from '@/components/RetrievalTerminal.vue';
import MatrixArchive from '@/components/MatrixArchive.vue';
import KnowledgeGraph from '@/components/KnowledgeGraph.vue';
import EntityGraph from '@/components/EntityGraph.vue';
import AsyncWatchers from '@/components/AsyncWatchers.vue';

const tabs = [
  { id: 'ingest', label: '_INGEST' },
  { id: 'query', label: '_QUERY' },
  { id: 'map', label: '_NEURAL_MAP' },
  { id: 'archive', label: '_ARCHIVE' },
  { id: 'knowledge', label: '_KNOWLEDGE' },
  { id: 'watchers', label: '_WATCHERS' }
];

const activeTab = ref('ingest');
const archiveRef = ref(null);
const graphRef = ref(null);
const entityGraphRef = ref(null);

const onGraphResult = (payload) => {
  activeTab.value = 'knowledge';
  nextTick(() => {
    if (entityGraphRef.value) {
      entityGraphRef.value.fitView();
      entityGraphRef.value.highlightPath(payload.entities, payload.path);
    }
  });
};
// 3. add a handler — a watcher ingest should refresh archive + both graphs
const onWatcherIngested = () => {
  if (archiveRef.value) archiveRef.value.fetchDocuments();
  if (graphRef.value) graphRef.value.loadGraph();
  if (entityGraphRef.value) entityGraphRef.value.loadGraph();
};

// Refresh graph only
const refreshGraph = () => {
  if (graphRef.value) graphRef.value.loadGraph();
};

// After a new ingest: refresh archive AND graph (both stay mounted thanks to v-show)
const refreshAll = () => {
  if (archiveRef.value) archiveRef.value.fetchDocuments();
  refreshGraph();
};

// Clicking a node on the map jumps to that memory in the Archive
const openDocFromGraph = (docId) => {
  activeTab.value = 'archive';
  if (archiveRef.value) archiveRef.value.focusDoc(docId);
};

// vis-network canvas has zero size while hidden; re-fit when the map tab opens
watch(activeTab, (t) => {
  if (t === 'map' && graphRef.value) graphRef.value.fitView();
});
</script>

<style>
/* GLOBAL FIX: one scroll container only (html), no body override */
html,
body,
#app {
  min-height: 100vh !important;
  height: auto !important;
}

body {
  overflow-x: hidden !important;
}
</style>

<style scoped>
/* Clip the drifting orbs so they can't stretch the page height (moving-scrollbar bug) */
.hero-section {
  overflow: hidden;
}

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

/* Tab bar */
.tab-bar {
  background: rgba(10, 10, 18, 0.7);
  border: 1px solid rgba(0, 210, 255, 0.3);
}

.tab-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  padding: 10px 22px;
  border-radius: 50px;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.tab-btn:hover {
  color: #00d2ff;
}

.tab-btn.active {
  background: linear-gradient(90deg, rgba(0, 210, 255, 0.2), rgba(255, 0, 127, 0.2));
  color: #ffffff;
  border: 1px solid rgba(0, 210, 255, 0.5);
  box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
}

/* Floating Orbs */
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
</style>