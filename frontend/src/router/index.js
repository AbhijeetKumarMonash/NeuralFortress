import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'About',
    component: AboutView
  }
]

const router = createRouter({
  // Note: For Vite, use import.meta.env.BASE_URL instead of process.env.BASE_URL
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
