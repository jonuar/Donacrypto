import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// ===== CONFIGURACIÓN DE VITE ===== 
// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // ===== CONFIGURACIÓN DE SASS =====
  css: {
    preprocessorOptions: {
      scss: {
        // Usar la API moderna de Sass para eliminar warnings
        api: 'modern-compiler',
        // Configuración adicional para compatibilidad
        charset: false,
        // Silenciar warnings específicos de deprecación
        silenceDeprecations: ['legacy-js-api', 'import', 'global-builtin', 'mixed-decls'],
        // Configurar el compilador moderno
        modernCompilerOptions: {
          style: 'expanded'
        }
      }
    }
  },
  // ===== CONFIGURACIÓN DE BUILD PARA PRODUCCIÓN =====
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['vue-toastification'],
          utils: ['axios', 'qrcode']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  // ===== CONFIGURACIÓN DEL SERVIDOR DE DESARROLLO =====
  server: {
    port: 3000,        // Puerto específico para el frontend
    host: true,        // Permite acceso desde la red local
    open: true,        // Abre automáticamente el navegador
    strictPort: true,  // Falla si el puerto no está disponible
  },
  // ===== CONFIGURACIÓN PARA PREVIEW =====
  preview: {
    port: 4173,
    host: true
  }
})
