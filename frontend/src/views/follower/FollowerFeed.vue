<template>
  <div class="feed-page">
    <!-- Header -->
    <div class="feed-header">
      <div class="header-content">
        <h1 class="page-title">🏠 Mi Feed</h1>
        <p class="page-subtitle">Contenido de los creadores que sigues</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="cargandoFeed" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando tu feed personalizado...</p>
    </div>

    <!-- Empty state - No following anyone -->
    <div v-else-if="posts.length === 0 && !cargandoFeed && mensaje" class="empty-feed">
      <div class="empty-icon">📱</div>
      <h2>Tu feed está vacío</h2>
      <p>{{ mensaje }}</p>
        <div class="feed-actions">
        <router-link to="/explore" class="btn btn-primary">
          Explorar Creadores
        </router-link>
        <router-link to="/creators" class="btn btn-outline">
          Ver Todos los Creadores
        </router-link>
      </div>
    </div>    <!-- Posts feed -->
    <div v-else class="feed-content">
      <div class="posts-container">        <div v-for="post in posts" :key="post._id" class="feed-post-wrapper">
          <PostCard 
            :post="post" 
            :showCreator="true" 
            :showActions="false"
            :showInteractions="true"
            @like="toggleLike"
          />
          
          <!-- Additional feed actions -->
          <div class="feed-post-actions">
            <button class="action-btn share-btn" @click="compartirPost(post)">
              🔗 Compartir
            </button>
            
            <router-link :to="`/creator/${post.creator_username}`" class="action-btn creator-btn">
              👤 Ver perfil
            </router-link>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="cargarPagina(paginaActual - 1)"
          :disabled="paginaActual === 1 || cargandoFeed"
          class="btn btn-outline"
        >
          ← Anterior
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="page in paginasVisibles" 
            :key="page"
            @click="cargarPagina(page)"
            :class="['page-btn', { active: page === paginaActual }]"
            :disabled="cargandoFeed"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          @click="cargarPagina(paginaActual + 1)"
          :disabled="paginaActual === totalPages || cargandoFeed"
          class="btn btn-outline"
        >
          Siguiente →
        </button>
      </div>

      <!-- Load more button for mobile -->
      <div v-if="totalPages > paginaActual" class="load-more-mobile">
        <button 
          @click="cargarPagina(paginaActual + 1)"
          :disabled="cargandoFeed"
          class="btn btn-primary btn-block"
        >
          {{ cargandoFeed ? 'Cargando...' : 'Cargar Más Posts' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import PostCard from '@/components/common/PostCard.vue'

export default {
  name: 'FollowerFeed',
  components: {
    PostCard
  },
  setup() {
    const router = useRouter()
    const toast = useToast()

    // Estados reactivos
    const posts = ref([])
    const cargandoFeed = ref(false)
    const mensaje = ref('')
    
    // Paginación
    const paginaActual = ref(1)
    const totalPosts = ref(0)
    const totalPages = ref(0)
    const postsPorPagina = 10

    // Computed
    const paginasVisibles = computed(() => {
      const total = totalPages.value
      const actual = paginaActual.value
      const rango = 2
      
      let inicio = Math.max(1, actual - rango)
      let fin = Math.min(total, actual + rango)
      
      // Ajustar si hay pocos números
      if (fin - inicio < 4) {
        if (inicio === 1) {
          fin = Math.min(total, inicio + 4)
        } else if (fin === total) {
          inicio = Math.max(1, fin - 4)
        }
      }
      
      const paginas = []
      for (let i = inicio; i <= fin; i++) {
        paginas.push(i)
      }
      
      return paginas
    })

    // Métodos
    const cargarFeed = async (page = 1) => {
      cargandoFeed.value = true
      mensaje.value = ''
      
      try {
        const response = await api.get('/user/feed', {
          params: { page, limit: postsPorPagina }
        })
        
        posts.value = response.data.posts
        paginaActual.value = response.data.page
        totalPosts.value = response.data.total
        totalPages.value = response.data.pages
        
        if (response.data.message) {
          mensaje.value = response.data.message
        }
      } catch (error) {
        console.error('Error al cargar feed:', error)
        
        if (error.response?.status === 401) {
          // Token expirado o no válido
          router.push('/login')
          return
        }
        
        toast.error('No se pudo cargar el feed')
        mensaje.value = 'Hubo un problema al cargar tu feed. Por favor, inténtalo más tarde.'
      } finally {
        cargandoFeed.value = false
      }
    }

    const cargarPagina = async (page) => {
      if (page >= 1 && page <= totalPages.value && page !== paginaActual.value) {
        await cargarFeed(page)
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    const toggleLike = async (post) => {
      // Por ahora solo actualizar localmente
      // En el futuro se puede implementar la funcionalidad real de likes
      post.liked = !post.liked
      if (post.liked) {
        post.likes_count = (post.likes_count || 0) + 1
        toast.success('Te gusta este post')
      } else {
        post.likes_count = Math.max(0, (post.likes_count || 0) - 1)
      }
    }

    const compartirPost = async (post) => {
      const url = `${window.location.origin}/creator/${post.creator_username}`
      
      if (navigator.share) {
        try {
          await navigator.share({
            title: post.title,
            text: `Mira este post de @${post.creator_username}: ${post.title}`,
            url: url
          })
        } catch (err) {
          if (err.name !== 'AbortError') {
            console.error('Error al compartir:', err)
          }
        }
      } else {
        // Fallback: copiar al portapapeles
        try {
          await navigator.clipboard.writeText(url)
          toast.success('Enlace copiado al portapapeles')
        } catch (err) {
          toast.error('No se pudo copiar el enlace')
        }
      }
    }
    
    const formatearTiempo = (fecha) => {
      if (!fecha) {
        return 'Fecha no disponible'
      }
      
      const ahora = new Date()
      const fechaPost = new Date(fecha)
      
      // Verificar si la fecha es válida
      if (isNaN(fechaPost.getTime())) {
        return 'Fecha inválida'
      }
      
      const diff = ahora - fechaPost
      
      const minutos = Math.floor(diff / (1000 * 60))
      const horas = Math.floor(diff / (1000 * 60 * 60))
      const dias = Math.floor(diff / (1000 * 60 * 60 * 24))
      
      if (minutos < 60) {
        return `${minutos}m`
      } else if (horas < 24) {
        return `${horas}h`
      } else if (dias < 7) {
        return `${dias}d`
      } else {
        return fechaPost.toLocaleDateString('es-ES', {
          month: 'short',
          day: 'numeric'
        })
      }
    }

    // Lifecycle
    onMounted(() => {
      cargarFeed()
    })

    return {
      posts,
      cargandoFeed,
      mensaje,
      paginaActual,
      totalPages,
      paginasVisibles,
      cargarFeed,
      cargarPagina,
      toggleLike,
      compartirPost,
      formatearTiempo
    }
  }
}
</script>

<style lang="scss" scoped>
.feed-page {
  min-height: 100vh;
  background: var(--color-background);
}

.feed-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-lg);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 var(--spacing-xs) 0;
}

.page-subtitle {
  color: var(--color-text-secondary);
  margin: 0;
}

.loading-container {
  text-align: center;
  padding: var(--spacing-xl);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border-light);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-feed {
  text-align: center;
  padding: var(--spacing-2xl);
  max-width: 500px;
  margin: 0 auto;
  
  .empty-icon {
    font-size: 4rem;
    margin-bottom: var(--spacing-lg);
  }
  
  h2 {
    color: var(--color-text);
    margin-bottom: var(--spacing-md);
  }
  
  p {
    color: var(--color-text-secondary);
    line-height: 1.6;
    margin-bottom: var(--spacing-xl);
  }
}

.feed-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  
  @media (max-width: 480px) {
    flex-direction: column;
  }
}

.feed-content {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.posts-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.feed-post-wrapper {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--color-border);
  }
}

.feed-post-actions {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-background);
  
  @media (max-width: 768px) {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
  }
}

.action-btn {
  background: none;
  border: 1px solid var(--color-border);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  
  &:hover {
    background: var(--color-border-light);
    color: var(--color-text);
    border-color: var(--color-border);
  }
  
  &.liked {
    color: var(--color-error);
    border-color: var(--color-error);
    background: rgba(239, 68, 68, 0.1);
  }
  
  &.creator-btn:hover {
    color: var(--color-primary);
    border-color: var(--color-primary);
    background: rgba(139, 92, 246, 0.1);
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  padding: var(--spacing-lg) 0;
  
  @media (max-width: 768px) {
    display: none;
  }
}

.page-numbers {
  display: flex;
  gap: var(--spacing-xs);
}

.page-btn {
  background: none;
  border: 1px solid var(--color-border);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  cursor: pointer;
  min-width: 40px;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--color-border-light);
  }
  
  &.active {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.load-more-mobile {
  margin-top: var(--spacing-xl);
  
  @media (min-width: 769px) {
    display: none;
  }
}

.btn-block {
  width: 100%;
}

@media (max-width: 768px) {
  .feed-page {
    padding: 0;
  }
  
  .feed-header {
    padding: var(--spacing-md);
  }
  
  .feed-content {
    padding: var(--spacing-md);
  }
  
  .feed-actions {
    flex-direction: column;
  }
}
</style>
