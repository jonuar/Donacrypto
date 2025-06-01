<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'App',
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
</style>
