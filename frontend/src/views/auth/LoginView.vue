<!-- ===== VISTA DE INICIO DE SESIÓN ==            <button
              @click="mostrarContrasena = !mostrarContrasena"
              class="password-toggle"
            >
              <span v-if="mostrarContrasena">👁️</span>
              <span v-else>👁️‍🗨️</span>
            </button>
<!-- Formulario de login con validación y manejo de errores -->
<template>
  <AuthComponent>
    <div class="login-form">      <div class="form-header">
        <!-- Botón para volver al inicio -->
        <router-link to="/" class="back-to-home">
          <span class="back-icon">←</span>
          Volver al Inicio
        </router-link>
        <h2 class="form-title">¡Bienvenido de vuelta!</h2>
        <p class="form-subtitle">Inicia sesión para continuar con tu cuenta</p>
      </div>

      <form @submit.prevent="handleLogin" class="form">        <div class="input-group">
          <label for="email" class="input-label">Correo electrónico</label>
          <input
            id="email"
            v-model="datosFormulario.email"
            type="email"
            class="input-field"
            :class="{ 'input-error': erroresValidacion.email }"
            placeholder="tu@email.com"
            required
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
              required
            />
            <button
              type="button"
              @click="mostrarContrasena = !mostrarContrasena"
              class="password-toggle"
            >
              <span v-if="mostrarContrasena">👁️</span>
              <span v-else>🙈</span>
            </button>
          </div>
          <span v-if="erroresValidacion.password" class="input-error-text">{{ erroresValidacion.password }}</span>
        </div>        <div class="form-options">
          <label class="checkbox-group">
            <input v-model="datosFormulario.rememberMe" type="checkbox" class="checkbox" />
            <span class="checkbox-label">Recordarme</span>
          </label>
          <router-link to="/forgot-password" class="forgot-link">
            ¿Olvidaste tu contraseña?
          </router-link>
        </div>

        <button
          type="submit"
          :disabled="cargandoDatos"
          class="btn btn-primary btn-lg w-full"
        >
          <span v-if="cargandoDatos" class="spinner"></span>
          <span v-else>Iniciar Sesión</span>
        </button>

        <div v-if="erroresValidacion.general" class="error-message">
          {{ erroresValidacion.general }}
        </div>
      </form>

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

<!-- ===== LÓGICA DEL COMPONENTE ===== -->
<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import AuthComponent from '@/components/auth/AuthComponent.vue'

export default {
  name: 'LoginView',
  components: {
    AuthComponent // Cambiado de AuthLayout a AuthComponent
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
      password: '',
      general: ''
    })    // Función para limpiar todos los errores
    const clearErrors = () => {
      erroresValidacion.email = ''
      erroresValidacion.password = ''
      erroresValidacion.general = ''
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
      if (!validateForm()) return

      cargandoDatos.value = true
      clearErrors()

      try {
        const result = await authStore.iniciarSesion({
          email: datosFormulario.email,
          password: datosFormulario.password,
          rememberMe: datosFormulario.rememberMe
        })

        if (result.success) {
          toast.success('¡Bienvenido de vuelta!')
          
          // Redirigir según el rol del usuario
          if (authStore.esCreador) {
            router.push('/dashboard')
          } else if (authStore.esSeguidor) {
            router.push('/feed')
          } else {
            router.push('/')
          }
        } else {
          erroresValidacion.general = result.error || 'Error al iniciar sesión'
          toast.error(erroresValidacion.general)
        }
      } catch (error) {
        erroresValidacion.general = 'Error de conexión. Intenta de nuevo.'
        toast.error(erroresValidacion.general)
      } finally {
        cargandoDatos.value = false
      }
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
}

.password-toggle {
  position: absolute;
  right: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-lg);
  color: var(--color-text-muted);
  transition: var(--transition);

  &:hover {
    color: var(--color-primary);
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

.forgot-link {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  text-decoration: none;
  transition: var(--transition);

  &:hover {
    color: var(--color-primary-dark);
    text-decoration: underline;
  }
}

.error-message {
  padding: var(--spacing-md);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-md);
  color: var(--color-error);
  font-size: var(--font-size-sm);
  text-align: center;
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
}
</style>
