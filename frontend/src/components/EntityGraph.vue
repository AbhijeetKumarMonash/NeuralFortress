<template>
  <div class="input-card glass-panel mx-auto rounded-4 p-4 mt-4 text-start"
       :class="{ fullscreen: isExpanded }">
    <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
      <h4 class="text-white mb-0 fs-5 font-monospace">_KNOWLEDGE_GRAPH // ENTITIES</h4>
      <div class="d-flex gap-2">
        <button @click="loadGraph" class="btn btn-sm btn-outline-info rounded-pill px-3 font-monospace">
          {{ isLoading ? 'Building...' : 'Rebuild' }}
        </button>
        <button @click="toggleExpand" class="btn btn-sm btn-outline-info rounded-pill px-3 font-monospace">
          {{ isExpanded ? 'Collapse ✕' : 'Expand ⛶' }}
        </button>
      </div>
    </div>

    <div v-if="statusMsg" class="text-info small font-monospace mb-1">{{ statusMsg }}</div>
    <div class="d-flex flex-wrap gap-3 mb-2">
      <span v-for="(c, t) in legend" :key="t" class="small font-monospace" :style="{ color: c }">
        ● {{ t }}
      </span>
    </div>

    <div ref="netContainer" class="graph-canvas rounded-3"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { Network } from 'vis-network/standalone';
import api from '@/api';

const netContainer = ref(null);
const isLoading = ref(false);
const isExpanded = ref(false);
const statusMsg = ref('');
let network = null;
let baseNodes = [];
let baseEdges = [];

const legend = {
  PERSON: '#FF007F', TECHNOLOGY: '#00D2FF', CONCEPT: '#27E0A6',
  ORG: '#FFB000', EVENT: '#FF6B6B', PLACE: '#9B6BFF', OTHER: '#9AA2B8'
};

const loadGraph = async () => {
  isLoading.value = true;
  statusMsg.value = '>> Extracting entity network...';
  try {
    const { data } = await api.getKnowledgeGraph();
    baseNodes = data.nodes.map(n => ({
      id: n.id, label: n.label, group: n.group,
      shape: 'dot', size: 15,
      color: { background: n.color, border: n.color, highlight: { background: '#FFFFFF', border: n.color } },
      font: { color: '#ffffff', face: 'monospace', size: 11 }
    }));
    baseEdges = data.edges.map((e, i) => ({
      id: 'e' + i, from: e.from, to: e.to, label: e.label,
      arrows: 'to',
      color: { color: 'rgba(0,210,255,0.25)', highlight: '#ff007f' },
      font: { color: '#7f8caa', size: 9, strokeWidth: 0, face: 'monospace' },
      width: 1
    }));
    render();
    statusMsg.value = `>> ${data.entity_count} entities, ${data.relationship_count} relationships mapped.`;
  } catch (err) {
    console.error('Knowledge graph error:', err);
    statusMsg.value = 'CRITICAL ERROR: Could not build the knowledge graph.';
  } finally {
    isLoading.value = false;
  }
};

const render = () => {
  if (network) network.destroy();
  network = new Network(netContainer.value,
    { nodes: baseNodes, edges: baseEdges },
    {
      edges: { smooth: { type: 'dynamic' } },
      physics: { stabilization: true, barnesHut: { gravitationalConstant: -9000, springLength: 160 } },
      interaction: { hover: true, tooltipDelay: 100 }
    });
};

// Called by parent after a GraphRAG query: light up the path entities + edges
const highlightPath = (pathEntityNames, pathPairs) => {
  const nameSet = new Set(pathEntityNames.map(n => n.toLowerCase()));
  baseNodes.forEach(n => {
    const on = nameSet.has(n.label.toLowerCase());
    n.size = on ? 24 : 10;
    n.font = { ...n.font, color: on ? '#ffffff' : '#5a6178' };
    n.borderWidth = on ? 3 : 1;
  });
  const pairSet = new Set(pathPairs.map(p => `${p.from.toLowerCase()}|${p.to.toLowerCase()}`));
  const nodeById = Object.fromEntries(baseNodes.map(n => [n.id, n.label.toLowerCase()]));
  baseEdges.forEach(e => {
    const key = `${nodeById[e.from]}|${nodeById[e.to]}`;
    const on = pairSet.has(key);
    e.color = on ? { color: '#ff007f', highlight: '#ff007f' } : { color: 'rgba(90,97,120,0.15)' };
    e.width = on ? 3 : 1;
    e.font = { ...e.font, color: on ? '#ff007f' : '#3a3f52' };
  });
  render();
};

const fitView = () => { if (network) { network.redraw(); network.fit({ animation: { duration: 400 } }); } };

const toggleExpand = async () => {
  isExpanded.value = !isExpanded.value;
  await nextTick();
  setTimeout(fitView, 60);
};

onMounted(loadGraph);
defineExpose({ loadGraph, highlightPath, fitView });
</script>

<style scoped>
.input-card { max-width: 900px; border-color: rgba(0,210,255,0.3); background: rgba(10,10,18,0.85); }
.fullscreen { position: fixed; inset: 2vh 2vw; z-index: 1050; max-width: none; margin: 0 !important; box-shadow: 0 0 60px rgba(0,0,0,0.9); }
.graph-canvas { height: 480px; background: #050508; border: 1px solid rgba(0,210,255,0.2); box-shadow: inset 0 0 20px rgba(0,0,0,0.8); }
.fullscreen .graph-canvas { height: calc(96vh - 150px); }
</style>