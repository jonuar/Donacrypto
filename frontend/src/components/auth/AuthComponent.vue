
<!-- Componente para vistas de login y registro -->

<template>
  <div class="auth-layout">
    <div class="auth-container">
      <!-- Lado Izquierdo - Branding y información de la marca -->
      <div class="auth-branding">
        <div class="brand-content">
          <!-- Logo y título principal -->
          <div class="brand-logo">
            <div class="logo-icon">💜</div>
            <h1 class="brand-title">Donaciones<br/>Decentralizadas</h1>
          </div>
          <!-- Descripción de la plataforma -->
          <p class="brand-subtitle">
            Ayuda a crecer a los creadores con donaciones descentralizadas y transparentes
          </p>
          <!-- Grid de características principales -->
          <div class="feature-grid">
            <div class="feature-item">
              <div class="feature-icon">🔗</div>
              <span>Blockchain</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">💫</div>
              <span>Transparente</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <span>Descentralizado</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🔒</div>
              <span>Seguro</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Lado Derecho - Sección del formulario de autenticación -->
      <div class="auth-form-section">
        <div class="auth-form-container">
          <!-- Espacio para el contenido dinámico (LoginView o RegisterView) -->
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<!-- ===== ESTILOS SCOPED DEL COMPONENTE DE AUTENTICACIÓN ===== -->
<style lang="scss" scoped>
/* Contenedor principal que ocupa toda la altura de la ventana */
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); /* Gradiente de fondo */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md); /* Reducimos padding para más espacio */
}

/* Contenedor principal con diseño en grid de dos columnas */
.auth-container {
  background: var(--fondo-tarjeta);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--borde-claro);
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 1fr; /* Dos columnas iguales */
  max-width: 1100px; /* Aumentamos el ancho máximo del contenedor */
  width: 100%;
  min-height: 600px;
}

/* Sección de branding con gradiente púrpura */
.auth-branding {
  background: linear-gradient(135deg, var(--morado-principal) 0%, var(--morado-hover) 100%);
  color: white;
  padding: var(--spacing-2xl);
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
  text-align: center;

  /* Efecto de fondo animado */
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: float 6s ease-in-out infinite; /* Animación flotante */
  }
}

/* Contenido del branding con z-index superior */
.brand-content {
  position: relative;
  z-index: 1; /* Por encima del efecto de fondo */
}

/* Sección del logo y título */
.brand-logo {
  margin-bottom: var(--spacing-xl);
}

/* Icono del logo (emoji) */
.logo-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

/* Título principal de la marca */
.brand-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: var(--spacing-lg);
}

/* Subtítulo descriptivo */
.brand-subtitle {
  font-size: var(--font-size-lg);
  opacity: 0.9; /* Ligeramente transparente */
  line-height: 1.6;
  margin-bottom: var(--spacing-xl);
}

/* Grid de características en 2x2 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); /* Adaptable a diferentes tamaños */
  gap: var(--spacing-lg);
}

/* Elemento individual de característica con efecto glassmorphism */
.feature-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.1); /* Fondo semi-transparente */
  border-radius: var(--radius-md);
  backdrop-filter: blur(10px); /* Efecto de desenfoque */
  transition: var(--transition);

  /* Efecto hover con elevación */
  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
  }
}

/* Icono de la característica */
.feature-icon {
  font-size: var(--font-size-lg);
}

/* Sección del formulario de autenticación */
.auth-form-section {
  padding: var(--spacing-2xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Contenedor del formulario con ancho máximo mejorado */
.auth-form-container {
  width: 100%;
  max-width: 480px; /* Aumentamos el ancho para mejor usabilidad con form-row */
  padding: 0 var(--spacing-sm); /* Añadimos padding interno para evitar overflow */
}

/* Animación flotante para el efecto de fondo */
@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 768px) {
  /* Cambiar a una sola columna en móviles */
  .auth-container {
    grid-template-columns: 1fr;
    max-width: 480px; /* Ancho más amplio en móvil */
    margin: 0 var(--spacing-md); /* Márgenes laterales en móvil */
  }

  /* Reducir padding y altura del branding */
  .auth-branding {
    padding: var(--spacing-xl);
    min-height: 200px;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center
  }

  .brand-content {
    width: 100%;
    max-width: 100%; /* Asegurar que no se corte */
  }

  /* Reducir tamaño del título */
  .brand-title {
    font-size: var(--font-size-2xl);
  }

  .brand-subtitle {
    display: None;
  }

  /* Mantener grid 2x2 pero con menos espacio */
  .feature-grid {
    // grid-template-columns: 1fr;
    // gap: var(--spacing-md);
    display: None;
  }

  /* Reducir padding del formulario */
  .auth-form-section {
    padding: var(--spacing-xl);
  }
}
</style>
