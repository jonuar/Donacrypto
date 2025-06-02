<template>
  <div class="follower-profile">
    <div class="profile-header">
      <h1 class="page-title">⚙️ Mi Perfil</h1>
      <p class="page-subtitle">Gestiona tu información personal</p>
    </div>

    <!-- Loading state -->
    <div v-if="cargandoPerfil" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando tu perfil...</p>
    </div>

    <!-- Profile form -->
    <div v-else class="profile-content">
      <form @submit.prevent="actualizarPerfil" class="profile-form">
        <!-- Avatar -->
        <div class="form-group avatar-group">
          <label class="form-label">Avatar</label>
          <div class="avatar-section">
            <div class="avatar-preview">
              <img 
                v-if="perfil.avatar_url" 
                :src="perfil.avatar_url" 
                :alt="perfil.username"
                class="avatar-image"
              />
              <div v-else class="avatar-placeholder">
                {{ perfil.username ? perfil.username.charAt(0).toUpperCase() : '👤' }}
              </div>
            </div>
            <div class="avatar-input">
              <input
                v-model="perfil.avatar_url"
                type="url"
                placeholder="URL de tu avatar (opcional)"
                class="form-input"
              />
              <small class="form-help">Proporciona una URL de imagen para tu avatar</small>
            </div>
          </div>
        </div>

        <!-- Username -->
        <div class="form-group">
          <label for="username" class="form-label">Nombre de usuario</label>
          <input
            id="username"
            v-model="perfil.username"
            type="text"
            required
            maxlength="30"
            class="form-input"
            placeholder="Tu nombre de usuario único"
          />
        </div>

        <!-- Email (readonly) -->
        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            v-model="perfil.email"
            type="email"
            readonly
            class="form-input readonly"
          />
          <small class="form-help">El email no se puede modificar</small>
        </div>

        <!-- Bio (opcional para followers) -->
        <div class="form-group">
          <label for="bio" class="form-label">Biografía (opcional)</label>
          <textarea
            id="bio"
            v-model="perfil.bio"
            maxlength="200"
            rows="3"
            class="form-textarea"
            placeholder="Cuéntanos algo sobre ti (opcional)"
          ></textarea>
          <small class="form-help">{{ perfil.bio ? perfil.bio.length : 0 }}/200 caracteres</small>
        </div>

        <!-- Action buttons -->
        <div class="form-actions">
          <button 
            type="submit" 
            :disabled="guardandoPerfil"
            class="btn btn-primary"
          >
            <span v-if="guardandoPerfil">💾 Guardando...</span>
            <span v-else>💾 Guardar Cambios</span>
          </button>
          
          <button 
            type="button" 
            @click="cancelarEdicion"
            class="btn btn-outline"
          >
            🚫 Cancelar
          </button>
        </div>
      </form>

      <!-- Additional sections -->
      <div class="profile-stats">
        <h3>📊 Estadísticas</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ estadisticas.siguiendo }}</div>
            <div class="stat-label">Siguiendo</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ estadisticas.miembro_desde }}</div>
            <div class="stat-label">Miembro desde</div>
          </div>
        </div>
      </div>

      <!-- Change password section -->
      <div class="password-section">
        <h3>🔒 Cambiar Contraseña</h3>
        <form @submit.prevent="cambiarContrasena" class="password-form">
          <div class="form-group">
            <label for="current-password" class="form-label">Contraseña actual</label>
            <input
              id="current-password"
              v-model="password.actual"
              type="password"
              required
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="new-password" class="form-label">Nueva contraseña</label>
            <input
              id="new-password"
              v-model="password.nueva"
              type="password"
              required
              minlength="6"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="confirm-password" class="form-label">Confirmar nueva contraseña</label>
            <input
              id="confirm-password"
              v-model="password.confirmar"
              type="password"
              required
              class="form-input"
            />
          </div>
          
          <button 
            type="submit" 
            :disabled="cambiandoPassword"
            class="btn btn-secondary"
          >
            <span v-if="cambiandoPassword">🔄 Cambiando...</span>
            <span v-else">🔒 Cambiar Contraseña</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

const router = useRouter()
const toast = useToast()

// Estados reactivos
const cargandoPerfil = ref(true)
const guardandoPerfil = ref(false)
const cambiandoPassword = ref(false)

// Datos del perfil
const perfil = reactive({
  username: '',
  email: '',
  avatar_url: '',
  bio: '',
  role: '',
  created_at: ''
})

// Datos originales para cancelar
const perfilOriginal = reactive({})

// Estadísticas
const estadisticas = reactive({
  siguiendo: 0,
  miembro_desde: ''
})

// Datos de contraseña
const password = reactive({
  actual: '',
  nueva: '',
  confirmar: ''
})

// Métodos
const cargarPerfil = async () => {
  cargandoPerfil.value = true
  try {
    const response = await api.get('/user/profile')
    
    Object.assign(perfil, response.data)
    Object.assign(perfilOriginal, response.data)
    
    // Formatear fecha de miembro
    if (perfil.created_at) {
      estadisticas.miembro_desde = new Date(perfil.created_at).getFullYear()
    }
    
    // Obtener estadísticas de seguimiento
    await cargarEstadisticas()
    
  } catch (error) {
    console.error('Error al cargar perfil:', error)
    toast.error('No se pudo cargar tu perfil')
    
    if (error.response?.status === 401) {
      router.push('/login')
    }
  } finally {
    cargandoPerfil.value = false
  }
}

const cargarEstadisticas = async () => {
  try {
    const response = await api.get('/user/following')
    estadisticas.siguiendo = response.data.count || 0
  } catch (error) {
    console.error('Error al cargar estadísticas:', error)
  }
}

const actualizarPerfil = async () => {
  guardandoPerfil.value = true
  
  try {
    // Validaciones
    if (!perfil.username.trim()) {
      toast.error('El nombre de usuario es requerido')
      return
    }
    
    if (perfil.username.length < 3) {
      toast.error('El nombre de usuario debe tener al menos 3 caracteres')
      return
    }
    
    // Preparar datos para enviar
    const datosActualizacion = {
      username: perfil.username.trim(),
      avatar_url: perfil.avatar_url.trim(),
      bio: perfil.bio.trim()
    }
    
    const response = await api.put('/user/update-profile', datosActualizacion)
    
    toast.success('✅ Perfil actualizado con éxito')
    
    // Actualizar datos originales
    Object.assign(perfilOriginal, perfil)
    
  } catch (error) {
    console.error('Error al actualizar perfil:', error)
    
    if (error.response?.status === 409) {
      toast.error('❌ El nombre de usuario ya está en uso')
    } else if (error.response?.status === 401) {
      toast.error('❌ Sesión expirada')
      router.push('/login')
    } else {
      toast.error('❌ Error al actualizar el perfil')
    }
  } finally {
    guardandoPerfil.value = false
  }
}

const cancelarEdicion = () => {
  Object.assign(perfil, perfilOriginal)
  toast.info('ℹ️ Cambios cancelados')
}

const cambiarContrasena = async () => {
  if (password.nueva !== password.confirmar) {
    toast.error('❌ Las contraseñas no coinciden')
    return
  }
  
  if (password.nueva.length < 6) {
    toast.error('❌ La nueva contraseña debe tener al menos 6 caracteres')
    return
  }
  
  cambiandoPassword.value = true
  
  try {
    await api.put('/user/change-password', {
      current_password: password.actual,
      new_password: password.nueva
    })
    
    toast.success('✅ Contraseña cambiada con éxito')
    
    // Limpiar formulario
    password.actual = ''
    password.nueva = ''
    password.confirmar = ''
    
  } catch (error) {
    console.error('Error al cambiar contraseña:', error)
    
    if (error.response?.status === 400) {
      toast.error('❌ La contraseña actual es incorrecta')
    } else if (error.response?.status === 401) {
      toast.error('❌ Sesión expirada')
      router.push('/login')
    } else {
      toast.error('❌ Error al cambiar la contraseña')
    }
  } finally {
    cambiandoPassword.value = false
  }
}

// Lifecycle
onMounted(() => {
  cargarPerfil()
})
</script>

<style scoped>
.follower-profile {
  min-height: 100vh;
  background: var(--color-background);
  padding: var(--spacing-lg);
}

.profile-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--font-size-xxl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-light);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xxl);
  gap: var(--spacing-lg);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.profile-content {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.profile-form {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.avatar-group {
  margin-bottom: var(--spacing-lg);
}

.avatar-section {
  display: flex;
  gap: var(--spacing-lg);
  align-items: flex-start;
}

.avatar-preview {
  flex-shrink: 0;
}

.avatar-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--color-border);
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.avatar-input {
  flex: 1;
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-label {
  display: block;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-md);
  background: var(--color-background);
  color: var(--color-text);
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.form-input.readonly {
  background: var(--color-border-light);
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-help {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  margin-top: var(--spacing-xs);
  display: block;
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.btn {
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-secondary {
  background: var(--color-secondary);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-secondary-dark);
}

.btn-outline {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-outline:hover:not(:disabled) {
  background: var(--color-border-light);
}

.profile-stats {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.profile-stats h3 {
  margin-bottom: var(--spacing-lg);
  color: var(--color-text);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-lg);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-lg);
  background: var(--color-background);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border-light);
}

.stat-number {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.password-section {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.password-section h3 {
  margin-bottom: var(--spacing-lg);
  color: var(--color-text);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .follower-profile {
    padding: var(--spacing-md);
  }
  
  .avatar-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
