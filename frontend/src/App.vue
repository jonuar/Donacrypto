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
    await authStore.initialize()
  }
}
</script>

<style lang="scss" scoped>
// Estilos globales
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: #f8fafc;
}

#app {
  min-height: 100vh;
}
</style>
