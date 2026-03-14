<template>
  <header class="glass-header sticky-top">
    <div class="container d-flex justify-content-between align-items-center py-3">
      <div class="brand d-flex align-items-center">
        <div class="brand-icon-animated">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#00D2FF"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polygon points="12 2 2 22 12 17 22 22 12 2"></polygon>
          </svg>
        </div>
        <span class="brand-text ms-2 fw-bolder fs-4 text-white tracking-wide">NeuralFortress</span>
      </div>

      <ul class="nav">
        <li class="nav-item">
          <router-link to="/" class="nav-link text-light fw-bold" active-class="active-nav"
            >Home</router-link
          >
        </li>
        <li class="nav-item">
          <router-link to="/about" class="nav-link text-light fw-bold" active-class="active-nav"
            >Our Story</router-link
          >
        </li>
      </ul>
    </div>
  </header>
</template>

<style scoped>
.glass-header {
  background: rgba(10, 5, 30, 0.4);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 50;
}

.tracking-wide {
  letter-spacing: 1px;
}

.brand-icon-animated {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
    drop-shadow: 0 5px 15px rgba(0, 210, 255, 0.6);
  }
  100% {
    transform: translateY(0px);
  }
}

.nav-link {
  transition: all 0.3s ease;
  opacity: 0.8;
}
.nav-link:hover {
  opacity: 1;
  transform: translateY(-2px);
  color: #00d2ff !important;
}
.active-nav {
  opacity: 1;
  color: #00d2ff !important;
  border-bottom: 2px solid #00d2ff;
}
</style>
