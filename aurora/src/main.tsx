import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
// Bundle the Inter font so the desktop app works fully offline (no CDN needed).
import '@fontsource-variable/inter'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* HashRouter keeps deep links working on any static host (GitHub Pages, Netlify…) */}
    <HashRouter>
      <App />
    </HashRouter>
  </React.StrictMode>,
)
