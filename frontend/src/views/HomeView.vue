<template>
  <div class="hero-section flex-grow-1 d-flex flex-column py-5 position-relative">
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

      <IngestionEngine @document-ingested="refreshArchive" />
      
      <RetrievalTerminal />
      
      <MatrixArchive ref="archiveRef" />

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import IngestionEngine from '@/components/IngestionEngine.vue';
import RetrievalTerminal from '@/components/RetrievalTerminal.vue';
import MatrixArchive from '@/components/MatrixArchive.vue';

const archiveRef = ref(null);

// When IngestionEngine says a document is saved, tell MatrixArchive to fetch the new list
const refreshArchive = () => {
  if (archiveRef.value) {
    archiveRef.value.fetchDocuments();
  }
};
</script>

<style>
/* GLOBAL SCROLLBAR FIX */
html, body, #app {
  min-height: 100vh !important;
  height: auto !important;
}

body {
  overflow-y: auto !important;
  overflow-x: hidden !important;
}
</style>

<style scoped>
/* Only the Hero-specific styles remain here */
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
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(100px, 150px) scale(1.2); }
}
</style>