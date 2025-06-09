<template>
  <div class="about-page">
    <!-- Navbar para usuarios no autenticados -->
    <nav class="navbar" v-if="!authStore.estaAutenticado">
      <div class="nav-container">
        <div class="nav-brand">
          <router-link to="/" class="brand-link">
            <span class="brand-icon">💜</span>
            <span class="brand-text">DonaCrypto</span>
          </router-link>
        </div>
        <div class="nav-actions">
          <router-link to="/" class="btn btn-ghost">
            Inicio
          </router-link>
          <router-link to="/login" class="btn btn-ghost">
            Iniciar sesión
          </router-link>
          <router-link to="/register" class="btn btn-primary">
            Registrarse
          </router-link>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <div class="about-hero">
        <h1>Acerca de Nosotros</h1>
        <p>Construyendo el futuro de las donaciones 100% descentralizadas</p>
      </div>

      <div class="content-section">
        <!-- Resto del contenido igual -->
        <div class="bento-card">
          <h2>Nuestra Misión</h2>
          <p>
            Crear una plataforma verdaderamente descentralizada donde los creadores 
            reciban donaciones directamente en sus wallets de criptomonedas, 
            sin intermediarios, sin comisiones y con total privacidad.
          </p>
        </div>

        <div class="bento-card">
          <h2>¿Por qué Descentralizado?</h2>
          <div class="benefits-list">
            <div class="benefit-item">
              <div class="benefit-icon">🔒</div>
              <div class="benefit-text">
                <h4>Verdaderamente Descentralizado</h4>
                <p>Sin intermediarios - Las donaciones van directamente a las wallets de los creadores</p>
              </div>
            </div>
            
            <div class="benefit-item">
              <div class="benefit-icon">💰</div>
              <div class="benefit-text">
                <h4>Sin Comisiones de Plataforma</h4>
                <p>100% de las donaciones van directamente para los creadores. Cero comisiones</p>
              </div>
            </div>
            
            <div class="benefit-item">
              <div class="benefit-icon">🔐</div>
              <div class="benefit-text">
                <h4>Privacidad Máxima</h4>
                <p>No se requiere KYC. Mantén tu anonimato y privacidad en todas las transacciones</p>
              </div>
            </div>
            
            <div class="benefit-item">
              <div class="benefit-icon">🌍</div>
              <div class="benefit-text">
                <h4>Acceso Global</h4>
                <p>Funciona en cualquier país sin restricciones geográficas o bancarias</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bento-card">
          <h2>¿Cómo Funciona?</h2>
          <div class="steps-list">
            <div class="step-item">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>Regístrate como Creador</h4>
                <p>Crea tu perfil y configura tus wallets de criptomonedas (24 criptomonedas soportadas: BTC, ETH, BNB, ADA, SOL, USDT, USDC y más)</p>
              </div>
            </div>
            
            <div class="step-item">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>Comparte tu Perfil</h4>
                <p>Comparte tu enlace y códigos QR con tu audiencia</p>
              </div>
            </div>
            
            <div class="step-item">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>Recibe Donaciones Directas</h4>
                <p>Las donaciones van directamente a tus wallets sin pasar por la plataforma</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer para usuarios no autenticados -->
    <footer class="footer" v-if="!authStore.estaAutenticado">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-links">
            <router-link to="/" class="footer-link">Inicio</router-link>
            <router-link to="/login" class="footer-link">Iniciar sesión</router-link>
            <router-link to="/register" class="footer-link">Registrarse</router-link>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2024 DonaCrypto. Plataforma de donaciones descentralizada.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AboutView',
  setup() {
    const authStore = useAuthStore()
    
    return {
      authStore
    }
  }
}
</script>

<style lang="scss" scoped>
.about-page {
  min-height: 100vh;
  background: var(--color-background);
  display: flex;
  flex-direction: column;
}

/* Navbar styles */
.navbar {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-md) 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
  color: var(--color-text);
  font-weight: 600;
  font-size: var(--font-size-lg);
}

.brand-icon {
  font-size: 1.5rem;
}

.nav-actions {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

.btn-ghost:hover {
  background: var(--color-background);
  color: var(--color-text);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

/* Footer styles */
.footer {
  background: var(--color-surface);
  border-top: 1px solid var(--color-border-light);
  margin-top: auto;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.footer-brand {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: var(--spacing-sm);
  font-weight: 600;
  font-size: var(--font-size-lg);
  color: var(--color-text);
  
}

.footer-links {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
  justify-content: center;
  width: 100%;
}

.footer-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: var(--color-primary);
}

.footer-bottom {
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
  text-align: center;
}

.footer-bottom p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.main-content {
  flex: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-lg);
}

.about-hero {
  text-align: center;
  margin-bottom: var(--spacing-2xl);

  h1 {
    font-size: var(--font-size-4xl);
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: var(--spacing-md);
  }

  p {
    font-size: var(--font-size-xl);
    color: var(--color-text-secondary);
  }
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.bento-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.benefits-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.benefit-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.benefit-text h4 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text);
}

.benefit-text p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text);
}

.step-content p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 var(--spacing-md);
  }
  
  .nav-actions {
    gap: var(--spacing-sm);
  }
  
  .btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
  
  .footer-content {
    flex-direction: column;
    gap: var(--spacing-md);
    text-align: center;
  }
  
  .footer-links {
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--spacing-md);
  }
  
  .benefit-item,
  .step-item {
    flex-direction: column;
    text-align: center;
  }
  
  .step-number {
    align-self: center;
  }
}
</style>
