<template>
  <div class="about-section flex-grow-1 py-5">
    <div class="container position-relative z-10" style="max-width: 1100px">
      <div class="text-center mb-5 pb-4 border-bottom border-secondary">
        <h1 class="fw-black text-white display-3 mb-4 text-shadow">
          The Genesis of NeuralFortress
        </h1>
        <p class="lead text-info fw-bold fs-4">
          We are not building a digital filing cabinet. We are engineering a cognitive extension.
        </p>
      </div>

      <div
        class="row mb-5 pb-5 align-items-center g-5 border-bottom border-secondary border-opacity-50"
      >
        <div class="col-lg-6">
          <h2 class="fw-bold text-gradient mb-4">The Cognitive Bottleneck</h2>
          <p class="text-white opacity-75 fs-5 lh-base mb-4">
            The modern intellect is under siege. Every day, we consume research papers,
            architectural diagrams, brilliant fragmented thoughts, and complex code snippets. The
            traditional response has been to manually sort this data into hierarchical folders.
          </p>
          <p class="text-white opacity-75 fs-5 lh-base mb-4">
            <strong>Why is this a problem?</strong> Folders require a rigid taxonomy. They rely on
            human memory to retrieve information months later. When you need to connect a specific
            configuration step you read in February with a deployment issue you face in October, a
            search bar looking for exact keywords fails you.
          </p>
        </div>
        <div class="col-lg-6">
          <div
            class="glass-panel p-2 rounded-4 image-container shadow-lg text-center position-relative overflow-hidden"
          >
            <div class="image-overlay"></div>
            <img
              src="../assets/images/Gemini_Generated_Image_8b4yp18b4yp18b4y.png"
              alt="Neural Network Concept"
              class="img-fluid rounded-3 w-100"
              style="min-height: 450px; object-fit: cover"
            />
          </div>
        </div>
      </div>

      <div class="row mb-5 pb-5 g-5 border-bottom border-secondary border-opacity-50">
        <div class="col-12 text-center mb-4">
          <h2 class="fw-bold text-gradient">The NeuralFortress Paradigm</h2>
        </div>

        <div class="col-md-6">
          <div class="glass-panel p-5 h-100 rounded-4">
            <h3 class="text-white fw-bold mb-4">
              <i class="bi bi-cpu text-info me-2"></i>What It Does
            </h3>
            <p class="text-white opacity-75 fs-5 lh-base mb-3">
              NeuralFortress is an Agentic Personal Knowledge Management System (PKMS). You simply
              drop raw, unformatted text, URLs, or code into the system.
            </p>
            <ul class="text-white opacity-75 fs-5 lh-base ps-3">
              <li class="mb-2">
                <strong>Autonomous Ingestion:</strong> Background AI reads and summarizes the data.
              </li>
              <li class="mb-2">
                <strong>Semantic Embedding:</strong> It converts text into high-dimensional vectors
                (math).
              </li>
              <li class="mb-2">
                <strong>RAG Retrieval:</strong> You chat with the system. It searches your vectors
                and generates precise answers based <em>only</em> on your past data.
              </li>
            </ul>
          </div>
        </div>

        <div class="col-md-6">
          <div class="glass-panel p-5 h-100 rounded-4">
            <h3 class="text-white fw-bold mb-4">
              <i class="bi bi-shield-check text-info me-2"></i>Why It Is Required
            </h3>
            <p class="text-white opacity-75 fs-5 lh-base mb-3">
              Human capital should be spent on synthesis, not sorting.
            </p>
            <p class="text-white opacity-75 fs-5 lh-base">
              You are building quantum computing roadmaps, studying for AWS certifications, and
              deploying Docker containers. The sheer volume of technical syntax is impossible to
              memorize. NeuralFortress acts as a secure, infallible "Second Brain" that scales
              infinitely with your ambitions. It eliminates friction between learning and recalling.
            </p>
          </div>
        </div>
      </div>

      <div class="mb-5 pb-5 border-bottom border-secondary border-opacity-50 text-center">
        <h2 class="fw-bold text-gradient mb-5">Architecture & Data Flow</h2>
        <div class="glass-panel rounded-4 p-5 text-center position-relative overflow-hidden">
          <svg
            class="w-100"
            height="200"
            viewBox="0 0 1000 200"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect
              x="50"
              y="70"
              width="160"
              height="60"
              rx="8"
              fill="rgba(255,255,255,0.05)"
              stroke="#00D2FF"
              stroke-width="2"
            />
            <text
              x="130"
              y="105"
              fill="white"
              font-size="16"
              font-family="monospace"
              text-anchor="middle"
            >
              1. Raw Input
            </text>

            <rect
              x="420"
              y="50"
              width="160"
              height="100"
              rx="8"
              fill="rgba(255, 0, 127, 0.15)"
              stroke="#FF007F"
              stroke-width="2"
            />
            <text
              x="500"
              y="95"
              fill="white"
              font-size="18"
              font-weight="bold"
              text-anchor="middle"
            >
              AI AGENT
            </text>
            <text
              x="500"
              y="120"
              fill="rgba(255,255,255,0.7)"
              font-size="12"
              font-family="monospace"
              text-anchor="middle"
            >
              Summarize & Embed
            </text>

            <rect
              x="790"
              y="70"
              width="160"
              height="60"
              rx="8"
              fill="rgba(255,255,255,0.05)"
              stroke="#00D2FF"
              stroke-width="2"
            />
            <text
              x="870"
              y="105"
              fill="white"
              font-size="16"
              font-family="monospace"
              text-anchor="middle"
            >
              3. pgvector DB
            </text>

            <path
              class="animated-path"
              d="M210 100 L420 100"
              stroke="#00D2FF"
              stroke-width="3"
              stroke-dasharray="10 5"
            />
            <path
              class="animated-path"
              d="M580 100 L790 100"
              stroke="#FF007F"
              stroke-width="3"
              stroke-dasharray="10 5"
            />

            <circle cx="0" cy="100" r="6" fill="#FFF">
              <animate attributeName="cx" from="210" to="420" dur="2s" repeatCount="indefinite" />
            </circle>
            <circle cx="0" cy="100" r="6" fill="#FFF">
              <animate attributeName="cx" from="580" to="790" dur="2s" repeatCount="indefinite" />
            </circle>
          </svg>
        </div>
      </div>

      <div class="mb-5 text-center">
        <h2 class="fw-bold text-gradient mb-5">Operational Use Cases</h2>

        <div class="carousel-container mx-auto" style="max-width: 800px">
          <div
            class="glass-panel rounded-4 p-5 position-relative overflow-hidden"
            style="min-height: 350px"
          >
            <transition name="fade" mode="out-in">
              <div :key="currentSlide" class="carousel-content text-start">
                <div class="d-flex align-items-center mb-4">
                  <div class="icon-box me-3" v-html="slides[currentSlide].icon"></div>
                  <h3 class="fw-bold text-white m-0">{{ slides[currentSlide].title }}</h3>
                </div>

                <p class="text-white opacity-75 fs-5 lh-base mb-3">
                  <strong class="text-info">The Action:</strong> {{ slides[currentSlide].action }}
                </p>
                <p class="text-white opacity-75 fs-5 lh-base m-0">
                  <strong class="text-pink">The Magic:</strong> {{ slides[currentSlide].magic }}
                </p>
              </div>
            </transition>

            <div
              class="carousel-controls d-flex justify-content-between position-absolute w-100 px-4"
              style="top: 50%; left: 0; transform: translateY(-50%)"
            >
              <button @click="prevSlide" class="carousel-btn">
                <i class="bi bi-chevron-left"></i> ❮
              </button>
              <button @click="nextSlide" class="carousel-btn">
                ❯ <i class="bi bi-chevron-right"></i>
              </button>
            </div>

            <div
              class="carousel-indicators d-flex justify-content-center position-absolute w-100"
              style="bottom: 20px; left: 0"
            >
              <span
                v-for="(slide, index) in slides"
                :key="index"
                @click="goToSlide(index)"
                class="indicator-dot"
                :class="{ active: currentSlide === index }"
              ></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const currentSlide = ref(0)
let slideInterval = null

const slides = [
  {
    title: 'The Cloud Architect',
    icon: `<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#00D2FF" stroke-width="2"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path></svg>`,
    action:
      'You dump raw AWS whitepapers, Nginx proxy configurations, and Docker deployment logs directly into NeuralFortress without organizing them into folders.',
    magic:
      "Months later, you ask the system, 'How did I route traffic for that containerized CRUD app?' The RAG engine instantly synthesizes a step-by-step architectural breakdown using strictly your past configurations."
  },
  {
    title: 'The Deep Tech Researcher',
    icon: `<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#FF007F" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="14.31" y1="8" x2="20.05" y2="17.94"></line><line x1="9.69" y1="8" x2="21.17" y2="8"></line><line x1="7.38" y1="12" x2="13.12" y2="2.06"></line><line x1="9.69" y1="16" x2="3.95" y2="6.06"></line><line x1="14.31" y1="16" x2="2.83" y2="16"></line><line x1="16.62" y1="12" x2="10.88" y2="21.94"></line></svg>`,
    action:
      'You feed the system complex academic papers on Qiskit, quantum circuit optimization, and C++ performance limits.',
    magic:
      "Because the system understands semantics rather than just keywords, you can query: 'Find the synergies between agentic AI loops and quantum algorithms in my notes.' It maps the conceptual overlap for you."
  },
  {
    title: 'The Full-Stack Developer',
    icon: `<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#00D2FF" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>`,
    action:
      'You paste messy Vue.js boilerplate code, random FastAPI snippets, and bugs you solved on StackOverflow into the omni-input box.',
    magic:
      "Instead of searching through old GitHub repos, you ask 'Give me the boilerplate for my standard Vue 3 API call.' NeuralFortress hands you your exact, formatted code snippet instantly."
  }
]

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % slides.length
}

const prevSlide = () => {
  currentSlide.value = (currentSlide.value - 1 + slides.length) % slides.length
}

const goToSlide = (index) => {
  currentSlide.value = index
}

// Auto-play the carousel
onMounted(() => {
  slideInterval = setInterval(nextSlide, 8000) // Change slide every 8 seconds
})

onUnmounted(() => {
  clearInterval(slideInterval)
})
</script>

<style scoped>
.fw-black {
  font-weight: 900;
  letter-spacing: -1px;
}
.text-shadow {
  text-shadow: 0 5px 20px rgba(0, 0, 0, 0.8);
}
.text-gradient {
  background: -webkit-linear-gradient(0deg, #00d2ff, #ff007f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.lh-base {
  line-height: 1.8 !important;
}
.text-pink {
  color: #ff007f;
}

/* Image Container */
.image-container {
  border: 1px solid rgba(0, 210, 255, 0.3);
}
.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 0, 127, 0.2), rgba(0, 210, 255, 0.2));
  pointer-events: none;
  border-radius: inherit;
}

/* Flowchart Animation */
.animated-path {
  animation: flowLine 2s linear infinite;
}
@keyframes flowLine {
  to {
    stroke-dashoffset: -30;
  }
}

/* Carousel Custom Styling */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.5s ease,
    transform 0.5s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.carousel-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}
.carousel-btn:hover {
  background: rgba(0, 210, 255, 0.4);
  transform: scale(1.1);
}

.indicator-dot {
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  margin: 0 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.indicator-dot.active {
  background: #00d2ff;
  box-shadow: 0 0 10px #00d2ff;
  transform: scale(1.3);
}
</style>
