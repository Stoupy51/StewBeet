import { StrictMode } from 'react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const rootEl = document.getElementById('root')!

if (rootEl.innerHTML.trim() !== '') {
  // Pre-rendered HTML exists: hydrate instead of replacing
  hydrateRoot(
    rootEl,
    <StrictMode>
      <App />
    </StrictMode>,
  )
} else {
  createRoot(rootEl).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}
