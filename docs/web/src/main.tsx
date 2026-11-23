import { StrictMode } from 'react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import '@fontsource-variable/archivo'
import '@fontsource-variable/archivo/wght-italic.css'
import '@fontsource-variable/jetbrains-mono'
import './index.css'
import './generated/codeColors.css'
import App from './App.tsx'
import { MarkdownContentProvider } from './context/MarkdownContentContext'

const rootEl = document.getElementById('root')!
// Written by server.tsx beside a documentation page it rendered, which has to hydrate from the same markdown
const prerendered = document.getElementById('prerendered-doc')?.textContent
// The server sends the page's highlighted code once, in the HTML of its blocks, and not again in the JSON
const highlighted = Object.fromEntries([...rootEl.querySelectorAll<HTMLElement>('[data-code-key]')].map((block) => [block.dataset.codeKey, block.innerHTML]))
const app = (
  <StrictMode>
    <MarkdownContentProvider doc={prerendered ? { ...JSON.parse(prerendered), highlighted } : null}>
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
