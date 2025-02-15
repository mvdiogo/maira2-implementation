import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  proxy: {
    '/generate_report': {
      target: [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8090",
        "https://www.igrejanazareno.com.br",
        "https://xray.igrejanazareno.com.br/",
        "https://xrayrest.igrejanazareno.com.br/",
        "http://xray.igrejanazareno.com.br/",
        "http://xrayrest.igrejanazareno.com.br/"
    ],
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },}
})
