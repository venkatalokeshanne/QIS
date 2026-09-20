import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // listen on the LAN too, so phones/tablets on the same Wi-Fi can open it;
    // /api is proxied from here, so only this port needs to be reachable
    host: true,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
