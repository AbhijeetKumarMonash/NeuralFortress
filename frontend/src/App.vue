<script>
import BHeader from './components/BHeader.vue'

export default {
  name: 'App',
  components: {
    BHeader
  }
}
</script>

<template>
  <div class="app-wrapper animated-bg">
    <BHeader />
    <main class="main-content z-10 relative">
      <router-view></router-view>
    </main>
  </div>
</template>

<style>
body,
html {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  color: #ffffff;
}

/* Deep, dark animated background for maximum contrast */
.animated-bg {
  min-height: 100vh;
  background: linear-gradient(-45deg, #050510, #130b29, #1a103c, #0a0a1a);
  background-size: 400% 400%;
  animation: gradientBG 20s ease infinite;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Glassmorphism */
.glass-panel {
  background: rgba(15, 15, 25, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.6);
}
</style>
