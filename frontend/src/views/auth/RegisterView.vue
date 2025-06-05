<!-- ===== VISTA DE REGISTRO ===== -->
<!-- Formulario de registro con selección de rol y validación completa -->
<template>
  <AuthComponent>
    <div class="register-form">
      <div class="form-header">
        <!-- Botón para volver al inicio -->
        <router-link to="/" class="back-to-home">
          <span class="back-icon">←</span>
          Volver al Inicio
        </router-link>
        <h2 class="form-title">¡Únete a nosotros!</h2>
        <p class="form-subtitle">Crea tu cuenta y comienza tu experiencia descentralizada</p>
      </div>

      <form @submit.prevent="manejarRegistro" class="form">
        <!-- Selección de tipo de usuario -->
        <div class="input-group">
          <label class="input-label">Tipo de cuenta</label>
          <div class="role-selector">
            <div 
              class="role-option"
              :class="{ active: datosFormulario.role === 'creator' }"
              @click="datosFormulario.role = 'creator'"
            >
              <div class="role-icon">🎨</div>
              <div class="role-content">
                <h4>Creador</h4>
                <p>Recibe donaciones por tu contenido</p>
              </div>
            </div>
            <div 
              class="role-option"
              :class="{ active: datosFormulario.role === 'follower' }"
              @click="datosFormulario.role = 'follower'"
            >
              <div class="role-icon">❤️</div>
              <div class="role-content">
                <h4>Seguidor</h4>
                <p>Apoya a tus creadores favoritos</p>
              </div>
            </div>
          </div>
          <span v-if="erroresValidacion.role" class="input-error-text">{{ erroresValidacion.role }}</span>
        </div>

        <!-- Información personal -->
        <div class="form-row">
          <div class="input-group">
            <label for="firstName" class="input-label">Nombre</label>
            <input
              id="firstName"
              v-model="datosFormulario.firstName"
              type="text"
              class="input-field"
              :class="{ 'input-error': erroresValidacion.firstName }"
              placeholder="Tu nombre"
              required
            />
            <span v-if="erroresValidacion.firstName" class="input-error-text">{{ erroresValidacion.firstName }}</span>
          </div>

          <div class="input-group">
            <label for="lastName" class="input-label">Apellido</label>
            <input
              id="lastName"
              v-model="datosFormulario.lastName"
              type="text"
              class="input-field"
              :class="{ 'input-error': erroresValidacion.lastName }"
              placeholder="Tu apellido"
              required
            />
            <span v-if="erroresValidacion.lastName" class="input-error-text">{{ erroresValidacion.lastName }}</span>
          </div>
        </div>

        <!-- Username -->
        <div class="input-group">
          <label for="username" class="input-label">Nombre de usuario</label>
          <input
            id="username"
            v-model="datosFormulario.username"
            type="text"
            class="input-field"
            :class="{ 'input-error': erroresValidacion.username }"
            placeholder="@tu_usuario"
            required
          />
          <span v-if="erroresValidacion.username" class="input-error-text">{{ erroresValidacion.username }}</span>
        </div>

        <!-- Email -->
        <div class="input-group">
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
        </div>

        <!-- Password -->
        <div class="input-group">
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
        </div>

        <!-- Confirm Password -->
        <!-- <div class="input-group">
          <label for="confirmPassword" class="input-label">Confirmar contraseña</label>
          <div class="password-field">
            <input
              id="confirmPassword"
              v-model="datosFormulario.confirmPassword"
              :type="mostrarConfirmacionContrasena ? 'text' : 'password'"
              class="input-field"
              :class="{ 'input-error': erroresValidacion.confirmPassword }"
              placeholder="••••••••"
              required
            />
            <button
              type="button"
              @click="mostrarConfirmacionContrasena = !mostrarConfirmacionContrasena"
              class="password-toggle"
            >
              <span v-if="mostrarConfirmacionContrasena">👁️</span>
              <span v-else>🙈</span>
            </button>
          </div>
          <span v-if="erroresValidacion.confirmPassword" class="input-error-text">{{ erroresValidacion.confirmPassword }}</span>
        </div> -->

        <!-- Terms and conditions -->
        <div class="input-group">
          <label class="checkbox-group">
            <input v-model="datosFormulario.acceptTerms" type="checkbox" class="checkbox" />
            <span class="checkbox-label">
              Acepto los <a href="#" class="terms-link">Términos y Condiciones</a> 
              y la <a href="#" class="terms-link">Política de Privacidad</a>
            </span>
          </label>
          <span v-if="erroresValidacion.acceptTerms" class="input-error-text">{{ erroresValidacion.acceptTerms }}</span>
        </div>

        <button
          type="submit"
          :disabled="cargandoDatos"
          class="btn btn-primary btn-lg w-full"
        >
          <span v-if="cargandoDatos" class="spinner"></span>
          <span v-else>Crear Cuenta</span>
        </button>

        <div v-if="erroresValidacion.general" class="error-message">
          {{ erroresValidacion.general }}
        </div>
      </form>

      <div class="form-footer">
        <p class="footer-text">
          ¿Ya tienes una cuenta?
          <router-link to="/login" class="footer-link">
            Inicia sesión aquí
          </router-link>
        </p>
      </div>
    </div>
  </AuthComponent>
</template>

<!-- ===== LÓGICA DEL COMPONENTE DE REGISTRO ===== -->
<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import AuthComponent from '@/components/auth/AuthComponent.vue'

export default {
  name: 'RegisterView',
  components: {
    AuthComponent
  },
  setup() {
    const router = useRouter()
    const toast = useToast()
    const authStore = useAuthStore()

    // Estados reactivos para controlar la UI
    const cargandoDatos = ref(false)
    const mostrarContrasena = ref(false)
    const mostrarConfirmacionContrasena = ref(false)

    const datosFormulario = reactive({
      role: 'follower',
      firstName: '',
      lastName: '',
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false
    })

    const erroresValidacion = reactive({
      role: '',
      firstName: '',
      lastName: '',
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: '',
      general: ''
    })

    const limpiarErrores = () => {
      Object.keys(erroresValidacion).forEach(key => {
        erroresValidacion[key] = ''
      })
    }

    const validarFormulario = () => {
      limpiarErrores()
      let esValido = true

      if (!datosFormulario.role) {
        erroresValidacion.role = 'Selecciona un tipo de cuenta'
        esValido = false
      }

      if (!datosFormulario.firstName.trim()) {
        erroresValidacion.firstName = 'El nombre es requerido'
        esValido = false
      }

      if (!datosFormulario.lastName.trim()) {
        erroresValidacion.lastName = 'El apellido es requerido'
        esValido = false
      }

      if (!datosFormulario.username.trim()) {
        erroresValidacion.username = 'El nombre de usuario es requerido'
        esValido = false
      } else if (datosFormulario.username.length < 5) {
        erroresValidacion.username = 'El nombre de usuario debe tener al menos 5 caracteres'
        esValido = false
      }

      if (!datosFormulario.email) {
        erroresValidacion.email = 'El correo electrónico es requerido'
        esValido = false
      } else if (!/\S+@\S+\.\S+/.test(datosFormulario.email)) {
        erroresValidacion.email = 'Ingresa un correo electrónico válido'
        esValido = false
      }

      if (!datosFormulario.password) {
        erroresValidacion.password = 'La contraseña es requerida'
        esValido = false
      } else if (datosFormulario.password.length < 6) {
        erroresValidacion.password = 'La contraseña debe tener al menos 6 caracteres'
        esValido = false
      }

      if (!datosFormulario.confirmPassword) {
        erroresValidacion.confirmPassword = 'Confirma tu contraseña'
        esValido = false
      } else if (datosFormulario.password !== datosFormulario.confirmPassword) {
        erroresValidacion.confirmPassword = 'Las contraseñas no coinciden'
        esValido = false
      }

      if (!datosFormulario.acceptTerms) {
        erroresValidacion.acceptTerms = 'Debes aceptar los términos y condiciones'
        esValido = false
      }

      return esValido
    }

    const manejarRegistro = async () => {
      if (!validarFormulario()) return

      cargandoDatos.value = true
      limpiarErrores()

      try {
        const resultado = await authStore.registrarUsuario({
          first_name: datosFormulario.firstName,
          last_name: datosFormulario.lastName,
          username: datosFormulario.username,
          email: datosFormulario.email,
          password: datosFormulario.password,
          role: datosFormulario.role
        })

        if (resultado.success) {
          toast.success('¡Cuenta creada exitosamente! Por favor inicia sesión.')
          router.push('/login')
        } else {
          erroresValidacion.general = resultado.error || 'Error al crear la cuenta'
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
      mostrarConfirmacionContrasena,
      manejarRegistro
    }
  }
}
</script>

<style lang="scss" scoped>
// Reutilizamos los mismos estilos del componente original
@use '@/assets/styles/style.scss';

.register-form {
  width: 100%;
}

.form-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.back-to-home {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-decoration: none;
  margin-bottom: var(--spacing-md);
  transition: var(--transition);

  &:hover {
    color: var(--color-primary);
  }
}

.back-icon {
  font-size: var(--font-size-lg);
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

.form-row {
  display: grid;
  // grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.role-option {
  padding: var(--spacing-md);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);

  &:hover {
    border-color: var(--color-primary-light);
    background: rgba(139, 92, 246, 0.05);
  }

  &.active {
    border-color: var(--color-primary);
    background: rgba(139, 92, 246, 0.1);
  }
}

.role-icon {
  font-size: var(--font-size-xl);
}

.role-content {
  h4 {
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 2px;
  }

  p {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    line-height: 1.3;
  }
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

.checkbox-group {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
  margin-top: 2px;
}

.checkbox-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.terms-link {
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
  .form-row {
    grid-template-columns: 1fr;
  }

  .role-selector {
    grid-template-columns: 1fr;
  }

  .role-option {
    text-align: center;
    flex-direction: column;
    gap: var(--spacing-xs);
  }
}
</style>