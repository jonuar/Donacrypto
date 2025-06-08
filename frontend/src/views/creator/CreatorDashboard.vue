<template>
  <div class="dashboard-page">
    <!-- Header del Dashboard -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">PANEL DE CREADOR</h1>
          <p class="page-subtitle">Gestiona tu perfil, wallets y ve tus estadísticas</p>
        </div>
        <div class="header-actions">          <button @click="actualizarDatos" :disabled="cargandoDatos" class="btn btn-secondary">
            <span v-if="cargandoDatos">...</span>
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
          <!-- <div class="stat-card">
            <div class="stat-icon">🔒</div>
            <div class="stat-info">
              <span class="stat-value">100%</span>
              <span class="stat-label">Donaciones Directas</span>
            </div>
          </div> -->
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
                </div>                <div class="wallet-actions">
                  <button @click="editarWallet(wallet)" class="btn-icon" title="Editar">
                    ✎
                  </button>
                  <button @click="eliminarWallet(wallet.currency_type)" class="btn-icon" title="Eliminar">
                    ×
                  </button>
                </div>
              </div>
              
              <div class="wallet-address">
                <span class="address-label">Dirección:</span>
                <code class="address-text">{{ wallet.wallet_address }}</code>
                <button @click="copiarDireccion(wallet.wallet_address)" class="btn-copy" title="Copiar">
                  ⧉
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
            <button 
              v-if="estadisticas.followers_count > 0" 
              @click="cargarSeguidores" 
              :disabled="cargandoSeguidores"
              class="btn btn-outline btn-sm"
            >
              <span v-if="cargandoSeguidores">Cargando...</span>
              <span v-else>↻ Actualizar</span>
            </button>
          </div>
          
          <div v-if="estadisticas.followers_count === 0" class="empty-state">
            <div class="empty-icon">👥</div>
            <h3>Aún no tienes seguidores</h3>
            <p>Comparte tu perfil para empezar a recibir seguidores</p>
          </div>
          
          <div v-else-if="cargandoSeguidores && seguidores.length === 0" class="loading-container">
            <div class="loading-spinner small"></div>
            <p>Cargando seguidores...</p>
          </div>
          
          <div v-else class="followers-content">
            <div class="followers-list">
              <div 
                v-for="seguidor in seguidores" 
                :key="seguidor.username" 
                class="follower-item"
              >
                <div class="follower-avatar">
                  <img 
                    v-if="seguidor.avatar_url" 
                    :src="seguidor.avatar_url" 
                    :alt="seguidor.username"
                    class="avatar-image"
                  />
                  <div v-else class="avatar-placeholder">
                    {{ seguidor.username ? seguidor.username.charAt(0).toUpperCase() : '👤' }}
                  </div>
                </div>
                  <div class="follower-info">
                  <h4 class="follower-username">@{{ seguidor.username }}</h4>
                  <p class="follower-date">
                    Siguiendo desde {{ formatearFechaSeguimiento(seguidor.followed_at) }}
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Mostrar mensaje si hay más seguidores -->
            <div v-if="estadisticas.followers_count > seguidores.length" class="followers-summary">
              <p class="summary-text">
                Mostrando {{ seguidores.length }} de {{ estadisticas.followers_count }} seguidores
              </p>
              <button @click="cargarMasSeguidores" :disabled="cargandoSeguidores" class="btn btn-outline btn-sm">
                <span v-if="cargandoSeguidores">Cargando...</span>
                <span v-else>Ver más seguidores</span>
              </button>
            </div>
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
          </div>        </section>

        <!-- Danger Zone -->
        <section class="dashboard-section danger-zone">
          <div class="section-header">
            <h2 class="section-title danger-title">Zona de Peligro</h2>
          </div>
          
          <div class="danger-content">
            <div class="danger-warning">
              <div class="warning-icon">⚠️</div>
              <div class="warning-text">
                <h3>Eliminar Cuenta</h3>
                <p>Una vez que elimines tu cuenta, no podrás recuperarla. Esta acción es permanente.</p>
              </div>
            </div>
              <button 
              @click="mostrarModalEliminarCuenta = true" 
              class="btn-danger"
            >
              Eliminar Cuenta Permanentemente
            </button>
          </div>
        </section>
      </div>
    </div>    <!-- Modal para Eliminar Cuenta -->
    <DeleteAccountModal 
      :mostrar="mostrarModalEliminarCuenta"
      :user-role="'creator'"
      @cerrar="mostrarModalEliminarCuenta = false"
    />

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
import DeleteAccountModal from '@/components/common/DeleteAccountModal.vue'

export default {
  name: 'CreatorDashboard',  components: {
    PostCard,
    DeleteAccountModal
  },
  setup() {
    const dashboardStore = useDashboardStore()
    const authStore = useAuthStore()
    const toast = useToast()

    // Estados reactivos
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
    })

    const mostrarModalEliminarCuenta = ref(false)

    // Computed properties
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
    
    // Seguidores computed properties
    const seguidores = computed(() => dashboardStore.seguidores)
    const cargandoSeguidores = computed(() => dashboardStore.cargandoSeguidores)
    
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

    // Gestión de seguidores
    const cargarSeguidores = async () => {      const resultado = await dashboardStore.obtenerSeguidores()
      if (!resultado.success) {
        toast.error(resultado.error || 'Error al cargar seguidores')
      }
    }

    const cargarMasSeguidores = async () => {
      const resultado = await dashboardStore.obtenerSeguidores(false) // false = no limpiar lista existente
      if (!resultado.success) {
        toast.error(resultado.error || 'Error al cargar más seguidores')
      }
    }

    const formatearFechaSeguimiento = (fecha) => {
      if (!fecha) return 'Fecha no disponible'
      
      try {
        let fechaSeguimiento
        
        // Manejar diferentes formatos de fecha de MongoDB
        if (typeof fecha === 'string') {
          fechaSeguimiento = new Date(fecha)
        } else if (fecha.$date) {
          // Formato BSON ObjectId con $date
          fechaSeguimiento = new Date(fecha.$date)
        } else if (fecha.getTime) {
          // Ya es un objeto Date
          fechaSeguimiento = fecha
        } else {
          // Intentar convertir directamente
          fechaSeguimiento = new Date(fecha)
        }
        
        if (isNaN(fechaSeguimiento.getTime())) {
          console.warn('Fecha inválida recibida:', fecha)
          return 'Fecha inválida'
        }
        
        return fechaSeguimiento.toLocaleDateString('es-ES', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })      } catch (error) {
        console.error('Error al formatear fecha:', error, fecha)
        return 'Fecha inválida'
      }
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
      await cargarSeguidores()
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
      mostrarModalEliminarCuenta,
        // Computed
      estadisticas,
      wallets,
      posts,
      cargandoDatos,
      cargandoWallets,
      cargandoPosts,
      cargandoPerfil,
      erroresFormulario,
      usuarioActual,
      monedasDisponibles,
      paginaActualPosts,
      totalPostsPaginas,
      totalPostsCount,
      seguidores,
      cargandoSeguidores,
        // Métodos
      actualizarDatos,
      getCurrencyIcon,
      copiarDireccion,
      formatearFecha,
      cargarSeguidores,
      cargarMasSeguidores,
      formatearFechaSeguimiento,
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
  border-radius: var(--radius-lg);
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
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.page-subtitle {
  color: var(--color-text-secondary);
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
  border-radius: var(--radius-lg);
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
  color: var(--color-text-secondary);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--spacing-xl);
}

.dashboard-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.section-header {
  display: flex;
  flex-direction: column;
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
  width: 100%;
}

.wallet-card {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  background: var(--color-background);
  width: 100%;
  box-sizing: border-box;
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
  border-radius: var(--radius-sm);
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
  border-radius: var(--radius-sm);
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
  border-radius: var(--radius-sm);
}

.address-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
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
  border-radius: var(--radius-sm);
  background: white;
  padding: var(--spacing-sm);
}

.qr-caption {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
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
  width: 60px;
  height: 60px;
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
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.profile-bio {
  color: var(--color-text);
  line-height: 1.5;
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
  border-radius: var(--radius-lg);
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
  color: var(--color-text-secondary);
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
.form-textarea {  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  background: var(--color-background);
  color: var(--color-text);
    &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
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
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
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
  border-radius: var(--radius-lg);
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

/* Estilos para Posts */
.posts-section {
  grid-column: 1 / -1; /* Ocupa todo el ancho del grid */
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
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
  border-radius: var(--radius-md);
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
  color: var(--color-text-secondary);
  font-weight: normal;
}

.posts-pagination .btn {
  min-width: 100px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

@media (max-width: 480px) {
  .dashboard-page {
    padding: var(--spacing-sm);
  }
  
  .dashboard-header {
    padding: var(--spacing-lg);
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: var(--spacing-sm);
  }
  
  .wallet-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .wallet-actions {
    align-self: stretch;
    justify-content: flex-end;
  }
  
  .modal-overlay {
    padding: var(--spacing-sm);
  }
  
  .modal-content {
    margin: 0;
    max-width: 100%;
  }
  
  .address-text {
    max-width: 120px;
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: var(--spacing-md);
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .dashboard-section {
    padding: var(--spacing-lg);
    overflow: hidden;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .page-title {
    font-size: var(--font-size-2xl);
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
  
  .stat-card {
    padding: var(--spacing-md);
    flex-direction: column;
    text-align: center;
  }
  
  .profile-display {
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-md);
  }
  
  .wallet-card {
    padding: var(--spacing-md);
  }
  
  .wallet-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .wallet-actions {
    align-self: flex-end;
  }
  
  .address-text {
    font-size: var(--font-size-xs);
  }
  
  .form-input,
  .form-select,
  .form-textarea {
    font-size: 16px; /* Evita el zoom en iOS */
  }
  
  .modal-content {
    margin: var(--spacing-md);
    max-width: calc(100vw - 2rem);
  }
  
  .form-actions {
    flex-direction: column;
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
    .danger-zone {
    .danger-warning {
      flex-direction: column;
      text-align: center;
      
      .warning-icon {
        align-self: center;
      }
    }
  }
  
  .btn-danger {
    width: 100%;
    padding: var(--spacing-md);
  }
}

// Sección de Seguidores
.followers-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.followers-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.follower-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }
}

.follower-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border-light);
  background: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.follower-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.follower-username {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--font-size-sm);
}

.follower-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.followers-summary {
  text-align: center;
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
  margin-top: var(--spacing-md);
}

.summary-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.wallet-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--spacing-md);
  gap: var(--spacing-sm);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: var(--spacing-md);
    opacity: 0.5;
  }
  
  h3 {
    font-size: var(--font-size-lg);
    font-weight: 600;
    margin-bottom: var(--spacing-xs);
    color: var(--color-text);
  }
  
  p {
    font-size: var(--font-size-sm);
    line-height: 1.5;
  }
}

// Danger Zone Styles
.danger-zone {
  border: 2px solid #dc3545;
  border-radius: var(--radius-md);
  background: rgba(220, 53, 69, 0.05);
  
  .danger-title {
    color: #dc3545;
    font-weight: 700;
  }
  
  .danger-content {
    padding: var(--spacing-lg);
  }
  
  .danger-warning {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
    background: rgba(220, 53, 69, 0.1);
    border-radius: var(--border-radius-sm);
    border-left: 4px solid #dc3545;
    
    .warning-icon {
      font-size: 24px;
      flex-shrink: 0;
    }
    
    .warning-text {
      flex: 1;
      
      h3 {
        color: #721c24;
        font-size: var(--font-size-md);
        font-weight: 600;
        margin: 0 0 var(--spacing-xs) 0;
      }
      
      p {
        color: #856404;
        font-size: var(--font-size-sm);
        line-height: 1.5;
        margin: 0;
      }    }
  }
}

// Botón de peligro - fuera de danger-zone para uso global
.btn-danger {
  background: #dc3545;
  color: white;
  border: 2px solid #dc3545;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: #c82333;
    border-color: #c82333;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.25);
  }
}
</style>
