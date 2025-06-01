import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    usuarioActual: null,
    tokenAcceso: localStorage.getItem('access_token'),
    estaAutenticado: false,
    cargandoDatos: false
  }),

  getters: {
    esCreador: (state) => state.usuarioActual?.role === 'creator',
    esSeguidor: (state) => state.usuarioActual?.role === 'follower',
    rolUsuario: (state) => state.usuarioActual?.role
  },
  actions: {
    async iniciarSesion(credenciales) {
      this.cargandoDatos = true
      try {
        const respuesta = await api.post('/auth/login', credenciales)
        const { access_token } = respuesta.data
        
        this.tokenAcceso = access_token
        localStorage.setItem('access_token', access_token)
        
        // Obtener información del usuario
        await this.obtenerPerfilUsuario()
        
        this.estaAutenticado = true
        return { success: true }
      } catch (errorRespuesta) {
        return { 
          success: false, 
          error: errorRespuesta.response?.data?.error || 'Error de conexión' 
        }
      } finally {
        this.cargandoDatos = false
      }
    },

    async registrarUsuario(datosUsuario) {
      this.cargandoDatos = true
      try {
        await api.post('/auth/register', datosUsuario)
        return { success: true }
      } catch (errorRespuesta) {
        return { 
          success: false, 
          error: errorRespuesta.response?.data?.error || 'Error de registro' 
        }
      } finally {
        this.cargandoDatos = false
      }
    },

    async obtenerPerfilUsuario() {
      try {
        const respuesta = await api.get('/user/profile')
        this.usuarioActual = respuesta.data
        this.estaAutenticado = true
      } catch (errorRespuesta) {
        this.cerrarSesion()
      }
    },

    cerrarSesion() {
      this.usuarioActual = null
      this.tokenAcceso = null
      this.estaAutenticado = false
      localStorage.removeItem('access_token')
    },

    // Inicializar store al cargar la app
    async inicializar() {
      if (this.tokenAcceso) {
        await this.obtenerPerfilUsuario()
      }
    }
  }
})