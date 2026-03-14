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
            class="custom-textarea form-control bg-transparent border-0 shadow-none fs-5 text-white"
            placeholder="Drop your scattered thoughts, project links, or raw data here..."
            rows="5"
          ></textarea>
        </div>

        <div class="d-flex justify-content-between align-items-center p-3 rounded-bottom mt-2">
          <span class="text-info small font-monospace"
            ><i class="bi bi-cpu me-1"></i> AI Summarization Active</span
          >
          <button class="btn-action">Initialize Upload</button>
        </div>
      </div>
    </div>
  </div>
</template>

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
</style>
