<template>
  <div class="explore-creators">
    <div class="explore-header">
      <div class="header-content">
        <h1 class="page-title">Descrubir Creadores</h1>
        <p class="page-subtitle">Sigue a nuevos creadores de contenido</p>
      </div>
    </div>    <!-- Sección de búsqueda y filtros -->
    <div class="search-section">
      <div class="search-container">        <!-- Barra de búsqueda de creadores -->
        <div class="search-bar">
          <div class="search-input-group">            <input
              v-model="terminoBusqueda"
              @keyup.enter="buscarCreadores"
              type="text"
              placeholder="Escribe el usuario aquí..."
              class="search-input"
            />
            <button @click="buscarCreadores" class="search-btn">Buscar</button>
          </div>          <small v-if="terminoBusqueda" class="search-help">
            Presiona Enter o haz clic en "Buscar" para iniciar la búsqueda
          </small>
        </div>
        
        <!-- Pestañas de filtrado por modo de vista -->
        <div class="filter-tabs">          <button 
            @click="cambiarModo('explorar')" 
            :class="['tab-btn', { active: modo === 'explorar' }]"
          >
            Explorar Todos
          </button>
          <button 
            @click="cambiarModo('siguiendo')" 
            :class="['tab-btn', { active: modo === 'siguiendo' }]"
          >
            Siguiendo ({{ totalSiguiendo }})
          </button></div>        <!-- Opciones de ordenamiento (Modo explorar) -->
        <div v-if="modo === 'explorar'" class="sort-options">
          <label class="sort-label">Ordenar por:</label>          <select v-model="ordenActual" @change="() => cargarCreadores(1)" class="sort-select">
            <option value="popular">Más populares</option>
            <option value="recent">Más recientes</option>
            <option value="alphabetical">A-Z</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="cargandoCreadores" class="loading-container">
      <div class="loading-spinner"></div>
      <p>{{ mensajeCarga }}</p>    </div>

    <!-- Estados vacíos cuando no hay resultados -->
    <div v-else-if="creadores.length === 0" class="empty-state">      <div class="empty-icon">
        {{ modo === 'busqueda' ? '🔍' : modo === 'siguiendo' ? '👥' : '⭐' }}
      </div>
      <h2>{{ mensajeVacio }}</h2>
      <p>{{ descripcionVacio }}</p>
        <div v-if="modo === 'siguiendo'" class="empty-actions">
        <button @click="cambiarModo('explorar')" class="btn btn-primary">
          Explorar Creadores
        </button>
      </div></div>

    <!-- Cuadrícula de creadores -->
    <div v-else class="creators-content">
      <div class="creators-grid">
        <div 
          v-for="creador in creadores" 
          :key="creador.username || creador.email"
aje de          class="creator-card"        >          <!-- Avatar e información del creador -->
          <div class="creator-header">
            <router-link :to="`/creator/${creador.username}`" class="creator-avatar-link">
              <div class="creator-avatar">
                <img 
                  v-if="creador.avatar_url" 
                  :src="creador.avatar_url" 
                  :alt="creador.username"
                  class="avatar-image"
                />
                <div v-else class="avatar-placeholder">
                  {{ creador.username ? creador.username.charAt(0).toUpperCase() : '👤' }}
                </div>
              </div>
            </router-link>
            
            <div class="creator-info">
              <router-link :to="`/creator/${creador.username}`" class="creator-name-link">
                <h3 class="creator-name">{{ creador.username }}</h3>
              </router-link>
              <p v-if="creador.bio" class="creator-bio">{{ creador.bio }}</p>              <div class="creator-stats">
                <span class="stat">
                  {{ creador.followers_count || 0 }} seguidores
                </span>
                <span class="stat">
                  {{ creador.posts_count || 0 }} posts
                </span>
              </div>
            </div>          </div>          <!-- Acciones del creador -->
          <div class="creator-actions">
            <button 
              v-if="!creador.following"
              @click="seguirCreador(creador)"
              :disabled="procesandoSeguimiento[creador.username]"
              class="btn btn-primary btn-sm"
            >
              <span v-if="procesandoSeguimiento[creador.username]">...</span>
              <span v-else>Seguir</span>
            </button>
            
            <button 
              v-else
              @click="dejarDeSeguir(creador)"
              :disabled="procesandoSeguimiento[creador.username]"
              class="btn btn-secondary btn-sm"
            >
              <span v-if="procesandoSeguimiento[creador.username]">Dejando de seguir...</span>
              <span v-else>Siguiendo</span>
            </button>
          </div></div>
      </div>

      <!-- Paginación -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="cambiarPagina(paginaActual - 1)"
          :disabled="paginaActual <= 1"
          class="pagination-btn"
        >
          ← Anterior
        </button>
        
        <div class="pagination-info">
          Página {{ paginaActual }} de {{ totalPages }}
        </div>
        
        <button 
          @click="cambiarPagina(paginaActual + 1)"
          :disabled="paginaActual >= totalPages"
          class="pagination-btn"
        >
          Siguiente →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

const router = useRouter()
const toast = useToast()

// Configuración de datos reactivos
const cargandoCreadores = ref(false)
const modo = ref('explorar') // Modos disponibles: 'explorar', 'siguiendo', 'busqueda'
const terminoBusqueda = ref('')
const ordenActual = ref('popular')

// Datos de creadores y paginación
const creadores = ref([])
const paginaActual = ref(1)
const totalPages = ref(1)
const totalCreadores = ref(0)
const totalSiguiendo = ref(0)

// Control de estados de procesamiento para evitar clics múltiples
const procesandoSeguimiento = reactive({})

// Configuración de paginación
const creadoresPorPagina = 12

// Propiedades computadas para mensajes dinámicos
const mensajeCarga = computed(() => {
  switch (modo.value) {
    case 'busqueda':
      return `Buscando creadores que coincidan con "${terminoBusqueda.value}"...`
    case 'siguiendo':
      return 'Cargando creadores que sigues...'
    default:
      return 'Explorando creadores disponibles...'
  }
})

const mensajeVacio = computed(() => {
  switch (modo.value) {
    case 'busqueda':
      return 'Sin resultados'
    case 'siguiendo':
      return 'No sigues a ningún creador'
    default:
      return 'No hay creadores disponibles'
  }
})

const descripcionVacio = computed(() => {
  switch (modo.value) {
    case 'busqueda':
      return `No se encontraron creadores que coincidan con "${terminoBusqueda.value}". Intenta con otro término de búsqueda.`
    case 'siguiendo':
      return 'Aún no sigues a ningún creador. ¡Explora y encuentra creadores increíbles para seguir!'
    default:
      return 'No hay creadores registrados en la plataforma en este momento.'
  }
})

// Métodos principales
const cargarCreadores = async (pagina = 1) => {
  cargandoCreadores.value = true
  
  try {
    let endpoint = ''
    let params = {
      page: pagina,
      limit: creadoresPorPagina
    }
    
    // Determinar endpoint y parámetros según el modo actual
    switch (modo.value) {
      case 'explorar':
        endpoint = '/user/explore-all-creators'
        params.sort = ordenActual.value
        break
        
      case 'siguiendo':
        endpoint = '/user/creators-list'
        params.sort = 'recent'
        break
        
      case 'busqueda':
        endpoint = '/user/search-creators'
        params.q = terminoBusqueda.value
        break
    }    const response = await api.get(endpoint, { params })
    
    creadores.value = response.data.creators || []
    paginaActual.value = response.data.page || 1
    totalPages.value = response.data.pages || 1
    totalCreadores.value = response.data.total || 0  } catch (error) {
    console.error('Error al cargar creadores:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        params: error.config?.params
      }
    })
    
    // Redireccionar a login si no está autenticado
    if (error.response?.status === 401) {
      router.push('/login')
      return
    }
    
    // Solo mostrar error toast si es un error real del servidor (no simplemente sin resultados)
    if (error.response?.status !== 404) {
      toast.error('No se pudieron cargar los creadores')
    }
    
    creadores.value = []
  } finally {
    cargandoCreadores.value = false
  }
}

// Cargar estadísticas de cuántos creadores sigue el usuario
const cargarEstadisticasSeguimiento = async () => {
  try {
    const response = await api.get('/user/following')
    totalSiguiendo.value = response.data.count || 0
  } catch (error) {
    console.error('Error al cargar estadísticas de seguimiento:', error)
  }
}

const cambiarModo = async (nuevoModo) => {
  modo.value = nuevoModo
  paginaActual.value = 1
  await cargarCreadores(1)
}

const buscarCreadores = async () => {
  if (!terminoBusqueda.value.trim()) {
    return
  }
  
  if (terminoBusqueda.value.trim().length < 5) {
    toast.info('La búsqueda debe tener al menos 5 caracteres')
    return
  }
  
  modo.value = 'busqueda'
  paginaActual.value = 1
  await cargarCreadores(1)
}

const cambiarPagina = async (nuevaPagina) => {
  if (nuevaPagina >= 1 && nuevaPagina <= totalPages.value && nuevaPagina !== paginaActual.value) {
    await cargarCreadores(nuevaPagina)
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const seguirCreador = async (creador) => {
  const username = creador.username
  procesandoSeguimiento[username] = true
  
  try {
     await api.post('/user/follow', {
      creator_username: username  // ✅ Usar username
    })
    
    // Actualizar estado local
    creador.following = true
    creador.followers_count = (creador.followers_count || 0) + 1
    totalSiguiendo.value += 1
    
    toast.success(`Ahora sigues a ${username}`)
    
  } catch (error) {
    console.error('Error al seguir creador:', error)
    
    if (error.response?.status === 401) {
      router.push('/login')
      return
    }
      const mensaje = error.response?.data?.error || 'Error al seguir al creador'
    toast.error(`${mensaje}`)
  } finally {
    procesandoSeguimiento[username] = false
  }
}

const dejarDeSeguir = async (creador) => {
  const username = creador.username
  procesandoSeguimiento[username] = true
  
  try {
    await api.post('/user/unfollow', {
      creator_username: username  // ✅ Usar username
    })
    
    // Actualizar estado local
    creador.following = false
    creador.followers_count = Math.max((creador.followers_count || 1) - 1, 0)
    totalSiguiendo.value = Math.max(totalSiguiendo.value - 1, 0)
    
    toast.success(`Dejaste de seguir a ${username}`)
    
    // Si estamos en la vista de "siguiendo", remover de la lista
    if (modo.value === 'siguiendo') {
      creadores.value = creadores.value.filter(c => c.username !== username)
    }
    
  } catch (error) {
    console.error('Error al dejar de seguir creador:', error)
    
    if (error.response?.status === 401) {
      router.push('/login')
      return
    }
      const mensaje = error.response?.data?.error || 'Error al dejar de seguir al creador'
    toast.error(`${mensaje}`)
  } finally {
    procesandoSeguimiento[username] = false
  }
}

// Watchers
watch(ordenActual, (nuevoOrden, ordenAnterior) => {
  if (modo.value === 'explorar') {
    cargarCreadores(1)
  }
})

// Lifecycle
onMounted(async () => {
  await cargarEstadisticasSeguimiento()
  await cargarCreadores(1)
})
</script>

<style scoped>
.explore-creators {
  min-height: 100vh;
  background: var(--color-background);
  padding: var(--spacing-lg);
}

.explore-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.search-section {
  max-width: 800px;
  margin: 0 auto var(--spacing-xl);
}

.search-container {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.search-bar {
  margin-bottom: var(--spacing-lg);
}

.search-input-group {
  display: flex;
  gap: var(--spacing-sm);
}

.search-input {
  flex: 1;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  background: var(--color-background);
  color: var(--color-text);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.search-btn {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-lg);
  transition: background 0.2s ease;
}

.search-btn:hover {
  background: var(--color-primary-dark);
}

.search-help {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.filter-tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
}

.tab-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px solid var(--color-border);
  background: var(--color-background);
  color: var(--color-text);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.tab-btn:hover:not(:disabled) {
  background: var(--color-border-light);
  color: var(--color-text-dark);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.tab-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.sort-label {
  font-weight: 600;
  color: var(--color-text);
}

.sort-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  gap: var(--spacing-lg);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  max-width: 500px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
}

.empty-state h2 {
  color: var(--color-text);
  margin-bottom: var(--spacing-md);
}

.empty-state p {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--spacing-xl);
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
}

.creators-content {
  max-width: 1200px;
  margin: 0 auto;
}

.creators-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.creator-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.creator-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-border);
}

.creator-header {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  flex: 1;
}

.creator-avatar {
  flex-shrink: 0;
}

.creator-avatar-link {
  display: inline-block;
  transition: transform 0.2s ease;
  text-decoration: none;
  
  &:hover {
    transform: scale(1.05);
  }
}

.avatar-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border);
  transition: border-color 0.2s ease;
}

.creator-avatar-link:hover .avatar-image {
  border-color: var(--color-primary);
}

.avatar-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.creator-avatar-link:hover .avatar-placeholder {
  background: var(--color-primary-dark);
}

.creator-info {
  flex: 1;
}

.creator-name-link {
  text-decoration: none;
  
  &:hover .creator-name {
    color: var(--color-primary);
  }
}

.creator-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-xs);
  transition: color 0.2s ease;
}

.creator-bio {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
  margin-bottom: var(--spacing-sm);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.creator-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.stat {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background: var(--color-background);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
}

.creator-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: auto;
}

.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  flex: 1;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-xs);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(81, 16, 185, 0.3);
}

.btn-secondary {
  background: #10b981;
  color: white;
  border: 1px solid #059669;
}

.btn-secondary:hover:not(:disabled) {
  background: #059669;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-outline {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-outline:hover:not(:disabled) {
  background: var(--color-border-light);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
}

.pagination-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.pagination-btn:disabled {
  background: var(--color-border);
  cursor: not-allowed;
}

.pagination-info {
  font-weight: 600;
  color: var(--color-text);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .explore-creators {
    padding: var(--spacing-md);
  }
  
  .creators-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .creator-actions {
    flex-direction: column;
  }
  
  .filter-tabs {
    justify-content: center;
  }
  
  .sort-options {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-input-group {
    flex-direction: column;
  }
  
  .pagination {
    flex-direction: column;
    gap: var(--spacing-md);
  }
}
</style>
