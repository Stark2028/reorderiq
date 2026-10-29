import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/assets/ui/',
  build: {
    outDir: '../src/reorderiq/web/ui',
    emptyOutDir: true,
    sourcemap: false,
    target: 'es2022',
  },
  server: {
    host: '127.0.0.1',
    port: 3010,
    strictPort: true,
    proxy: { '/api': 'http://127.0.0.1:8010', '/assets/fonts': 'http://127.0.0.1:8010' },
  },
});
