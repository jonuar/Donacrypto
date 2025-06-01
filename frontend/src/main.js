// ===== IMPORTACIONES DE ESTILOS =====
// Importamos el sistema de estilos Bento UI personalizado
import './assets/styles/style.scss'

// ===== IMPORTACIONES DE LIBRERÍAS =====
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

// ===== IMPORTACIONES DE LA APLICACIÓN =====
import App from './App.vue'
import router from './router'

// ===== CONFIGURACIÓN DE LA APLICACIÓN =====
const app = createApp(App)

// Configuración de stores (Pinia)
app.use(createPinia())
// Configuración del router
app.use(router)
// Configuración de notificaciones toast
app.use(Toast, {
  position: 'top-right',     // Posición de las notificaciones
  timeout: 5000,             // Tiempo antes de auto-cerrar
  closeOnClick: true,        // Cerrar al hacer clic
  pauseOnFocusLoss: true,    // Pausar cuando se pierde el foco
  pauseOnHover: true,        // Pausar al pasar el mouse
  draggable: true,           // Permitir arrastrar
  draggablePercent: 0.6,     // Porcentaje de arrastre para cerrar
  showCloseButtonOnHover: false, // No mostrar botón cerrar al hover
  hideProgressBar: false,    // Mostrar barra de progreso
  closeButton: 'button',     // Tipo de botón de cierre
  icon: true,                // Mostrar iconos
  rtl: false                 // Dirección de texto (izquierda a derecha)
})

// ===== MONTAJE DE LA APLICACIÓN =====
// Montamos la aplicación en el elemento con id 'app'
app.mount('#app')
