import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// ===== CONFIGURACIÓN DE VITE ===== 
// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
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
    minify: true,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
//   // ===== CONFIGURACIÓN DEL SERVIDOR DE DESARROLLO =====
//   server: {
//     port: 3000,        // Puerto específico para el frontend
//     host: true,        // Permite acceso desde la red local
//     open: true,        // Abre automáticamente el navegador
//     strictPort: true,  // Falla si el puerto no está disponible
//   },
//   // ===== CONFIGURACIÓN PARA PREVIEW =====
//   preview: {
//     port: 4173,
//     host: true
//   }
// Configuración específica para SPA
  server: {
    port: 3000,
    strictPort: true,
    historyApiFallback: true
  }
})
