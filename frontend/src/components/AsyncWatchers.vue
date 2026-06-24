<template>
  <div class="input-card glass-panel mx-auto rounded-4 p-4 mt-4 text-start">
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <h4 class="text-white mb-0 fs-5 font-monospace">_ASYNC_WATCHERS // AUTONOMOUS_INGESTION</h4>
      <button @click="fetchWatchers" class="btn btn-sm btn-outline-info rounded-pill px-3 font-monospace">Refresh</button>
    </div>

    <p class="text-secondary small font-monospace mb-3">
      >> Background agents poll sources every {{ intervalSec }}s and auto-ingest changed content
      through the full pipeline — chunk · synthesize · graph-extract.
    </p>

    <div class="d-flex gap-2 mb-3 flex-wrap">
      <input v-model="newUrl" placeholder="https://..." class="form-control bg-transparent border-light-subtle text-white custom-input" />
      <input v-model="newLabel" placeholder="label (optional)" class="form-control bg-transparent border-light-subtle text-white custom-input" style="max-width: 200px" />
      <button @click="add" :disabled="!newUrl || adding" class="btn btn-outline-info rounded-pill px-4 font-monospace">
        {{ adding ? 'Adding...' : 'Add Watcher' }}
      </button>
    </div>

    <div class="watcher-list rounded-3">
      <div v-if="loading" class="text-info pulsing-text font-monospace p-3">>> Loading watchers...</div>
      <div v-else-if="!watchers.length" class="text-secondary font-monospace p-3">>> No watchers configured. Add one above.</div>
      <div v-for="w in watchers" :key="w.id" class="watcher-row p-3">
        <div class="d-flex justify-content-between align-items-start gap-2 flex-wrap">
          <div class="flex-grow-1" style="min-width: 0">
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="status-dot" :class="statusClass(w)"></span>
              <span class="text-white fw-bold text-truncate">{{ w.label || w.url }}</span>
              <span v-if="!w.active" class="badge bg-secondary font-monospace">PAUSED</span>
            </div>
            <div class="text-secondary small font-monospace text-truncate">{{ w.url }}</div>
            <div class="text-info small font-monospace mt-1">{{ w.last_status || 'never polled' }} · {{ formatTime(w.last_checked) }}</div>
          </div>
          <div class="d-flex gap-1">
            <button @click="run(w.id)" :disabled="runningId === w.id" class="btn btn-sm btn-outline-info font-monospace">{{ runningId === w.id ? '...' : 'Run' }}</button>
            <button @click="toggle(w.id)" class="btn btn-sm btn-outline-warning font-monospace">{{ w.active ? 'Pause' : 'Resume' }}</button>
            <button @click="remove(w.id)" class="btn btn-sm btn-outline-danger font-monospace">✕</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '@/api';

const emit = defineEmits(['watcher-ingested']);

const watchers = ref([]);
const loading = ref(false);
const adding = ref(false);
const runningId = ref(null);
const newUrl = ref('');
const newLabel = ref('');
const intervalSec = 60;
let pollTimer = null;

const fetchWatchers = async () => {
  loading.value = true;
  try { watchers.value = (await api.listWatchers()).data.watchers; }
  catch (e) { console.error(e); }
  finally { loading.value = false; }
};

const add = async () => {
  adding.value = true;
  try { await api.addWatcher(newUrl.value.trim(), newLabel.value.trim()); newUrl.value=''; newLabel.value=''; await fetchWatchers(); }
  catch (e) { console.error(e); }
  finally { adding.value = false; }
};

const run = async (id) => {
  runningId.value = id;
  try {
    const { data } = await api.runWatcher(id);
    if (data.status === 'ingested') emit('watcher-ingested', data);
    await fetchWatchers();
  } catch (e) { console.error(e); }
  finally { runningId.value = null; }
};

const toggle = async (id) => { await api.toggleWatcher(id); await fetchWatchers(); };
const remove = async (id) => { if (!confirm('Delete this watcher?')) return; await api.deleteWatcher(id); await fetchWatchers(); };

const statusClass = (w) => {
  if (!w.active) return 'dot-paused';
  if (!w.last_status) return 'dot-pending';
  if (w.last_status.startsWith('ok')) return 'dot-ok';
  if (w.last_status === 'unchanged') return 'dot-idle';
  return 'dot-error';
};

const formatTime = (iso) => {
  if (!iso) return 'never';
  const d = new Date(iso), s = Math.floor((Date.now() - d.getTime()) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return d.toLocaleString();
};

onMounted(() => { fetchWatchers(); pollTimer = setInterval(fetchWatchers, 15000); });
onUnmounted(() => clearInterval(pollTimer));
defineExpose({ fetchWatchers });
</script>

<style scoped>
.input-card { max-width: 900px; border-color: rgba(0,210,255,0.3); background: rgba(10,10,18,0.7); }
.custom-input { outline: none !important; box-shadow: none !important; }
.custom-input:focus { border-color: #00d2ff !important; }
.watcher-list { background: rgba(5,5,8,0.6); border: 1px solid rgba(0,210,255,0.2); }
.watcher-row { border-bottom: 1px solid rgba(0,210,255,0.1); }
.watcher-row:last-child { border-bottom: none; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot-ok { background: #27e0a6; box-shadow: 0 0 8px #27e0a6; }
.dot-idle { background: #00d2ff; }
.dot-pending { background: #f3c13a; }
.dot-error { background: #ff007f; box-shadow: 0 0 8px #ff007f; }
.dot-paused { background: #555; }
.pulsing-text { animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>