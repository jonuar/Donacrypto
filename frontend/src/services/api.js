import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

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
  },
  withCredentials: false
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
      limpiarTokens()
    }
    return Promise.reject(errorRespuesta)
  }
)

// Interceptor para logging en desarrollo
api.interceptors.request.use(request => {
  console.log('API Request:', request.baseURL + request.url)
  return request
})

export default api