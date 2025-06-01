import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// Crear instancia de axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar token automáticamente
api.interceptors.request.use(
  (configuracion) => {
    const tokenAcceso = localStorage.getItem('access_token')
    if (tokenAcceso) {
      configuracion.headers.Authorization = `Bearer ${tokenAcceso}`
    }
    return configuracion
  },
  (errorRespuesta) => {
    return Promise.reject(errorRespuesta)
  }
)

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (respuesta) => respuesta,
  (errorRespuesta) => {
    if (errorRespuesta.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(errorRespuesta)
  }
)

export default api