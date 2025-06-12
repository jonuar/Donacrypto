import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NotFound from '@/views/NotFound.vue'

// Vistas principales
import HomeView from '@/views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/creator/CreatorDashboard.vue'),
      meta: { requiresAuth: true, role: 'creator' },
    },
    {
      path: '/creator/:username',
      name: 'creator-profile',
      component: () => import('@/views/creator/CreatorPublicProfile.vue'),
      props: true,
    },
    {
      path: '/feed',
      name: 'feed',
      component: () => import('@/views/follower/FollowerFeed.vue'),
      meta: { requiresAuth: true, role: 'follower' },
    },
    {
      path: '/profile',
      name: 'follower-profile',
      component: () => import('@/views/follower/FollowerProfile.vue'),
      meta: { requiresAuth: true, role: 'follower' },
    },
    {
      path: '/explore',
      name: 'explore-creators',
      component: () => import('@/views/follower/ExploreCreators.vue'),
      meta: { requiresAuth: true, role: 'follower' },
    },
    {
      path: '/creators',
      name: 'following-creators',
      component: () => import('@/views/follower/ExploreCreators.vue'),
      meta: { requiresAuth: true, role: 'follower' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFound,
    },
  ],
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
  const requiredRole = to.meta.role

  if (requiresAuth && !authStore.estaAutenticado) {
    next('/login')
  } else if (requiresGuest && authStore.estaAutenticado) {
    // Redirigir a home si ya está autenticado
    next('/')
  } else if (requiredRole && authStore.usuarioActual?.role !== requiredRole) {
    // Verificar rol específico
    next('/')
  } else {
    next()
  }
})

export default router
