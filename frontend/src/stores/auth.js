import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    usuarioActual: null,
    tokenAcceso: null,
    estaAutenticado: false,
    cargandoDatos: false,
    recordarSesion: false
  }),

  getters: {
    esCreador: (state) => state.usuarioActual?.role === 'creator',
    esSeguidor: (state) => state.usuarioActual?.role === 'follower',
    rolUsuario: (state) => state.usuarioActual?.role
  },

  actions: {
    // Función para obtener el token desde cualquier almacenamiento
    obtenerTokenAlmacenado() {
      return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    },

    // Función para guardar token según la estrategia
    guardarToken(token, recordarMe) {
      if (recordarMe) {
        localStorage.setItem('access_token', token)
        localStorage.setItem('remember_me', 'true')
        // Limpiar sessionStorage si existe
        sessionStorage.removeItem('access_token')
      } else {
        sessionStorage.setItem('access_token', token)
        // Limpiar localStorage si existe
        localStorage.removeItem('access_token')
        localStorage.removeItem('remember_me')
      }
    },

    // Función para limpiar todos los tokens
    limpiarTokens() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('remember_me')
      sessionStorage.removeItem('access_token')
    },

    async iniciarSesion(credenciales) {
      this.cargandoDatos = true
      try {
        // Incluir remember_me en las credenciales
        const datosLogin = {
          email: credenciales.email,
          password: credenciales.password,
          remember_me: credenciales.rememberMe || false
        }

        const respuesta = await api.post('/auth/login', datosLogin)
        const { access_token, remember_me } = respuesta.data
        
        this.tokenAcceso = access_token
        this.recordarSesion = remember_me || false
        
        // Guardar token según la estrategia
        this.guardarToken(access_token, this.recordarSesion)
        
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
      this.recordarSesion = false
      this.limpiarTokens()
    },

    // Eliminar cuenta del usuario
    async eliminarCuenta(password) {
      try {
        await api.delete('/user/delete-account', {
          data: { password }
        })
        
        // Limpiar estado de autenticación
        this.cerrarSesion()
        
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error al eliminar la cuenta' 
        }
      }
    },

    // Inicializar store al cargar la app
    async inicializar() {
      const token = this.obtenerTokenAlmacenado()
      const recordarMe = localStorage.getItem('remember_me') === 'true'
      
      if (token) {
        this.tokenAcceso = token
        this.recordarSesion = recordarMe
        await this.obtenerPerfilUsuario()
      }
    }
  }
})