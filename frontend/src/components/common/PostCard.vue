<template>
  <article class="post-card">
    <header class="post-header">
      <div class="post-meta">
        <div class="creator-info" v-if="showCreator">
          <img 
            :src="post.creator_avatar || '/placeholder-avatar.png'" 
            :alt="post.creator_username"
            class="creator-avatar"
          >
          <div class="creator-details">
            <h4 class="creator-name">@{{ post.creator_username }}</h4>
            <time class="post-date">{{ formatearFecha(post.created_at) }}</time>
          </div>
        </div>
        <div class="post-actions" v-if="showActions">
          <button 
            @click="$emit('delete', post._id)" 
            class="btn-icon btn-danger"
            title="Eliminar post"
          >
            ×
          </button>
        </div>
      </div>
      <h2 class="post-title">{{ post.title }}</h2>
    </header>
    
    <div class="post-content">
      <p>{{ post.content }}</p>
    </div>
      <footer class="post-footer">
      <div class="post-stats">
        <button 
          v-if="showInteractions" 
          @click="$emit('like', post)"
          class="stat-item interaction-btn like-btn" 
          :class="{ liked: post.liked }"
        >
          <span class="stat-icon">❤️</span>
          <span class="stat-count">{{ post.likes_count || 0 }}</span>
        </button>
        <span v-else class="stat-item">
          <span class="stat-icon">❤️</span>
          <span class="stat-count">{{ post.likes_count || 0 }}</span>
        </span>
        <time class="post-timestamp" v-if="!showCreator">
          {{ formatearFecha(post.created_at) }}
        </time>
      </div>
    </footer>
  </article>
</template>

<script>
export default {
  name: 'PostCard',  props: {
    post: {
      type: Object,
      required: true
    },
    showCreator: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: false
    },
    showInteractions: {
      type: Boolean,
      default: false
    }
  },
  emits: ['delete', 'like'],  methods: {
    formatearFecha(fecha) {
      if (!fecha) {
        return 'Fecha no disponible'
      }
      
      const now = new Date()
      const postDate = new Date(fecha)
      
      // Verificar si la fecha es válida
      if (isNaN(postDate.getTime())) {
        return 'Fecha inválida'
      }
      
      const diffTime = Math.abs(now - postDate)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) {
        return 'Hace 1 día'
      } else if (diffDays < 7) {
        return `Hace ${diffDays} días`
      } else {
        return postDate.toLocaleDateString('es-ES', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.post-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--color-border);
  }
}

.post-header {
  margin-bottom: var(--spacing-md);
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-sm);
}

.creator-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.creator-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border-light);
}

.creator-details {
  display: flex;
  flex-direction: column;
}

.creator-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-primary);
  margin: 0;
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
}

.post-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.post-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.btn-icon {
  background: none;  border: none;
  padding: var(--spacing-xs);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background-color 0.2s;
  
  &:hover {
    background: var(--color-background);
  }
  
  &.btn-danger:hover {
    background: rgba(239, 68, 68, 0.1);
  }
}

.post-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  line-height: 1.3;
}

.post-content {
  margin-bottom: var(--spacing-md);
}

.post-content p {
  color: var(--color-text);
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.post-footer {
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-light);
}

.post-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  
  &.interaction-btn {
    background: none;
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    padding: var(--spacing-xs);
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      background: var(--color-border-light);
      border-color: var(--color-border);
    }
    
    &.liked {
      color: var(--color-error);
      border-color: var(--color-error);
      background: rgba(239, 68, 68, 0.1);
    }
  }
}

.stat-icon {
  font-size: var(--font-size-base);
}

.post-timestamp {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .post-card {
    padding: var(--spacing-md);
  }
  
  .creator-info {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }
  
  .creator-avatar {
    width: 32px;
    height: 32px;
  }
  
  .post-stats {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }
}
</style>
