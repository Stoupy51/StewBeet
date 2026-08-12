/**
 * Bun SSR server: replaces `vite preview`.
 *
 * For /markdown?src=... requests:
 *   1. Fetches the GitHub raw markdown content server-side.
 *   2. Renders the full page HTML via renderToString (so crawlers receive real content).
 *   3. Rewrites the <head> for that document (title, description, og/twitter, canonical).
 *   4. Returns the enriched HTML response.
 *
 * All other requests are served as static files from dist/.
 * Unknown paths get dist/404.html with a 404 status.
 */
import { prerender } from 'react-dom/static';
import { StaticRouter } from 'react-router';
import { LanguageProvider } from './src/context/LanguageContext';
import { AppRoutes } from './src/AppRoutes';
import { MarkdownContentProvider } from './src/context/MarkdownContentContext';
import { applyPageMeta, markdownPageMeta } from './src/utils/pageMeta';
import { clientIpFrom, handlePlayground } from './src/api/playground';
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

/** Body of the document `prerender` emits: everything that belongs inside #root. */
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

    // The playground body is capped at 16 KB by the handler, so nothing legitimate comes close.
    // Set here as well, because without it Bun buffers a hostile body in full before any of our
    // code runs and gets a say about its size.
    maxRequestBodySize: 64 * 1024,

    async fetch(req, server) {
        const url = new URL(req.url);
        const { pathname } = url;

        // ── Playground builds ─────────────────────────────────────────────────
        // Before /markdown and before the static branches: the 404 fallthrough at the bottom would
        // otherwise answer a mistyped API call with dist/404.html, and a caller parsing that as
        // JSON gets a syntax error instead of a status it can act on.
        if (pathname === '/api/playground') {
            return handlePlayground(req, clientIpFrom(req, server.requestIP(req)?.address ?? ''));
        }

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

            // Without this the document would ship index.html's head: same title and same
            // link preview for every page of the documentation.
            const output = applyPageMeta(template, markdownPageMeta(src, markdownContent)).replace(
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

        // Unknown path: the pre-rendered catch-all route, with the status that goes with it.
        // Answering 200 with the landing page turned every dead link into a soft 404 and
        // showed the reader the home page instead of telling them the page was gone.
        return new Response(Bun.file(join(distDir, '404.html')), {
            status: 404,
            headers: { 'Content-Type': 'text/html; charset=utf-8' },
        });
    },
});

console.log('Server running on http://0.0.0.0:4173');
