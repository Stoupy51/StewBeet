/**
 * Bun SSR server — replaces `vite preview`.
 *
 * For /markdown?src=... requests:
 *   1. Fetches the GitHub raw markdown content server-side.
 *   2. Renders the full page HTML via renderToString (so crawlers receive real content).
 *   3. Returns the enriched HTML response.
 *
 * All other requests are served as static files from dist/.
 * Unknown paths fall back to dist/index.html (SPA fallback).
 */
import { prerender } from 'react-dom/static';
import { StaticRouter } from 'react-router';
import { LanguageProvider } from './src/context/LanguageContext';
import { AppRoutes } from './src/AppRoutes';
import { MarkdownContentProvider } from './src/context/MarkdownContentContext';
import { readFileSync } from 'fs';
import { join } from 'path';

const distDir = join(import.meta.dir, 'dist');
const FETCH_TIMEOUT_MS = 7000;
const MAX_MARKDOWN_CHARS = 500_000;
const DOC_SRC_PATTERN = /^(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+\.md$/;
// _template.html is the original Vite-built index.html before prerender modifies it.
// It contains the empty <div id="root"></div> used as the injection target.
const template = readFileSync(join(distDir, '_template.html'), 'utf-8');
/** Gzipped search indexes, built on first request and kept for the process lifetime. */
const gzipCache = new Map<string, Uint8Array>();

/** Convert a `src` param to the raw GitHub URL (same logic as MarkdownPage.tsx). */
function isValidDocSrc(src: string): boolean {
    return DOC_SRC_PATTERN.test(src) && !src.includes('..');
}

/** Body of the document `prerender` emits — everything that belongs inside #root. */
function extractBody(html: string): string {
    const start = html.indexOf('<body>');
    const end = html.lastIndexOf('</body>');
    if (start === -1 || end === -1) return html;
    return html.slice(start + '<body>'.length, end);
}

function srcToRawUrl(src: string): string {
    return `https://github.com/Stoupy51/StewBeet/blob/main/docs/${src}`
        .replace('github.com/', 'raw.githubusercontent.com/')
        .replace('/blob/', '/')
        .replace('/raw/refs/heads/', '/');
}

Bun.serve({
    port: 4173,
    hostname: '0.0.0.0',

    async fetch(req) {
        const url = new URL(req.url);
        const { pathname } = url;

        // ── SSR for /markdown?src=... ─────────────────────────────────────────
        if (pathname === '/markdown') {
            const src = url.searchParams.get('src');
            let markdownContent = '';

            if (src && isValidDocSrc(src)) {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
                try {
                    const rawUrl = srcToRawUrl(src);
                    const res = await fetch(rawUrl, { signal: controller.signal });
                    if (res.ok) {
                        const text = await res.text();
                        if (text.length <= MAX_MARKDOWN_CHARS) {
                            markdownContent = text;
                        }
                    }
                } catch {
                    // content stays empty; page will render error state on client
                } finally {
                    clearTimeout(timeoutId);
                }
            }

            const location = pathname + url.search;
            const { prelude } = await prerender(
                <MarkdownContentProvider content={markdownContent}>
                    <StaticRouter location={location}>
                        <LanguageProvider>
                            <AppRoutes />
                        </LanguageProvider>
                    </StaticRouter>
                </MarkdownContentProvider>
            );
            const body = extractBody(await new Response(prelude).text());

            const output = template.replace(
                '<div id="root"></div>',
                `<div id="root">${body}</div>`,
            );

            return new Response(output, {
                headers: { 'Content-Type': 'text/html; charset=utf-8' },
            });
        }

        // ── Search index (large JSON, worth compressing once per process) ─────
        if (/^\/search-index\.[a-z]{2}\.json$/.test(pathname)) {
            const file = Bun.file(join(distDir, pathname));
            if (await file.exists()) {
                if (!req.headers.get('accept-encoding')?.includes('gzip')) {
                    return new Response(file);
                }
                let compressed = gzipCache.get(pathname);
                if (!compressed) {
                    compressed = Bun.gzipSync(new Uint8Array(await file.arrayBuffer()));
                    gzipCache.set(pathname, compressed);
                }
                return new Response(compressed, {
                    headers: {
                        'Content-Type': 'application/json; charset=utf-8',
                        'Content-Encoding': 'gzip',
                    },
                });
            }
        }

        // ── Static file serving ───────────────────────────────────────────────
        if (pathname !== '/') {
            const file = Bun.file(join(distDir, pathname));
            if (await file.exists()) {
                return new Response(file);
            }
        }

        // Try pathname/index.html (for pre-rendered SPA routes like /documentation)
        const indexFile = Bun.file(join(distDir, pathname.replace(/\/$/, ''), 'index.html'));
        if (await indexFile.exists()) {
            return new Response(indexFile, {
                headers: { 'Content-Type': 'text/html; charset=utf-8' },
            });
        }

        // SPA fallback — let the client-side router handle unknown paths
        return new Response(Bun.file(join(distDir, 'index.html')), {
            headers: { 'Content-Type': 'text/html; charset=utf-8' },
        });
    },
});

console.log('Server running on http://0.0.0.0:4173');
