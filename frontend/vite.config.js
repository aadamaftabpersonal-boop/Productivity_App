import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react' // (or vue, etc., depending on your framework)
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(), // Add this line right here
  ],
})