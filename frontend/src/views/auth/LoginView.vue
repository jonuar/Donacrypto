<template>
  <AuthComponent>
    <div class="login-form">
      <div class="form-header">
        <!-- Botón para volver al inicio -->
        <router-link to="/" class="back-to-home">
          <span class="back-icon">←</span>
          Volver al Inicio
        </router-link>
        <h2 class="form-title">¡Bienvenido de vuelta!</h2>
        <p class="form-subtitle">Inicia sesión para continuar con tu cuenta</p>
      </div>

      <div class="form">
        <div class="input-group">
          <label for="email" class="input-label">Correo electrónico</label>
          <input
            id="email"
            v-model="datosFormulario.email"
            type="email"
            class="input-field"
            :class="{ 'input-error': erroresValidacion.email }"
            placeholder="tu@email.com"
            @keyup.enter="handleLogin"
          />
          <span v-if="erroresValidacion.email" class="input-error-text">{{ erroresValidacion.email }}</span>
        </div>        <div class="input-group">
          <label for="password" class="input-label">Contraseña</label>
         <div class="password-field">
            <input
              id="password"
              v-model="datosFormulario.password"
              :type="mostrarContrasena ? 'text' : 'password'"
              class="input-field"
              :class="{ 'input-error': erroresValidacion.password }"
              placeholder="••••••••"
              @keyup.enter="handleLogin"
            />

            <button
              type="button"
              @click.prevent.stop="mostrarContrasena = !mostrarContrasena"
              class="password-toggle"
              :aria-label="mostrarContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            >
              <!-- Iconos SVG -->
              <svg v-if="mostrarContrasena" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94L17.94 17.94z"/>
                <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19l-6.84-6.84z"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>
          <span v-if="erroresValidacion.password" class="input-error-text">{{ erroresValidacion.password }}</span>
        </div>        <div class="form-options">
          <label class="checkbox-group">
            <input v-model="datosFormulario.rememberMe" type="checkbox" class="checkbox" />
            <span class="checkbox-label">Recordarme</span>
          </label>
        </div>

        <button
          type="button"
          @click.prevent.stop="handleLogin"
          :disabled="cargandoDatos"
          class="btn btn-primary btn-lg w-full"
        >
          <span v-if="cargandoDatos" class="spinner"></span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </div>

      <div class="form-footer">
        <p class="footer-text">
          ¿No tienes una cuenta?
          <router-link to="/register" class="footer-link">
            Regístrate aquí
          </router-link>        </p>
      </div>
    </div>
  </AuthComponent>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import AuthComponent from '@/components/auth/AuthComponent.vue'

export default {
  name: 'LoginView',
  components: {
    AuthComponent
  },
  setup() {    const router = useRouter()
    const toast = useToast()
    const authStore = useAuthStore()

    const cargandoDatos = ref(false)
    const mostrarContrasena = ref(false)

    // Formulario reactivo para los datos de login
    const datosFormulario = reactive({
      email: '',
      password: '',
      rememberMe: false
        })

    // Objeto reactivo para manejar errores de validación
    const erroresValidacion = reactive({
      email: '',
      password: ''
    })    // Función para limpiar todos los errores
    const clearErrors = () => {
      erroresValidacion.email = ''
      erroresValidacion.password = ''
    }    // Función de validación del formulario
    const validateForm = () => {
      clearErrors()
      let isValid = true

      // Validación del email
      if (!datosFormulario.email) {
        erroresValidacion.email = 'El correo electrónico es requerido'
        isValid = false
      } else if (!/\S+@\S+\.\S+/.test(datosFormulario.email)) {
        erroresValidacion.email = 'Ingresa un correo electrónico válido'
        isValid = false
      }

      // Validación de la contraseña
      if (!datosFormulario.password) {
        erroresValidacion.password = 'La contraseña es requerida'
        isValid = false
      } else if (datosFormulario.password.length < 6) {
        erroresValidacion.password = 'La contraseña debe tener al menos 6 caracteres'
        isValid = false
      }      return isValid
    }

    // Función principal para manejar el login
    const handleLogin = async () => {
      try {
        if (!validateForm()) {
          return false
        }

        if (cargandoDatos.value) {
          return false
        }

        cargandoDatos.value = true
        clearErrors()
        
        const result = await authStore.iniciarSesion({
          email: datosFormulario.email,
          password: datosFormulario.password,
          rememberMe: datosFormulario.rememberMe
        })

        if (result.success) {
          toast.success('¡Bienvenido de vuelta!')
          
          // Redirigir según el rol del usuario
          if (authStore.esCreador) {
            await router.push('/dashboard')
          } else if (authStore.esSeguidor) {
            await router.push('/feed')
          } else {
            await router.push('/')
          }
        } else {
          toast.error('❌ Credenciales incorrectas. Verifica tu email y contraseña.')
        }
      } catch (error) {
        toast.error('Error de conexión. Intenta de nuevo.')
      } finally {
        cargandoDatos.value = false
      }
      
      return false
    }

    return {
      datosFormulario,
      erroresValidacion,
      cargandoDatos,
      mostrarContrasena,
      handleLogin
    }
  }
}
</script>

<style lang="scss" scoped>
.login-form {
  width: 100%;
}

.form-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.form-title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
}

.form-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.password-field {
  position: relative;
  width: 100%;

  & .input-field {
  width: 100%;
  padding-right: 50px; /* Espacio para el botón */
  box-sizing: border-box;
  }
}

.password-toggle {
  position: absolute;
  right: 12px; /* Según el padding del input */
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  transition: var(--transition);
  z-index: 2; /* Encima del input */
  padding: 4px; /* Área de click más grande */
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;

  &:hover {
    color: var(--color-primary);
    background-color: rgba(var(--color-primary-rgb), 0.1);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.2);
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

.checkbox-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.form-footer {
  text-align: center;
}

.footer-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.footer-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
  transition: var(--transition);

  &:hover {
    color: var(--color-primary-dark);
    text-decoration: underline;
  }
}

@media (max-width: 768px) {
  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .password-field .input-field {
    padding-right: 45px; /* Menos espacio en móvil */
  }
  
  .password-toggle {
    right: 10px;
    width: 28px;
    height: 28px;
    font-size: var(--font-size-base);
  }
}
</style>
