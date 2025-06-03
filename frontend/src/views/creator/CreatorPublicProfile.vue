<template>
  <div class="creator-profile-page">
    <!-- Loading state -->
    <div v-if="cargandoCreador" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando perfil del creador...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">❌</div>
      <h2>Creador no encontrado</h2>
      <p>{{ error }}</p>
      <router-link to="/" class="btn btn-primary">Volver al inicio</router-link>
    </div>

    <!-- Creator profile -->
    <div v-else-if="creador" class="creator-profile">
      <!-- Header -->
      <div class="profile-header">
        <div class="profile-info">
          <div class="profile-avatar">
            <img 
              :src="creador.avatar_url || '/placeholder-avatar.png'" 
              :alt="creador.username"
              class="avatar-image"
            >
          </div>
          
          <div class="profile-details">
            <h1 class="profile-username">@{{ creador.username }}</h1>
            <p v-if="creador.bio" class="profile-bio">{{ creador.bio }}</p>
            
            <div class="profile-stats">
              <div class="stat">
                <span class="stat-value">{{ posts.length }}</span>
                <span class="stat-label">Posts</span>
              </div>
              <!-- Aquí podrían ir más estadísticas como seguidores si las haces públicas -->
            </div>
          </div>
        </div>

        <!-- Donation section -->
        <div class="donation-section">
          <h3>💰 Apoyar al Creador</h3>
          <p>Donaciones directas sin intermediarios</p>
          
          <div v-if="wallets.length > 0" class="donation-methods">
            <div v-for="wallet in wallets" :key="wallet.currency_type" class="wallet-item">
              <div class="wallet-info">
                <span class="currency-icon">{{ getCurrencyIcon(wallet.currency_type) }}</span>
                <span class="currency-name">{{ wallet.currency_type }}</span>
              </div>
              
              <div class="wallet-address-container">
                <code class="wallet-address">{{ wallet.wallet_address }}</code>
                <button @click="copiarDireccion(wallet.wallet_address)" class="btn-copy" title="Copiar">
                  📋
                </button>
              </div>
              
              <div class="qr-container">
                <canvas 
                  :data-ref="`qr-${wallet.currency_type}`"
                  class="qr-code"
                ></canvas>
              </div>
            </div>
          </div>
          
          <div v-else class="no-wallets">
            <p>Este creador aún no ha configurado métodos de donación.</p>
          </div>
        </div>
      </div>

      <!-- Posts section -->
      <div class="posts-section">
        <div class="section-header">
          <h2>📝 Posts Recientes</h2>
        </div>

        <div v-if="cargandoPosts" class="loading-container">
          <div class="loading-spinner small"></div>
          <p>Cargando posts...</p>
        </div>

        <div v-else-if="posts.length === 0" class="empty-posts">
          <div class="empty-icon">📄</div>
          <h3>No hay posts aún</h3>
          <p>Este creador aún no ha publicado contenido.</p>
        </div>

        <div v-else class="posts-grid">
          <article v-for="post in posts" :key="post._id" class="post-card">
            <header class="post-header">
              <h3 class="post-title">{{ post.title }}</h3>
              <time class="post-date">{{ formatearFecha(post.created_at) }}</time>
            </header>
            
            <div class="post-content">
              <p>{{ post.content }}</p>
            </div>
            
            <footer class="post-footer">
              <div class="post-stats">
                <span class="likes">❤️ {{ post.likes_count || 0 }}</span>
              </div>
            </footer>
          </article>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            @click="cambiarPagina(paginaActual - 1)"
            :disabled="paginaActual === 1"
            class="btn btn-outline"
          >
            Anterior
          </button>
          
          <span class="page-info">
            Página {{ paginaActual }} de {{ totalPages }}
          </span>
          
          <button 
            @click="cambiarPagina(paginaActual + 1)"
            :disabled="paginaActual === totalPages"
            class="btn btn-outline"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

export default {
  name: 'CreatorPublicProfile',
  setup() {
    const route = useRoute()
    const toast = useToast()

    // Estados reactivos
    const creador = ref(null)
    const posts = ref([])
    const wallets = ref([])
    const cargandoCreador = ref(false)
    const cargandoPosts = ref(false)
    const error = ref('')
    
    // Paginación
    const paginaActual = ref(1)
    const totalPosts = ref(0)
    const postsPorPagina = 10

    // Computed
    const totalPages = computed(() => Math.ceil(totalPosts.value / postsPorPagina))

    // Métodos
    const obtenerPerfilCreador = async (username) => {
      cargandoCreador.value = true
      error.value = ''
      
      try {
        // Obtener información de donación (incluye perfil básico del creador)
        const response = await api.get(`/user/creator/${username}/donation-info`)
        creador.value = response.data.creator
        wallets.value = response.data.wallets || []
        
        await generarCodigosQR()
      } catch (err) {
        console.error('Error al obtener perfil del creador:', err)
        error.value = err.response?.data?.error || 'No se pudo cargar el perfil del creador'
      } finally {
        cargandoCreador.value = false
      }
    }

    const obtenerPosts = async (username, page = 1) => {
      cargandoPosts.value = true
      
      try {
        const response = await api.get(`/user/creator/posts/${username}`, {
          params: { page, limit: postsPorPagina }
        })
        
        posts.value = response.data.posts
        totalPosts.value = response.data.total
        paginaActual.value = page
      } catch (err) {
        console.error('Error al obtener posts:', err)
        toast.error('No se pudieron cargar los posts')
      } finally {
        cargandoPosts.value = false
      }
    }

    const cambiarPagina = async (nuevaPagina) => {
      if (nuevaPagina >= 1 && nuevaPagina <= totalPages.value) {
        await obtenerPosts(route.params.username, nuevaPagina)
      }
    }

    const getCurrencyIcon = (currency) => {
      const icons = {
        'ETH': '⟠',
        'BTC': '₿',
        'USDT': '₮'
      }
      return icons[currency] || '💰'
    }

    const copiarDireccion = async (address) => {
      try {
        await navigator.clipboard.writeText(address)
        toast.success('Dirección copiada al portapapeles')
      } catch (err) {
        toast.error('No se pudo copiar la dirección')
      }
    }
    
    const formatearFecha = (fecha) => {
      if (!fecha) {
        return 'Fecha no disponible'
      }
      
      const postDate = new Date(fecha)
      
      // Verificar si la fecha es válida
      if (isNaN(postDate.getTime())) {
        return 'Fecha inválida'
      }
      
      return postDate.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const generarCodigosQR = async () => {
      await nextTick()
      
      try {
        const QRCode = (await import('qrcode')).default
        
        for (const wallet of wallets.value) {
          const canvas = document.querySelector(`[data-ref="qr-${wallet.currency_type}"]`)
          if (canvas) {
            QRCode.toCanvas(canvas, wallet.wallet_address, {
              width: 150,
              margin: 1,
              color: {
                dark: '#1a1a1a',
                light: '#ffffff'
              }
            })
          }
        }
      } catch (error) {
        console.warn('No se pudo cargar la librería QRCode:', error)
      }
    }

    // Watchers
    watch(() => route.params.username, async (newUsername) => {
      if (newUsername) {
        await obtenerPerfilCreador(newUsername)
        await obtenerPosts(newUsername)
      }
    })

    // Lifecycle
    onMounted(async () => {
      const username = route.params.username
      if (username) {
        await obtenerPerfilCreador(username)
        await obtenerPosts(username)
      }
    })

    return {
      creador,
      posts,
      wallets,
      cargandoCreador,
      cargandoPosts,
      error,
      paginaActual,
      totalPages,
      obtenerPerfilCreador,
      obtenerPosts,
      cambiarPagina,
      getCurrencyIcon,
      copiarDireccion,
      formatearFecha
    }
  }
}
</script>

<style lang="scss" scoped>
.creator-profile-page {
  min-height: 100vh;
  background: var(--color-background);
  padding: var(--spacing-lg);
}

.loading-container,
.error-container {
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
  
  &.small {
    width: 24px;
    height: 24px;
    border-width: 2px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  .error-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
  }
  
  h2 {
    color: var(--color-text);
    margin-bottom: var(--spacing-sm);
  }
  
  p {
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-lg);
  }
}

.creator-profile {
  max-width: 1200px;
  margin: 0 auto;
}

.profile-header {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-xl);
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.profile-info {
  display: flex;
  gap: var(--spacing-lg);
  align-items: flex-start;
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--color-border-light);
}

.profile-details {
  flex: 1;
}

.profile-username {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 var(--spacing-sm) 0;
}

.profile-bio {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--spacing-md) 0;
}

.profile-stats {
  display: flex;
  gap: var(--spacing-lg);
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-text);
}

.stat-label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.donation-section {
  h3 {
    color: var(--color-text);
    margin: 0 0 var(--spacing-xs) 0;
  }
  
  p {
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-md) 0;
    font-size: var(--font-size-sm);
  }
}

.donation-methods {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.wallet-item {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  background: var(--color-background);
}

.wallet-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.currency-icon {
  font-size: var(--font-size-lg);
}

.currency-name {
  font-weight: 600;
  color: var(--color-text);
}

.wallet-address-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.wallet-address {
  background: var(--color-surface);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-family: monospace;
  font-size: var(--font-size-xs);
  color: var(--color-text);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-copy {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  
  &:hover {
    background: var(--color-border-light);
  }
}

.qr-container {
  text-align: center;
}

.qr-code {
  border-radius: var(--radius-sm);
  background: white;
  padding: var(--spacing-xs);
}

.no-wallets {
  text-align: center;
  padding: var(--spacing-lg);
  color: var(--color-text-secondary);
}

.posts-section {
  .section-header {
    margin-bottom: var(--spacing-lg);
    
    h2 {
      font-size: var(--font-size-xl);
      font-weight: 600;
      color: var(--color-text);
      margin: 0;
    }
  }
}

.empty-posts {
  text-align: center;
  padding: var(--spacing-xl);
  
  .empty-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
  }
  
  h3 {
    color: var(--color-text);
    margin-bottom: var(--spacing-sm);
  }
  
  p {
    color: var(--color-text-secondary);
  }
}

.posts-grid {
  display: grid;
  gap: var(--spacing-lg);
}

.post-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.post-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  flex: 1;
}

.post-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.post-content {
  margin-bottom: var(--spacing-md);
  
  p {
    color: var(--color-text);
    line-height: 1.6;
    margin: 0;
    white-space: pre-wrap;
  }
}

.post-footer {
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-light);
}

.post-stats {
  display: flex;
  gap: var(--spacing-md);
}

.likes {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
}

.page-info {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

@media (max-width: 768px) {
  .creator-profile-page {
    padding: var(--spacing-md);
  }
  
  .profile-info {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-stats {
    justify-content: center;
  }
  
  .pagination {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}
</style>
