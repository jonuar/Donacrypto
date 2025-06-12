<template>
    <div class="not-found-page">
        <div class="not-found-container">
            <div class="error-content">
                <div class="error-icon">404</div>
                <h1 class="error-title">¡Oops! Página no encontrada</h1>
                <p class="error-message">
                    Lo sentimos, la página que estás buscando no existe o ha sido movida.
                </p>
                <div class="error-actions">
                    <router-link to="/" class="btn btn-primary">
                        Volver al Inicio
                    </router-link>
                    <button @click="$router.go(-1)" class="btn btn-outline">
                        Volver Atrás
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.not-found-page {
    min-height: 100vh;
    background: var(--color-background);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
}

.not-found-container {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    padding: var(--spacing-2xl);
    max-width: 500px;
    width: 100%;
    text-align: center;
    border: 1px solid var(--color-border-light);
}

.error-icon {
    font-size: 6rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: var(--spacing-lg);
    line-height: 1;
    background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.error-title {
    font-size: var(--font-size-2xl);
    color: var(--color-text);
    margin-bottom: var(--spacing-md);
}

.error-message {
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-xl);
}

.error-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
}

@media (max-width: 480px) {
    .not-found-container {
        padding: var(--spacing-xl);
    }

    .error-icon {
        font-size: 4rem;
    }

    .error-title {
        font-size: var(--font-size-xl);
    }

    .error-actions {
        flex-direction: column;
        gap: var(--spacing-sm);
    }

    .btn {
        width: 100%;
    }
}
</style>