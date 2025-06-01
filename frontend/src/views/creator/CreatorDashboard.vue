<template>
  <div class="dashboard-page">
    <!-- Header del Dashboard -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">PANEL DE CREADOR</h1>
          <p class="page-subtitle">Gestiona tu perfil, wallets y ve tus estadísticas</p>
        </div>
        <div class="header-actions">
          <button @click="actualizarDatos" :disabled="cargandoDatos" class="btn btn-secondary">
            <span v-if="cargandoDatos">🔄</span>
            <span v-else>↻</span>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="cargandoDatos && !estadisticas.followers_count" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando datos del dashboard...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Estadísticas Principales -->
      <section class="stats-section">
        <h2 class="section-title">Estadísticas</h2>        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
              <span class="stat-value">{{ estadisticas.followers_count || 0 }}</span>
              <span class="stat-label">Seguidores</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <span class="stat-value">{{ estadisticas.posts_count || 0 }}</span>
              <span class="stat-label">Posts</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🪙</div>
            <div class="stat-info">
              <span class="stat-value">{{ wallets.length || 0 }}</span>
              <span class="stat-label">Wallets Configuradas</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🔒</div>
            <div class="stat-info">
              <span class="stat-value">100%</span>
              <span class="stat-label">Donaciones Directas</span>
            </div>
          </div>
        </div>
        
        <!-- Información sobre donaciones directas -->
        <div class="info-banner">
          <div class="info-content">
            <h3>🔒 Donaciones Descentralizadas</h3>
            <p>
              Las donaciones van directamente a tus wallets de criptomonedas. 
              <strong>Sin intermediarios, sin comisiones, con privacidad total.</strong>
            </p>
          </div>
        </div>
      </section>

      <!-- Grid Principal -->
      <div class="dashboard-grid">
        <!-- Gestión de Wallets -->
        <section class="dashboard-section">
          <div class="section-header">
            <h2 class="section-title">Wallets de Criptomonedas</h2>
            <button @click="mostrarFormularioWallet = true" class="btn btn-primary btn-sm">
              + Agregar Wallet
            </button>
          </div>
          
          <div v-if="cargandoWallets" class="loading-container">
            <div class="loading-spinner small"></div>
            <p>Cargando wallets...</p>
          </div>
          
          <div v-else-if="wallets.length === 0" class="empty-state">
            <div class="empty-icon">🪙</div>
            <h3>No tienes wallets configuradas</h3>
            <p>Agrega al menos una wallet para recibir donaciones</p>
            <button @click="mostrarFormularioWallet = true" class="btn btn-primary">
              Agregar Primera Wallet
            </button>
          </div>
          
          <div v-else class="wallets-list">
            <div v-for="wallet in wallets" :key="wallet.currency_type" class="wallet-card">
              <div class="wallet-header">
                <div class="wallet-currency">
                  <span class="currency-icon">{{ getCurrencyIcon(wallet.currency_type) }}</span>
                  <span class="currency-name">{{ wallet.currency_type }}</span>
                  <span v-if="wallet.is_default" class="default-badge">Predeterminada</span>
                </div>
                <div class="wallet-actions">
                  <button @click="editarWallet(wallet)" class="btn-icon" title="Editar">
                    ✏️
                  </button>
                  <button @click="eliminarWallet(wallet.currency_type)" class="btn-icon" title="Eliminar">
                    🗑️
                  </button>
                </div>
              </div>
              
              <div class="wallet-address">
                <span class="address-label">Dirección:</span>
                <code class="address-text">{{ wallet.wallet_address }}</code>
                <button @click="copiarDireccion(wallet.wallet_address)" class="btn-copy" title="Copiar">
                  📋
                </button>
              </div>
                <!-- QR Code -->
              <div class="wallet-qr">
                <canvas :data-ref="`qr-${wallet.currency_type}`" class="qr-code"></canvas>
                <p class="qr-caption">Código QR para donaciones</p>
              </div>
              
              <div class="wallet-footer">
                <button 
                  v-if="!wallet.is_default" 
                  @click="establecerPredeterminada(wallet.currency_type)"
                  class="btn btn-outline btn-sm"
                >
                  Establecer como Predeterminada
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Gestión de Perfil -->
        <section class="dashboard-section">          <div class="section-header">
            <h2 class="section-title">Mi Perfil</h2>
            <button @click="toggleEditarPerfil" class="btn btn-secondary btn-sm">
              Editar
            </button>
          </div>
          
          <form v-if="editandoPerfil" @submit.prevent="guardarPerfil" class="profile-form">
            <div class="form-group">
              <label for="username">Nombre de Usuario</label>
              <input 
                id="username"
                v-model="perfilFormulario.username" 
                type="text" 
                class="form-input"
                :class="{ 'error': erroresFormulario.username }"
                placeholder="mi_usuario"
              >
              <span v-if="erroresFormulario.username" class="error-text">
                {{ erroresFormulario.username }}
              </span>
            </div>
            
            <div class="form-group">
              <label for="bio">Biografía</label>
              <textarea 
                id="bio"
                v-model="perfilFormulario.bio" 
                class="form-textarea"
                placeholder="Cuéntanos sobre ti..."
                rows="3"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="avatar_url">URL del Avatar</label>
              <input 
                id="avatar_url"
                v-model="perfilFormulario.avatar_url" 
                type="url" 
                class="form-input"
                placeholder="https://ejemplo.com/mi-avatar.jpg"
              >
            </div>
            
            <div v-if="erroresFormulario.general" class="error-message">
              {{ erroresFormulario.general }}
            </div>            <div class="form-actions">
              <button type="submit" :disabled="cargandoPerfil" class="btn btn-primary">
                {{ cargandoPerfil ? 'Guardando...' : 'Guardar Cambios' }}
              </button>
              <button type="button" @click="cancelarEdicionPerfil" class="btn btn-outline">
                Cancelar
              </button>
            </div>
          </form>
          
          <div v-else class="profile-display">
            <div class="profile-avatar">
              <img 
                :src="usuarioActual?.avatar_url || '/placeholder-avatar.png'" 
                :alt="usuarioActual?.username"
                class="avatar-image"
              >
            </div>
            <div class="profile-info">
              <h3 class="profile-username">@{{ usuarioActual?.username }}</h3>
              <p class="profile-email">{{ usuarioActual?.email }}</p>
              <p class="profile-bio">{{ usuarioActual?.bio || 'Sin biografía configurada' }}</p>
            </div>
          </div>
        </section>        <!-- Seguidores -->
        <section class="dashboard-section">
          <div class="section-header">
            <h2 class="section-title">Seguidores ({{ estadisticas.followers_count || 0 }})</h2>
          </div>
          
          <div v-if="estadisticas.followers_count === 0" class="empty-state">
            <div class="empty-icon">👥</div>
            <h3>Aún no tienes seguidores</h3>
            <p>Comparte tu perfil para empezar a recibir seguidores</p>
          </div>
          
          <div v-else class="followers-info">
            <p>Tienes {{ estadisticas.followers_count }} seguidores de tu contenido.</p>
            <!-- Lista de seguidores -->
          </div>
        </section>

        <!-- Gestión de Posts -->
        <section class="dashboard-section posts-section">
          <div class="section-header">
            <h2 class="section-title">Mis Posts ({{ estadisticas.posts_count || 0 }})</h2>
            <button @click="abrirFormularioPost" class="btn btn-primary btn-sm">
              + Crear Post
            </button>
          </div>
          
          <div v-if="cargandoPosts" class="loading-container">
            <div class="loading-spinner small"></div>
            <p>Cargando posts...</p>
          </div>
          
          <div v-else-if="posts.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>No tienes posts publicados</h3>
            <p>Crea tu primer post para empezar a compartir contenido con tus seguidores</p>
            <button @click="abrirFormularioPost" class="btn btn-primary">
              Crear Primer Post
            </button>
          </div>          <div v-else class="posts-list">
            <PostCard 
              v-for="post in posts" 
              :key="post._id" 
              :post="post"
              :show-actions="true"
              @delete="eliminarPost"
            />
            
            <!-- Paginación de posts -->
            <div v-if="totalPostsPaginas > 1" class="posts-pagination">
              <button 
                @click="cargarPaginaPosts(paginaActualPosts - 1)"
                :disabled="paginaActualPosts === 1 || cargandoPosts"
                class="btn btn-outline btn-sm"
              >
                ← Anterior
              </button>
              
              <div class="page-info">
                Página {{ paginaActualPosts }} de {{ totalPostsPaginas }}
                <span class="posts-count">({{ totalPostsCount }} posts total)</span>
              </div>
              
              <button 
                @click="cargarPaginaPosts(paginaActualPosts + 1)"
                :disabled="paginaActualPosts === totalPostsPaginas || cargandoPosts"
                class="btn btn-outline btn-sm"
              >
                Siguiente →
              </button>
            </div>
          </div>
        </section> 
      </div>
    </div>

    <!-- Modal para Agregar/Editar Wallet -->
    <div v-if="mostrarFormularioWallet" class="modal-overlay" @click="cerrarFormularioWallet">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ walletEditando ? 'Editar' : 'Agregar' }} Wallet</h3>
          <button @click="cerrarFormularioWallet" class="btn-close">×</button>
        </div>
        
        <form @submit.prevent="guardarWallet" class="wallet-form">
          <div class="form-group">
            <label for="currency_type">Tipo de Moneda</label>
            <select 
              id="currency_type"
              v-model="walletFormulario.currency_type" 
              class="form-select"
              :disabled="walletEditando"
              required
            >
              <option value="">Seleccionar moneda</option>
              <option v-for="moneda in monedasDisponibles" :key="moneda" :value="moneda">
                {{ moneda }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="wallet_address">Dirección de la Wallet</label>
            <input 
              id="wallet_address"
              v-model="walletFormulario.wallet_address" 
              type="text" 
              class="form-input"
              placeholder="0x1234..."
              required
            >
          </div>
          
          <div v-if="erroresFormulario.general" class="error-message">
            {{ erroresFormulario.general }}
          </div>
          
          <div class="form-actions">
            <button type="submit" :disabled="cargandoWallets" class="btn btn-primary">
              {{ cargandoWallets ? 'Guardando...' : 'Guardar' }}
            </button>
            <button type="button" @click="cerrarFormularioWallet" class="btn btn-outline">
              Cancelar
            </button>          </div>
        </form>
      </div>
    </div>

    <!-- Modal para Crear Post -->
    <div v-if="mostrarFormularioPost" class="modal-overlay" @click="cerrarFormularioPost">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Crear Nuevo Post</h3>
          <button @click="cerrarFormularioPost" class="btn-close">×</button>
        </div>
        
        <form @submit.prevent="crearPost" class="post-form">
          <div class="form-group">
            <label for="post_title">Título del Post</label>
            <input 
              id="post_title"
              v-model="postFormulario.title" 
              type="text" 
              class="form-input"
              placeholder="Título de tu post..."
              required
            >
          </div>
          
          <div class="form-group">
            <label for="post_content">Contenido</label>
            <textarea 
              id="post_content"
              v-model="postFormulario.content" 
              class="form-textarea"
              placeholder="Escribe el contenido de tu post..."
              rows="6"
              required
            ></textarea>
          </div>
          
          <div v-if="erroresFormulario.general" class="error-message">
            {{ erroresFormulario.general }}
          </div>
          
          <div class="form-actions">
            <button type="submit" :disabled="cargandoPosts" class="btn btn-primary">
              {{ cargandoPosts ? 'Publicando...' : 'Publicar Post' }}
            </button>
            <button type="button" @click="cerrarFormularioPost" class="btn btn-outline">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import PostCard from '@/components/common/PostCard.vue'

export default {
  name: 'CreatorDashboard',
  components: {
    PostCard
  },
  setup() {
    const dashboardStore = useDashboardStore()
    const authStore = useAuthStore()
    const toast = useToast()    // Estados reactivos
    const mostrarFormularioWallet = ref(false)
    const walletEditando = ref(null)
    const walletFormulario = reactive({
      currency_type: '',
      wallet_address: ''
    })

    const editandoPerfil = ref(false)
    const perfilFormulario = reactive({
      username: '',
      bio: '',
      avatar_url: ''
    })

    const mostrarFormularioPost = ref(false)
    const postFormulario = reactive({
      title: '',
      content: ''
    })    // Computed properties
    const estadisticas = computed(() => dashboardStore.estadisticas)
    const wallets = computed(() => dashboardStore.wallets)
    const posts = computed(() => dashboardStore.posts)
    const cargandoDatos = computed(() => dashboardStore.cargandoDatos)
    const cargandoWallets = computed(() => dashboardStore.cargandoWallets)
    const cargandoPosts = computed(() => dashboardStore.cargandoPosts)
    const cargandoPerfil = computed(() => dashboardStore.editandoPerfil)
    const erroresFormulario = computed(() => dashboardStore.erroresFormulario)
    const usuarioActual = computed(() => authStore.usuarioActual)
    const monedasSoportadas = computed(() => dashboardStore.monedasSoportadas)
    
    // Pagination computed properties
    const paginaActualPosts = computed(() => dashboardStore.paginaActualPosts)
    const totalPostsPaginas = computed(() => dashboardStore.totalPostsPaginas)
    const totalPostsCount = computed(() => dashboardStore.totalPostsCount)

    const monedasDisponibles = computed(() => {
      const monedasUsadas = wallets.value.map(w => w.currency_type)
      if (walletEditando.value) {
        return monedasSoportadas.value
      }
      return monedasSoportadas.value.filter(m => !monedasUsadas.includes(m))
    })

    // Métodos
    const actualizarDatos = async () => {
      await dashboardStore.inicializarDashboard()
      toast.success('Datos actualizados')
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
      return new Date(fecha).toLocaleDateString('es-ES')
    }

    // Gestión de wallets
    const editarWallet = (wallet) => {
      walletEditando.value = wallet
      walletFormulario.currency_type = wallet.currency_type
      walletFormulario.wallet_address = wallet.wallet_address
      mostrarFormularioWallet.value = true
    }

    const cerrarFormularioWallet = () => {
      mostrarFormularioWallet.value = false
      walletEditando.value = null
      walletFormulario.currency_type = ''
      walletFormulario.wallet_address = ''
      dashboardStore.limpiarErrores()
    }

    const guardarWallet = async () => {
      const resultado = walletEditando.value
        ? await dashboardStore.actualizarWallet(walletFormulario.currency_type, walletFormulario.wallet_address)
        : await dashboardStore.agregarWallet(walletFormulario)

      if (resultado.success) {
        toast.success(walletEditando.value ? 'Wallet actualizada' : 'Wallet agregada')
        cerrarFormularioWallet()
        await generarCodigosQR()
      } else {
        toast.error(resultado.error)
      }
    }

    const eliminarWallet = async (currency_type) => {
      if (!confirm(`¿Estás seguro de eliminar la wallet de ${currency_type}?`)) return

      const resultado = await dashboardStore.eliminarWallet(currency_type)
      if (resultado.success) {
        toast.success('Wallet eliminada')
      } else {
        toast.error(resultado.error)
      }
    }

    const establecerPredeterminada = async (currency_type) => {
      const resultado = await dashboardStore.establecerWalletPredeterminada(currency_type)
      if (resultado.success) {
        toast.success('Wallet establecida como predeterminada')
      } else {
        toast.error(resultado.error)
      }
    }

    // Gestión de perfil
    const toggleEditarPerfil = () => {
      editandoPerfil.value = !editandoPerfil.value
      if (editandoPerfil.value) {
        const usuario = usuarioActual.value
        perfilFormulario.username = usuario?.username || ''
        perfilFormulario.bio = usuario?.bio || ''
        perfilFormulario.avatar_url = usuario?.avatar_url || ''
      }
      dashboardStore.limpiarErrores()
    }

    const cancelarEdicionPerfil = () => {
      editandoPerfil.value = false
      dashboardStore.limpiarErrores()
    }

    const guardarPerfil = async () => {
      const resultado = await dashboardStore.actualizarPerfil(perfilFormulario)
      
      if (resultado.success) {
        toast.success('Perfil actualizado')
        editandoPerfil.value = false
        await authStore.obtenerPerfilUsuario() // Actualizar datos en el store de auth
      } else {
        toast.error(resultado.error)      }
    }

    // Gestión de posts
    const abrirFormularioPost = () => {
      mostrarFormularioPost.value = true
      postFormulario.title = ''
      postFormulario.content = ''
      dashboardStore.limpiarErrores()
    }

    const cerrarFormularioPost = () => {
      mostrarFormularioPost.value = false
      postFormulario.title = ''
      postFormulario.content = ''
      dashboardStore.limpiarErrores()
    }

    const crearPost = async () => {
      const resultado = await dashboardStore.crearPost(postFormulario)
      
      if (resultado.success) {
        toast.success('Post creado con éxito')
        cerrarFormularioPost()      } else {
        toast.error(resultado.error)
      }
    }

    const eliminarPost = async (postId) => {
      if (!confirm('¿Estás seguro de eliminar este post?')) return

      const resultado = await dashboardStore.eliminarPost(postId)
      if (resultado.success) {
        toast.success('Post eliminado')
      } else {
        toast.error(resultado.error)
      }
    }

    const cargarPaginaPosts = async (page) => {
      if (page >= 1 && page <= totalPostsPaginas.value && page !== paginaActualPosts.value) {
        const resultado = await dashboardStore.cargarPaginaPosts(page)
        if (!resultado.success) {
          toast.error(resultado.error)
        }
      }
    }

    const formatearFechaPost = (fecha) => {
      return new Date(fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Generar códigos QR para las wallets
    const generarCodigosQR = async () => {
      await nextTick()
      
      // Importar QRCode de forma dinámica
      try {
        const QRCode = (await import('qrcode')).default
        
        for (const wallet of wallets.value) {
          const canvas = document.querySelector(`[data-ref="qr-${wallet.currency_type}"]`)
          if (canvas) {
            QRCode.toCanvas(canvas, wallet.wallet_address, {
              width: 120,
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
    }    // Lifecycle
    onMounted(async () => {
      await dashboardStore.inicializarDashboard()
      await generarCodigosQR()
    })

    return {
      // Estados
      mostrarFormularioWallet,
      walletEditando,
      walletFormulario,
      editandoPerfil,
      perfilFormulario,
      mostrarFormularioPost,
      postFormulario,
      
      // Computed
      estadisticas,
      wallets,
      posts,
      cargandoDatos,
      cargandoWallets,
      cargandoPosts,
      cargandoPerfil,      erroresFormulario,
      usuarioActual,
      monedasDisponibles,
      paginaActualPosts,
      totalPostsPaginas,
      totalPostsCount,
      
      // Métodos
      actualizarDatos,
      getCurrencyIcon,
      copiarDireccion,
      formatearFecha,
      editarWallet,
      cerrarFormularioWallet,
      guardarWallet,
      eliminarWallet,
      establecerPredeterminada,
      toggleEditarPerfil,
      cancelarEdicionPerfil,
      guardarPerfil,
      abrirFormularioPost,
      cerrarFormularioPost,
      crearPost,
      eliminarPost,
      cargarPaginaPosts,
      formatearFechaPost
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--color-background);
  padding: var(--spacing-lg);
}

.dashboard-header {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-lg);
}

.page-title {
  font-size: var(--font-size-xxl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.page-subtitle {
  color: var(--color-text-light);
  margin: var(--spacing-xs) 0 0 0;
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

.stats-section {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-lg);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.stat-card {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.stat-icon {
  font-size: 2rem;
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
  color: var(--color-text-light);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-xl);
}

.dashboard-section {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-xl);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.wallets-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.wallet-card {
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  background: var(--color-background);
}

.wallet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.wallet-currency {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.currency-icon {
  font-size: var(--font-size-lg);
}

.currency-name {
  font-weight: 600;
  color: var(--color-text);
}

.default-badge {
  background: var(--color-success);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.wallet-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-icon {
  background: none;
  border: none;
  padding: var(--spacing-xs);
  cursor: pointer;
  border-radius: var(--border-radius-sm);
  transition: background-color 0.2s;
  
  &:hover {
    background: var(--color-border-light);
  }
}

.wallet-address {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm);
  background: var(--color-surface);
  border-radius: var(--border-radius-sm);
}

.address-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  min-width: max-content;
}

.address-text {
  font-family: monospace;
  font-size: var(--font-size-sm);
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
}

.wallet-qr {
  text-align: center;
  margin: var(--spacing-md) 0;
}

.qr-code {
  border-radius: var(--border-radius-sm);
  background: white;
  padding: var(--spacing-sm);
}

.qr-caption {
  font-size: var(--font-size-xs);
  color: var(--color-text-light);
  margin-top: var(--spacing-xs);
}

.profile-display {
  display: flex;
  gap: var(--spacing-lg);
  align-items: flex-start;
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border-light);
}

.profile-username {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-xs);
}

.profile-email {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  margin-bottom: var(--spacing-sm);
}

.profile-bio {
  color: var(--color-text);
  line-height: 1.5;
}

.donations-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.donation-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  background: var(--color-background);
}

.donation-amount {
  font-weight: 600;
  color: var(--color-success);
}

.donation-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-md);
}

.modal-content {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.btn-close {
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  cursor: pointer;
  color: var(--color-text-light);
  padding: var(--spacing-xs);
  
  &:hover {
    color: var(--color-text);
  }
}

.wallet-form,
.profile-form {
  padding: var(--spacing-lg);
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
  color: var(--color-text);
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-md);
  background: var(--color-background);
  color: var(--color-text);
  
  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
  }
  
  &.error {
    border-color: var(--color-error);
  }
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.error-text {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
  display: block;
}

.error-message {
  background: rgba(var(--color-error-rgb), 0.1);
  color: var(--color-error);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-sm);
}

.form-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
}

.info-banner {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  margin-top: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  color: white;
}

.info-content h3 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-lg);
}

.info-content p {
  margin: 0;
  opacity: 0.9;
  line-height: 1.5;
}

.decentralized-benefits {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-md);
}

.benefit-card {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-surface);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border-light);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
}

.benefit-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.benefit-content h4 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--color-text);
}

.benefit-content p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  line-height: 1.4;
}

/* Estilos para Posts */
.posts-section {
  grid-column: 1 / -1; /* Ocupa todo el ancho del grid */
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.post-card {
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  background: var(--color-background);
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: var(--shadow-sm);
    border-color: var(--color-border);
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

.post-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.post-content {
  margin-bottom: var(--spacing-md);
}

.post-content p {
  color: var(--color-text);
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap; /* Preserve line breaks */
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-light);
}

.post-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.post-likes {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.post-form {
  padding: var(--spacing-lg);
}

.post-form .form-textarea {
  min-height: 120px;
}

/* Pagination Styles */
.posts-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-surface);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border-light);
}

.page-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text);
  font-weight: 500;
}

.posts-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-light);
  font-weight: normal;
}

.posts-pagination .btn {
  min-width: 100px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: var(--spacing-md);
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
    .profile-display {
    flex-direction: column;
    text-align: center;
  }
  
  .posts-pagination {
    flex-direction: column;
    gap: var(--spacing-sm);
    text-align: center;
  }
  
  .posts-pagination .btn {
    min-width: auto;
    flex: 1;
  }
}
</style>
