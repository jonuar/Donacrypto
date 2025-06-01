import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Vistas principales
import HomeView from '@/views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { requiresGuest: true }
    }
  ]
})

// Guards de navegación
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Inicializar store si hay token
  if (!authStore.estaAutenticado && authStore.tokenAcceso) {
    await authStore.inicializar()
  }
  
  const requiresAuth = to.meta.requiresAuth
  const requiresGuest = to.meta.requiresGuest
  
  if (requiresAuth && !authStore.estaAutenticado) {
    next('/login')
  } else if (requiresGuest && authStore.estaAutenticado) {
    // Redirigir a home si ya está autenticado
    next('/')
  } else {
    next()
  }
})

export default router
