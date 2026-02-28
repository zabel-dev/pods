import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/subtitles': 'http://127.0.0.1:8000',
      '/subtitles-both': 'http://127.0.0.1:8000',
      '/summary': 'http://127.0.0.1:8000',
      '/history': 'http://127.0.0.1:8000',
      '/video-info': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000',
    },
  },
})
