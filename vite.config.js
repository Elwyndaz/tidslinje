import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// OBS: Byt ut 'arbetarrorelsens-tidslinje' mot ditt faktiska GitHub-repo-namn
export default defineConfig({
  plugins: [react()],
  base: '/arbetarrorelsens-tidslinje/',
})
