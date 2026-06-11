<template>
  <div
    class="input-card glass-panel mx-auto rounded-4 p-4 mt-4 text-start"
    :class="{ fullscreen: isExpanded }"
  >
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h4 class="text-white mb-0 fs-5 font-monospace">_NEURAL_MAP // SEMANTIC_GRAPH</h4>
      <div class="d-flex gap-2">
        <button @click="loadGraph" class="btn btn-sm btn-outline-info rounded-pill px-3 font-monospace">
          {{ isLoading ? 'Mapping...' : 'Re-Map' }}
        </button>
        <button @click="toggleExpand" class="btn btn-sm btn-outline-info rounded-pill px-3 font-monospace">
          {{ isExpanded ? 'Collapse ✕' : 'Expand ⛶' }}
        </button>
      </div>
    </div>

    <div v-if="statusMsg" class="text-info small font-monospace mb-1">{{ statusMsg }}</div>
    <div class="text-secondary small font-monospace mb-2">
      >> Click any node to open that memory in the Archive. Drag to explore.
    </div>

    <div ref="netContainer" class="graph-canvas rounded-3"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { Network } from 'vis-network/standalone';
import api from '@/api';

const emit = defineEmits(['node-selected']);

const netContainer = ref(null);
const isLoading = ref(false);
const isExpanded = ref(false);
const statusMsg = ref('');
let network = null;

const loadGraph = async () => {
  isLoading.value = true;
  statusMsg.value = '>> Computing semantic distances...';
  try {
    let { data } = await api.getGraph(0.55);
    // Auto-relax threshold if the graph has no connections yet
    if (data.edges.length === 0 && data.nodes.length > 1) {
      ({ data } = await api.getGraph(0.45));
    }
    const nodes = data.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      shape: 'dot',
      size: 16,
      color: {
        background: '#0a0a12',
        border: '#00d2ff',
        highlight: { background: '#ff007f', border: '#00d2ff' }
      },
      font: { color: '#ffffff', face: 'monospace', size: 12 }
    }));
    const edges = data.edges.map((e) => ({
      from: e.from,
      to: e.to,
      width: 1 + e.value * 4,
      color: { color: 'rgba(0,210,255,0.35)', highlight: '#ff007f' }
    }));

    if (network) network.destroy();
    network = new Network(
      netContainer.value,
      { nodes, edges },
      {
        edges: { smooth: true },
        physics: { stabilization: true, barnesHut: { gravitationalConstant: -8000, springLength: 140 } },
        interaction: { hover: true }
      }
    );

    // Node click -> tell HomeView to open this memory in the Archive tab
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        emit('node-selected', params.nodes[0]);
      }
    });

    statusMsg.value = `>> ${nodes.length} memories mapped, ${edges.length} neural links detected.`;
  } catch (err) {
    console.error('Graph error:', err);
    statusMsg.value = 'CRITICAL ERROR: Could not map the neural matrix.';
  } finally {
    isLoading.value = false;
  }
};

// Re-fit after the container becomes visible or changes size (tab switch / expand)
const fitView = () => {
  if (network) {
    network.redraw();
    network.fit({ animation: { duration: 400 } });
  }
};

const toggleExpand = async () => {
  isExpanded.value = !isExpanded.value;
  await nextTick();
  setTimeout(fitView, 60); // let the CSS resize land first
};

onMounted(loadGraph);

defineExpose({ loadGraph, fitView });
</script>

<style scoped>
.input-card {
  max-width: 900px;
  border-color: rgba(0, 210, 255, 0.3);
  background: rgba(10, 10, 18, 0.85);
}

/* Fullscreen overlay mode */
.fullscreen {
  position: fixed;
  inset: 2vh 2vw;
  z-index: 1050;
  max-width: none;
  margin: 0 !important;
  box-shadow: 0 0 60px rgba(0, 0, 0, 0.9);
}

.graph-canvas {
  height: 480px;
  background: #050508;
  border: 1px solid rgba(0, 210, 255, 0.2);
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8);
}

.fullscreen .graph-canvas {
  height: calc(96vh - 130px);
}
</style>