import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';

export default defineConfig({
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  base: './',
  plugins: [vue()],
  server: {
    host: 'localhost',
    port: 9595,
    watch: {
      ignored: ['node_modules'],
    },
  },
  preview: {
    port: 9595, // preview 端口（和 dev 一致）
  },
  build: {
    chunkSizeWarningLimit: 1000
  }

});
