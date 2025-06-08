<template>
  <div v-if="mostrar" class="modal-overlay" @click="cerrar">
    <div class="modal-content delete-account-modal" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">⚠️ Eliminar Cuenta</h3>
        <button @click="cerrar" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="warning-message">
          <p><strong>Esta acción es irreversible.</strong></p>
          <p>Se eliminarán permanentemente:</p>
          <ul>
            <li v-if="userRole === 'creator'">Todos tus posts y contenido</li>
            <li v-if="userRole === 'creator'">Tus wallets configuradas</li>
            <li v-if="userRole === 'creator'">Tus seguidores</li>
            <li v-if="userRole === 'follower'">Tus seguimientos a creadores</li>
            <li>Tu perfil y datos personales</li>
            <li>Tu historial en la plataforma</li>
          </ul>
        </div>
        
        <form @submit.prevent="confirmarEliminacion" class="delete-form">
          <div class="form-group">
            <label for="password-confirm" class="form-label">
              Confirma tu contraseña para continuar:
            </label>
            <input
              id="password-confirm"
              v-model="passwordConfirm"
              type="password"
              class="form-input"
              placeholder="Tu contraseña actual"
              required
            />
          </div>
          
          <div class="form-actions">
            <button 
              type="button" 
              @click="cerrar"
              class="btn btn-outline"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              :disabled="procesando || !passwordConfirm"
              class="btn btn-danger"
            >
              <span v-if="procesando">Eliminando...</span>
              <span v-else>Eliminar Cuenta Permanentemente</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'DeleteAccountModal',
  props: {
    mostrar: {
      type: Boolean,
      default: false
    },
    userRole: {
      type: String,
      default: ''
    }
  },
  emits: ['cerrar'],  setup(props, { emit }) {
    const router = useRouter()
    const toast = useToast()
    const authStore = useAuthStore()
    
    const passwordConfirm = ref('')
    const procesando = ref(false)
    
    // Usar la prop userRole directamente o obtener del store como fallback
    const userRole = computed(() => props.userRole || authStore.usuarioActual?.role)
    
    const cerrar = () => {
      passwordConfirm.value = ''
      emit('cerrar')
    }
    
    const confirmarEliminacion = async () => {
      if (!passwordConfirm.value) {
        toast.error('Debes confirmar tu contraseña')
        return
      }
      
      procesando.value = true
      
      try {
        const resultado = await authStore.eliminarCuenta(passwordConfirm.value)
        
        if (resultado.success) {
          toast.success('Cuenta eliminada exitosamente')
          await router.push('/')
        } else {
          toast.error(resultado.error)
        }
      } catch (error) {
        toast.error('Error inesperado al eliminar la cuenta')
      } finally {
        procesando.value = false
      }
    }
    
    return {
      passwordConfirm,
      procesando,
      userRole,
      cerrar,
      confirmarEliminacion
    }
  }
}
</script>

<style lang="scss" scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: var(--radius-lg, 12px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg, 24px);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.modal-title {
  margin: 0;
  color: var(--color-danger, #ef4444);
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-text-secondary, #6b7280);
  
  &:hover {
    color: var(--color-text, #1f2937);
  }
}

.modal-body {
  padding: var(--spacing-lg, 24px);
}

.warning-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md, 8px);
  padding: var(--spacing-lg, 24px);
  margin-bottom: var(--spacing-lg, 24px);
  
  p {
    margin-bottom: var(--spacing-sm, 12px);
    color: var(--color-text, #1f2937);
  }
  
  ul {
    margin-left: var(--spacing-lg, 24px);
    color: var(--color-text-secondary, #6b7280);
    
    li {
      margin-bottom: var(--spacing-xs, 8px);
    }
  }
}

.delete-form {
  .form-group {
    margin-bottom: var(--spacing-lg, 24px);
  }
  
  .form-label {
    display: block;
    margin-bottom: var(--spacing-sm, 12px);
    font-weight: 500;
    color: var(--color-text, #1f2937);
  }
  
  .form-input {
    width: 100%;
    padding: var(--spacing-md, 16px);
    border: 1px solid var(--color-border, #d1d5db);
    border-radius: var(--radius-md, 8px);
    font-size: var(--font-size-base, 16px);
    
    &:focus {
      outline: none;
      border-color: var(--color-primary, #3b82f6);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }
  
  .form-actions {
    display: flex;
    gap: var(--spacing-md, 16px);
    justify-content: flex-end;
  }
}

.btn {
  padding: var(--spacing-md, 16px) var(--spacing-lg, 24px);
  border-radius: var(--radius-md, 8px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-outline {
  background: white;
  color: var(--color-text, #1f2937);
  border-color: var(--color-border, #d1d5db);
  
  &:hover:not(:disabled) {
    background: var(--color-gray-50, #f9fafb);
  }
}

.btn-danger {
  background: var(--color-danger, #ef4444);
  color: white;
  border-color: var(--color-danger, #ef4444);
  
  &:hover:not(:disabled) {
    background: #dc2626;
    border-color: #dc2626;
  }
}

@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }
  
  .modal-content {
    margin: var(--spacing-md, 16px);
  }
}
</style>
