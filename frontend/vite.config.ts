import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages serves the site under /<repo-name>/, so we need the base path
// to match when deployed. Locally (vite dev / preview) we keep the default '/'.
const isPagesBuild = process.env.GITHUB_PAGES === '1'

export default defineConfig({
  base: isPagesBuild ? '/sunu-/' : '/',
  plugins: [react()],
})
