import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  define: {
    global: 'globalThis',
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api/blockscout': {
        target: 'https://explorer-1205614515668104.devnet.alchemy.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/blockscout/, ''),
        secure: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
}) 