<template>
  <div class="about-page">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">
          <span class="brand-icon">💜</span>
          <span class="brand-text">Decentralized Donations</span>
        </router-link>
        <div class="nav-actions">
          <router-link to="/" class="btn btn-ghost">Volver al Inicio</router-link>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <div class="about-hero">
        <h1>Acerca de Nosotros</h1>
        <p>Construyendo el futuro de las donaciones descentralizadas</p>
      </div>

      <div class="content-section">
        <div class="bento-card">
          <h2>Nuestra Misión</h2>
          <p>
            Democratizar el acceso a las donaciones y crear un ecosistema 
            transparente donde los creadores puedan recibir apoyo directo 
            de su audiencia sin intermediarios.
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<style lang="scss" scoped>
.about-page {
  min-height: 100vh;
  background: var(--color-background);
}

.navbar {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  font-size: var(--font-size-lg);
  color: var(--color-text);
  text-decoration: none;
}

.brand-icon {
  font-size: var(--font-size-xl);
}

.main-content {
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
  .bento-card {
    padding: var(--spacing-xl);

    h2 {
      font-size: var(--font-size-2xl);
      font-weight: 600;
      color: var(--color-text);
      margin-bottom: var(--spacing-lg);
    }

    p {
      font-size: var(--font-size-lg);
      color: var(--color-text-secondary);
      line-height: 1.6;
    }
  }
}
</style>
