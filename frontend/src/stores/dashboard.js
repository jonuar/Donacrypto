import { defineStore } from 'pinia'
import api from '@/services/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    // Estado de carga
    cargandoDatos: false,
    cargandoWallets: false,
    cargandoSeguidores: false,
      // Datos del dashboard
    estadisticas: {
      followers_count: 0,
      posts_count: 0
    },
    wallets: [],
    seguidores: [],
    
    // Estado del perfil
    editandoPerfil: false,
    erroresFormulario: {}
  }),

  getters: {
    // Wallets por tipo de moneda
    walletsPorTipo: (state) => {
      const walletMap = {}
      state.wallets.forEach(wallet => {
        walletMap[wallet.currency_type] = wallet
      })
      return walletMap
    },
    
    // Wallet predeterminada
    walletPredeterminada: (state) => {
      return state.wallets.find(w => w.is_default) || state.wallets[0]
    },
    
    // Monedas soportadas
    monedasSoportadas: () => ['ETH', 'BTC', 'USDT'],
    
    // Validar si tiene todas las wallets
    tieneTodasLasWallets: (state) => {
      const monedasSoportadas = ['ETH', 'BTC', 'USDT']
      const monedasActuales = state.wallets.map(w => w.currency_type)
      return monedasSoportadas.every(moneda => monedasActuales.includes(moneda))
    }
  },

  actions: {    // Obtener datos del dashboard
    async obtenerDatosDashboard() {
      this.cargandoDatos = true
      try {
        const respuesta = await api.get('/user/creator/dashboard')
        this.estadisticas = respuesta.data.stats
        return { success: true }
      } catch (error) {
        console.error('Error al obtener datos del dashboard:', error)
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error al cargar los datos' 
        }
      } finally {
        this.cargandoDatos = false
      }
    },

    // Obtener wallets del creador
    async obtenerWallets() {
      this.cargandoWallets = true
      try {
        const respuesta = await api.get('/user/wallets')
        this.wallets = respuesta.data.wallets
        return { success: true }
      } catch (error) {
        console.error('Error al obtener wallets:', error)
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error al cargar las wallets' 
        }
      } finally {
        this.cargandoWallets = false
      }
    },

    // Agregar nueva wallet
    async agregarWallet(datosWallet) {
      this.cargandoWallets = true
      this.erroresFormulario = {}
      try {
        await api.post('/user/wallets', datosWallet)
        await this.obtenerWallets() // Recargar lista
        return { success: true }
      } catch (error) {
        const errorResponse = error.response?.data
        if (errorResponse?.error) {
          this.erroresFormulario.general = errorResponse.error
        }
        return { 
          success: false, 
          error: errorResponse?.error || 'Error al agregar wallet' 
        }
      } finally {
        this.cargandoWallets = false
      }
    },

    // Actualizar wallet existente
    async actualizarWallet(currency_type, wallet_address) {
      this.cargandoWallets = true
      this.erroresFormulario = {}
      try {
        await api.put(`/user/wallets/${currency_type}`, { wallet_address })
        await this.obtenerWallets() // Recargar lista
        return { success: true }
      } catch (error) {
        const errorResponse = error.response?.data
        if (errorResponse?.error) {
          this.erroresFormulario.general = errorResponse.error
        }
        return { 
          success: false, 
          error: errorResponse?.error || 'Error al actualizar wallet' 
        }
      } finally {
        this.cargandoWallets = false
      }
    },

    // Eliminar wallet
    async eliminarWallet(currency_type) {
      this.cargandoWallets = true
      try {
        await api.delete(`/user/wallets/${currency_type}`)
        await this.obtenerWallets() // Recargar lista
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error al eliminar wallet' 
        }
      } finally {
        this.cargandoWallets = false
      }
    },

    // Establecer wallet como predeterminada
    async establecerWalletPredeterminada(currency_type) {
      this.cargandoWallets = true
      try {
        await api.put(`/user/wallets/set-default/${currency_type}`)
        await this.obtenerWallets() // Recargar lista
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error al establecer wallet predeterminada' 
        }
      } finally {
        this.cargandoWallets = false
      }
    },    // Obtener lista de seguidores
    async obtenerSeguidores(page = 1, limit = 20) {
      this.cargandoSeguidores = true
      try {
        const respuesta = await api.get('/user/creator/followers', {
          params: { page, limit }
        })
        this.seguidores = respuesta.data.followers
        return { 
          success: true, 
          data: respuesta.data
        }
      } catch (error) {
        console.error('Error al obtener seguidores:', error)
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error al cargar seguidores' 
        }
      } finally {
        this.cargandoSeguidores = false
      }
    },

    // Actualizar perfil de creador
    async actualizarPerfil(datosFormulario) {
      this.editandoPerfil = true
      this.erroresFormulario = {}
      try {
        await api.put('/user/creator/update-profile', datosFormulario)
        return { success: true }
      } catch (error) {
        const errorResponse = error.response?.data
        if (errorResponse?.error) {
          if (errorResponse.error.includes('nombre de usuario')) {
            this.erroresFormulario.username = errorResponse.error
          } else {
            this.erroresFormulario.general = errorResponse.error
          }
        }
        return { 
          success: false, 
          error: errorResponse?.error || 'Error al actualizar perfil' 
        }
      } finally {
        this.editandoPerfil = false
      }
    },

    // Limpiar errores del formulario
    limpiarErrores() {
      this.erroresFormulario = {}
    },

    // Inicializar dashboard (cargar todos los datos)
    async inicializarDashboard() {
      const resultados = await Promise.allSettled([
        this.obtenerDatosDashboard(),
        this.obtenerWallets(),
        this.obtenerSeguidores()
      ])

      // Verificar si alguna falló
      const fallos = resultados.filter(r => r.status === 'rejected' || !r.value?.success)
      
      if (fallos.length > 0) {
        console.warn('Algunos datos del dashboard no se pudieron cargar:', fallos)
      }

      return { success: true }
    }
  }
})
