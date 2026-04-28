import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 4173,
  },
  preview: {
    allowedHosts: ['stewbeet.paralya.fr'],
  },
  build: {
    minify: false,
  },
})
