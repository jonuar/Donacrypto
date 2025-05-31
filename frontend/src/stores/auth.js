import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token'),
    isAuthenticated: false,
    loading: false
  }),

  getters: {
    isCreator: (state) => state.user?.role === 'creator',
    isFollower: (state) => state.user?.role === 'follower',
    userRole: (state) => state.user?.role
  },

  actions: {
    async login(credentials) {
      this.loading = true
      try {
        const response = await api.post('/auth/login', credentials)
        const { access_token } = response.data
        
        this.token = access_token
        localStorage.setItem('access_token', access_token)
        
        // Obtener información del usuario
        await this.fetchUserProfile()
        
        this.isAuthenticated = true
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error de conexión' 
        }
      } finally {
        this.loading = false
      }
    },

    async register(userData) {
      this.loading = true
      try {
        await api.post('/auth/register', userData)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Error de registro' 
        }
      } finally {
        this.loading = false
      }
    },

    async fetchUserProfile() {
      try {
        const response = await api.get('/user/profile')
        this.user = response.data
        this.isAuthenticated = true
      } catch (error) {
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('access_token')
    },

    // Inicializar store al cargar la app
    async initialize() {
      if (this.token) {
        await this.fetchUserProfile()
      }
    }
  }
})