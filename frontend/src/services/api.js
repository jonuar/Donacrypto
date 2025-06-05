import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// Función para obtener token desde cualquier almacenamiento
const obtenerToken = () => {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
}

// Función para limpiar todos los tokens
const limpiarTokens = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('remember_me')
  sessionStorage.removeItem('access_token')
}

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
    const tokenAcceso = obtenerToken()
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
      limpiarTokens()
      window.location.href = '/login'
    }
    return Promise.reject(errorRespuesta)
  }
)

export default api