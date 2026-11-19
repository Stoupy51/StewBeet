import { StrictMode } from 'react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import '@fontsource-variable/archivo'
import '@fontsource-variable/archivo/wght-italic.css'
import '@fontsource-variable/jetbrains-mono'
import './index.css'
import App from './App.tsx'
import { MarkdownContentProvider } from './context/MarkdownContentContext'

const rootEl = document.getElementById('root')!
// Written by server.tsx beside a documentation page it rendered, which has to hydrate from the same markdown
const prerendered = document.getElementById('prerendered-doc')?.textContent
const app = (
  <StrictMode>
    <MarkdownContentProvider doc={prerendered ? JSON.parse(prerendered) : null}>
      <App />
    </MarkdownContentProvider>
  </StrictMode>
)

if (rootEl.innerHTML.trim() !== '') {
  // Pre-rendered HTML exists: hydrate instead of replacing
  hydrateRoot(rootEl, app)
} else {
  createRoot(rootEl).render(app)
}
