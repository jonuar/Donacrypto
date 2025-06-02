<template>
  <div id="app">
    <nav class="app-nav" v-if="usuario">
      <div class="nav-content">
        <router-link to="/" class="nav-brand">
          <span class="brand-icon">💜</span>
          <span class="brand-text">DonaCrypto</span>
        </router-link>
        <div class="nav-links">
          <router-link v-if="usuario.role === 'creator' && route.path !== '/dashboard'" to="/dashboard" class="btn btn-primary btn-sm">Dashboard</router-link>
          
          <!-- Navigation for followers -->
          <template v-if="usuario.role === 'follower'">
            <router-link to="/feed" class="nav-link" :class="{ 'active': route.path === '/feed' }">
              🏠 Feed
            </router-link>
            <router-link to="/explore" class="nav-link" :class="{ 'active': route.path === '/explore' }">
              🔍 Explorar
            </router-link>
            <router-link to="/profile" class="nav-link" :class="{ 'active': route.path === '/profile' }">
              👤 Perfil
            </router-link>
          </template>
          
          <button @click="logout" class="btn btn-ghost btn-sm">Cerrar Sesión</button>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const route = useRoute()
    
    const usuario = computed(() => authStore.usuarioActual)
    
    const logout = async () => {
      await authStore.cerrarSesion()
      router.push('/')
    }
    
    return {
      usuario,
      logout,
      route
    }
  },
  async created() {
    // Inicializar autenticación al cargar la app
    const authStore = useAuthStore()
    await authStore.inicializar()
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  width: 100%;
}

.app-nav {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-md) 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
  text-decoration: none;
}

.brand-icon {
  font-size: var(--font-size-xl);
}

.brand-text {
  color: var(--color-primary);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.nav-link {
  color: var(--color-text);
  text-decoration: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: var(--color-surface-alt);
}

.nav-link.active {
  background-color: var(--color-primary);
  color: white;
  font-weight: 600;
}

@media (max-width: 768px) {
  .nav-content {
    padding: 0 var(--spacing-md);
  }
  
  .nav-links {
    gap: var(--spacing-sm);
  }
  
  .nav-link {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
}
</style>
