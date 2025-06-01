<template>
  <div id="app">
    <nav class="app-nav" v-if="usuario">
      <div class="nav-content">
        <router-link to="/" class="nav-brand">DonaCrypto</router-link>
        <div class="nav-links">
          <router-link v-if="usuario.role === 'creator'" to="/dashboard" class="nav-link">Dashboard</router-link>
          <router-link v-if="usuario.role === 'follower'" to="/feed" class="nav-link">Feed</router-link>
          <button @click="logout" class="btn btn-outline btn-sm">Cerrar Sesión</button>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    
    const usuario = computed(() => authStore.usuarioActual)
    
    const logout = async () => {
      await authStore.logout()
      router.push('/login')
    }
    
    return {
      usuario,
      logout
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
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
  text-decoration: none;
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
  
  &:hover {
    background: var(--color-background);
  }
  
  &.router-link-active {
    background: var(--color-primary);
    color: white;
  }
}
</style>
