import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Vistas principales
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'

// Vistas del Creator
import CreatorDashboard from '@/views/creator/DashboardView.vue'
import CreatorProfile from '@/views/creator/ProfileView.vue'

// Vistas del Follower
import FollowerFeed from '@/views/follower/FeedView.vue'
import ExploreCreators from '@/views/follower/ExploreView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { requiresGuest: true }
    },
    
    // Rutas del Creator
    {
      path: '/creator/dashboard',
      name: 'creator-dashboard',
      component: CreatorDashboard,
      meta: { requiresAuth: true, role: 'creator' }
    },
    {
      path: '/creator/profile',
      name: 'creator-profile',
      component: CreatorProfile,
      meta: { requiresAuth: true, role: 'creator' }
    },
    
    // Rutas del Follower
    {
      path: '/feed',
      name: 'follower-feed',
      component: FollowerFeed,
      meta: { requiresAuth: true, role: 'follower' }
    },
    {
      path: '/explore',
      name: 'explore-creators',
      component: ExploreCreators,
      meta: { requiresAuth: true, role: 'follower' }
    }
  ]
})

// Guards de navegación
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Inicializar store si hay token
  if (!authStore.isAuthenticated && authStore.token) {
    await authStore.initialize()
  }
  
  const requiresAuth = to.meta.requiresAuth
  const requiresGuest = to.meta.requiresGuest
  const requiredRole = to.meta.role
  
  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (requiresGuest && authStore.isAuthenticated) {
    // Redirigir según el rol
    const redirectPath = authStore.isCreator ? '/creator/dashboard' : '/feed'
    next(redirectPath)
  } else if (requiredRole && authStore.userRole !== requiredRole) {
    // Rol incorrecto
    next('/')
  } else {
    next()
  }
})

export default router
