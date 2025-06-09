<template>
  <div class="creator-profile-page">
    <!-- Loading state -->
    <div v-if="cargandoCreador" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando perfil del creador...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-container">      <div class="error-icon">❌</div>
      <h2>Creador no encontrado</h2>
      <p>{{ error }}</p>
      <router-link to="/" class="btn btn-primary">Volver al inicio</router-link>
    </div>

    <!-- Creator profile -->
    <div v-else-if="creador" class="creator-profile">
      <!-- Bento Grid Layout -->
      <div class="bento-grid">
          <!-- Perfil Principal (Bento Card Grande) -->
        <div class="bento-card profile-main">
          <div class="profile-content">
            <div class="profile-avatar">
              <img 
                :src="creador.avatar_url || '/placeholder-avatar.png'" 
                :alt="creador.username"
                class="avatar-image"
              >
              <div class="avatar-badge">✨</div>
            </div>
            
            <div class="profile-info">
              <h1 class="profile-username">@{{ creador.username }}</h1>
              <p v-if="creador.bio" class="profile-bio">{{ creador.bio }}</p>
              <div class="profile-meta">
                <span class="creator-badge">Creador Verificado</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Estadísticas -->
        <div class="bento-card stats-card">
          <div class="card-header">
            <h3>📊 Estadísticas</h3>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ posts.length }}</span>
              <span class="stat-label">Posts</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ wallets.length }}</span>
              <span class="stat-label">Wallets</span>
            </div>
          </div>
        </div>

        <!-- Donaciones (Bento Card Mediana) -->
        <div class="bento-card donation-card">
          <div class="card-header">
            <h3>💰 Apoyar Creador</h3>
            <p class="card-subtitle">Donaciones directas sin intermediarios</p>
          </div>
          
          <div v-if="wallets.length > 0" class="donation-methods">
            <div v-for="wallet in wallets" :key="wallet.currency_type" class="wallet-bento">
              <div class="wallet-header">
                <span class="currency-icon">{{ getCurrencyIcon(wallet.currency_type) }}</span>
                <span class="currency-name">{{ wallet.currency_type }}</span>
              </div>
              
              <div class="wallet-body">
                <div class="wallet-address-container">
                  <code class="wallet-address">{{ wallet.wallet_address.slice(0, 12) }}...{{ wallet.wallet_address.slice(-8) }}</code>
                  <button @click="copiarDireccion(wallet.wallet_address)" class="btn-copy" title="Copiar dirección completa">
                    📋
                  </button>
                </div>
                  <div class="qr-container">
                  <canvas 
                    :id="`qr-${wallet.currency_type}`"
                    class="qr-code"
                    @click="abrirModalQR(wallet)"
                    title="Haz clic para ver en grande"
                  ></canvas>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="no-wallets">
            <div class="empty-state">
              <span class="empty-icon">💳</span>
              <p>Sin wallets configurados</p>
            </div>
          </div>
        </div>        <!-- Posts (Bento Card Ancha) -->
        <div class="bento-card posts-card">
          <div class="card-header">
            <h3>📝 Posts del Creador</h3>
            <span v-if="totalPosts > 0" class="posts-count">{{ totalPosts }} publicaciones</span>
          </div>

          <div v-if="cargandoPosts" class="loading-state">
            <div class="loading-spinner small"></div>
            <p>Cargando posts...</p>
          </div>

          <div v-else-if="posts.length === 0" class="empty-state">
            <span class="empty-icon">📄</span>
            <h4>No hay contenido aún</h4>
            <p>Este creador está preparando contenido increíble</p>
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
              :disabled="paginaActual === 1 || cargandoPosts"
              class="btn btn-outline"
            >
              ← Anterior
            </button>
            
            <div class="pagination-info">
              <span class="page-info">
                Página {{ paginaActual }} de {{ totalPages }}
              </span>
              <span class="posts-info">
                {{ ((paginaActual - 1) * postsPorPagina) + 1 }}-{{ Math.min(paginaActual * postsPorPagina, totalPosts) }} de {{ totalPosts }} posts
              </span>
            </div>
            
            <button 
              @click="cambiarPagina(paginaActual + 1)"
              :disabled="paginaActual === totalPages || cargandoPosts"
              class="btn btn-outline"
            >
              Siguiente →
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Modal QR ampliado -->
    <div v-if="mostrarModalQR" class="qr-modal-overlay" @click="cerrarModalQR">
      <div class="qr-modal" @click.stop>
        <div class="qr-modal-header">
          <h3>{{ getCurrencyIcon(walletSeleccionada?.currency_type) }} {{ walletSeleccionada?.currency_type }}</h3>
          <button @click="cerrarModalQR" class="close-btn">✕</button>
        </div>
          <div class="qr-modal-content">
          <div class="qr-large-container">
            <canvas 
              ref="qrModalCanvas"
              class="qr-large"
            ></canvas>
          </div>
          
          <div class="wallet-details">
            <p class="wallet-label">Dirección de la wallet:</p>
            <div class="wallet-address-large">
              <code>{{ walletSeleccionada?.wallet_address }}</code>
              <button 
                @click="copiarDireccion(walletSeleccionada?.wallet_address)" 
                class="btn-copy-large"
                title="Copiar dirección"
              >
                ⧉ Copiar
              </button>
            </div>
            <p class="qr-instructions">
              Escanea este código QR con tu wallet o copia la dirección para enviar {{ walletSeleccionada?.currency_type }}
            </p>
          </div>
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
    const toast = useToast()    // Estados reactivos
    const creador = ref(null)
    const posts = ref([])
    const wallets = ref([])
    const cargandoCreador = ref(false)
    const cargandoPosts = ref(false)
    const error = ref('')
      // Estados del modal QR
    const mostrarModalQR = ref(false)
    const walletSeleccionada = ref(null)
    
    // Referencias para los canvas QR
    const qrRefs = ref({})
    const qrModalCanvas = ref(null)
    
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
        paginaActual.value = page      } catch (err) {
        console.error('Error al obtener posts:', err);
        toast.error('No se pudieron cargar los posts')      } finally {
        cargandoPosts.value = false
      }
    }

    const cambiarPagina = async (nuevaPagina) => {      if (nuevaPagina >= 1 && nuevaPagina <= totalPages.value && !cargandoPosts.value) {
        await obtenerPosts(route.params.username, nuevaPagina)
      }
    }

    const getCurrencyIcon = (currency) => {
      const icons = {
        // Layer 1 Blockchains
        'BTC': '₿',
        'ETH': '⟠', 
        'BNB': '🟡',
        'ADA': '♠',
        'SOL': '◉',
        'DOT': '●',
        'AVAX': '🔺',
        'MATIC': '🔷',
        'ATOM': '⚛',
        'LTC': 'Ł',
        'XRP': '◊',
        'TRX': '🔺',
        
        // Stablecoins
        'USDT': '₮',
        'USDC': '⚪',
        'BUSD': '🟡',
        'DAI': '◈',
        
        // DeFi Tokens
        'UNI': '🦄',
        'LINK': '🔗',
        'AAVE': '👻',
        'COMP': '🏛',
        
        // Layer 2
        'ARB': '🔷',
        'OP': '🔴',
        
        // Meme Coins
        'DOGE': '🐕',
        'SHIB': '🐕'
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
      console.log('Generando códigos QR para wallets:', wallets.value)
      
      try {
        const QRCode = (await import('qrcode')).default
        console.log('Librería QRCode cargada correctamente')
        
        for (const wallet of wallets.value) {
          console.log(`Procesando wallet ${wallet.currency_type}:`, wallet.wallet_address)
          
          // Esperar a que el DOM esté listo
          await nextTick()
            // Buscar el canvas por múltiples selectores
          const canvasSelectors = [
            `#qr-${wallet.currency_type}`,
            `canvas#qr-${wallet.currency_type}`,
            `canvas[id="qr-${wallet.currency_type}"]`,
            `.qr-code`
          ]
          
          let canvas = null
          for (const selector of canvasSelectors) {
            const elements = document.querySelectorAll(selector)
            if (elements.length > 0) {
              // Si hay múltiples canvas, usar el índice correspondiente
              const index = wallets.value.indexOf(wallet)
              canvas = elements[index] || elements[0]
              break
            }
          }
          
          console.log(`Canvas encontrado para ${wallet.currency_type}:`, !!canvas)
          if (canvas) {
            await QRCode.toCanvas(canvas, wallet.wallet_address, {
              width: 150,
              margin: 1,
              color: {
                dark: '#1a1a1a',
                light: '#ffffff'
              }
            })
            console.log(`QR generado exitosamente para ${wallet.currency_type}`)
          } else {
            console.error(`No se encontró canvas para ${wallet.currency_type}`)
            console.log('Elementos canvas disponibles:', document.querySelectorAll('canvas'))
          }
        }
      } catch (error) {
        console.error('Error al generar códigos QR:', error)
      }
    }

    const abrirModalQR = async (wallet) => {
      walletSeleccionada.value = wallet
      mostrarModalQR.value = true
      
      // Esperar a que el modal se renderice y luego generar el QR grande
      await nextTick()
      setTimeout(async () => {
        await generarQRModal(wallet)
      }, 100)
    }

    const cerrarModalQR = () => {
      mostrarModalQR.value = false
      walletSeleccionada.value = null
    }

    const generarQRModal = async (wallet) => {
      try {
        console.log('Generando QR modal para:', wallet.currency_type)
        const QRCode = (await import('qrcode')).default
        
        // Usar la ref del canvas del modal
        const canvas = qrModalCanvas.value        
        if (canvas) {
          console.log('Canvas del modal encontrado usando ref, generando QR...')
          await QRCode.toCanvas(canvas, wallet.wallet_address, {
            width: 300,
            margin: 2,
            color: {
              dark: '#1a1a1a',
              light: '#ffffff'
            }
          })
          console.log(`QR modal generado exitosamente para ${wallet.currency_type}`)        } else {
          console.error(`No se encontró canvas para modal ${wallet.currency_type}`)
          console.log('qrModalCanvas.value:', qrModalCanvas.value)
          console.log('Modal visible:', !!document.querySelector('.qr-modal'))
        }
      } catch (error) {
        console.error('Error al generar QR modal:', error)
      }
    }

    // Watchers
    watch(() => route.params.username, async (newUsername) => {
      if (newUsername) {
        await obtenerPerfilCreador(newUsername)
        await obtenerPosts(newUsername)
      }
    })

    // Watcher para regenerar QR cuando cambien los wallets
    watch(wallets, async (newWallets) => {
      if (newWallets && newWallets.length > 0) {
        console.log('Wallets detectados, generando códigos QR...')
        // Pequeño delay para asegurar que el DOM esté actualizado
        setTimeout(() => {
          generarCodigosQR()
        }, 100)
      }
    }, { deep: true })

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
      totalPosts,
      postsPorPagina,
      mostrarModalQR,
      walletSeleccionada,
      qrModalCanvas,
      obtenerPerfilCreador,
      obtenerPosts,
      cambiarPagina,
      getCurrencyIcon,
      copiarDireccion,      formatearFecha,
      generarCodigosQR,
      abrirModalQR,
      cerrarModalQR,
      generarQRModal
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

.bento-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.bento-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  position: relative;
  overflow: hidden;
}

.profile-main {
  grid-column: 1 / 2;
  grid-row: 1 / 2;
  
  @media (max-width: 1024px) {
    grid-column: 1;
    grid-row: 1;
  }
}

.profile-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);

  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
}

.profile-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--color-border-light);
}

.avatar-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  border: 3px solid var(--color-surface);
}

.profile-info {
  flex: 1;
}

.profile-username {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 var(--spacing-sm) 0;
  background: linear-gradient(135deg, var(--color-text), var(--color-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.profile-bio {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--font-size-lg);
}

.profile-meta {
  display: flex;
  gap: var(--spacing-sm);
}

.creator-badge {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.stats-card {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
  
  @media (max-width: 1024px) {
    grid-column: 1;
    grid-row: 2;
  }
}

.card-header {
  margin-bottom: var(--spacing-lg);
  
  h3 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-text);
    margin: 0 0 var(--spacing-xs) 0;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }
  
  .card-subtitle {
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    margin: 0;
  }
  
  .posts-count {
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    font-weight: 500;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.stat-item {
  text-align: center;
  padding: var(--spacing-md);
  background: var(--color-background);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
}

.stat-value {
  display: block;
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.donation-card {
  grid-column: 1 / 3;
  grid-row: 2 / 3;
  
  @media (max-width: 1024px) {
    grid-column: 1;
    grid-row: 3;
  }
}

.donation-methods {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.wallet-bento {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 2px solid var(--color-border-light);
  position: relative;
  overflow: hidden;
}

.wallet-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border-light);
}

.currency-icon {
  font-size: var(--font-size-xl);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
}

.currency-name {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--font-size-lg);
}

.wallet-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.wallet-address-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: var(--color-surface);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.wallet-address {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  flex: 1;
  font-weight: 500;
}

.btn-copy {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.qr-container {
  display: flex;
  justify-content: center;
}

.qr-code {
  border-radius: var(--radius-md);
  background: white;
  padding: var(--spacing-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    border-color: var(--color-primary);
  }
}

.posts-card {
  grid-column: 1 / 3;
  grid-row: 3 / 4;
  
  @media (max-width: 1024px) {
    grid-column: 1;
    grid-row: 4;
  }
}

.loading-state, .empty-state {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
  
  .loading-spinner {
    margin: 0 auto var(--spacing-md);
  }
  
  .empty-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
    opacity: 0.7;
  }
  
  h4 {
    color: var(--color-text);
    margin-bottom: var(--spacing-sm);
    font-weight: 600;
  }
}

.qr-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.qr-modal {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--color-border-light);
}

.qr-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-light);
  
  h3 {
    margin: 0;
    font-size: var(--font-size-xl);
    color: var(--color-text);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }
}

.close-btn {
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  cursor: pointer;
  color: var(--color-text-secondary);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
}

.qr-modal-content {
  text-align: center;
}

.qr-large-container {
  margin-bottom: var(--spacing-lg);
  display: flex;
  justify-content: center;
}

.qr-large {
  border-radius: var(--radius-md);
  background: white;
  padding: var(--spacing-md);
  border: 2px solid var(--color-border-light);
}

.wallet-details {
  text-align: left;
}

.wallet-label {
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.wallet-address-large {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  
  code {
    flex: 1;
    font-family: monospace;
    font-size: var(--font-size-sm);
    color: var(--color-text);
    word-break: break-all;
    line-height: 1.4;
  }
}

.btn-copy-large {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  white-space: nowrap;
}

.qr-instructions {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
  text-align: center;
  padding: var(--spacing-md);
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.no-wallets {
  text-align: center;
  padding: var(--spacing-lg);
  color: var(--color-text-secondary);
}

.posts-grid {
  display: grid;
  gap: var(--spacing-lg);
}

.post-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  position: relative;
  overflow: hidden;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-md);
}

.post-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  flex: 1;
  line-height: 1.3;
}

.post-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  background: var(--color-background);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  font-weight: 500;
  flex-shrink: 0;
}

.post-content {
  margin-bottom: var(--spacing-lg);
  
  p {
    color: var(--color-text);
    line-height: 1.6;
    margin: 0;
    white-space: pre-wrap;
    font-size: var(--font-size-md);
  }
}

.post-footer {
  padding-top: var(--spacing-md);
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
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
  padding: var(--spacing-lg);
}

.pagination-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.page-info {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  background: var(--color-surface);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-light);
}

.posts-info {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}

.btn {
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--font-size-md);
  font-weight: 600;
  cursor: pointer;
  border: 2px solid transparent;
  
  &.btn-outline {
    background: var(--color-surface);
    color: var(--color-text);
    border-color: var(--color-border-light);
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  &.btn-primary {
    background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
    color: white;
  }
}

@media (max-width: 768px) {
  .creator-profile-page {
    padding: var(--spacing-md);
  }
  
  .bento-grid {
    gap: var(--spacing-md);
  }
  
  .bento-card {
    padding: var(--spacing-lg);
  }
  
  .profile-content {
    gap: var(--spacing-lg);
  }
  
  .avatar-image {
    width: 100px;
    height: 100px;
  }
  
  .profile-username {
    font-size: var(--font-size-2xl);
  }
  
  .donation-methods {
    grid-template-columns: 1fr;
  }
  
  .wallet-bento {
    padding: var(--spacing-md);
  }
  
  .post-card {
    padding: var(--spacing-lg);
  }
  
  .post-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: flex-start;
  }
    
  .pagination {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .pagination-info {
    order: -1;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .wallet-address {
    font-size: var(--font-size-xs);
  }
}
</style>
