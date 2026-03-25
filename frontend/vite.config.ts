import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/convert': 'http://127.0.0.1:5000',
      '/': {
        target: 'http://127.0.0.1:5000',
        bypass: (request) => {
          const accept = request.headers.accept ?? ''
          if (accept.includes('text/html')) {
            return request.url
          }
          return undefined
        },
      },
    },
  },
})
