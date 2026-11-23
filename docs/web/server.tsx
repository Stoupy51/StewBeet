/**
 * Bun SSR server: replaces `vite preview`.
 *
 * For a doc page, /docs/<slug> or /fr/docs/<slug>:
 *   1. Reads the markdown from dist/docs, the copy this build serves, and its highlighted code.
 *   2. Renders the full page HTML in the language of the address (so crawlers receive real content).
 *   3. Rewrites the <head> for that document (title, description, og/twitter, canonical, hreflang).
 *   4. Returns the enriched HTML response, with the markdown embedded for the client to hydrate from.
 *
 * Every address the site had before /docs answers with a permanent redirect to its page.
 * All other requests are served as static files from dist/.
 * Unknown paths get dist/404.html with a 404 status.
 */
import { prerender } from 'react-dom/static';
import { StaticRouter } from 'react-router';
import { LanguageProvider } from './src/context/LanguageContext';
import { AppRoutes } from './src/AppRoutes';
import { MarkdownContentProvider } from './src/context/MarkdownContentContext';
import { applyPageMeta, markdownPageMeta } from './src/utils/pageMeta';
import { docHref, docSrc, pageAt, srcHref } from './src/docsPages';
import { clientIpFrom } from './src/api/sandbox';
import { handlePlayground } from './src/api/playground';
import { handleHeaders } from './src/api/headers';
import { MAX_PACK_BYTES } from './src/api/sandboxLimits';
import { handleTelemetryBuild, handleTelemetryBuilds, handleTelemetryEvent, handleTelemetryStreams } from './src/api/telemetry';
import { readFileSync } from 'fs';
import { join } from 'path';

const distDir = join(import.meta.dir, 'dist');
// _template.html is the original Vite-built index.html before prerender modifies it.
// It contains the empty <div id="root"></div> used as the injection target.
const template = readFileSync(join(distDir, '_template.html'), 'utf-8');
/** Gzipped search indexes, built on first request and kept for the process lifetime. */
const gzipCache = new Map<string, Uint8Array>();

/** Addresses the site had before /docs and /tools, kept alive for every link posted to them. */
const MOVED: Record<string, string> = {
    '/documentation': '/docs',
    '/fr/docs': '/docs',
    '/playground': '/tools/playground',
    '/auto_headers': '/tools/auto_headers',
    '/markdown_to_pmc_bbcode': '/tools/bbcode',
};

/** A relative Location, since the origin this process sees is the proxy's, not the visitor's. */
function movedTo(path: string): Response {
    return new Response(null, { status: 301, headers: { Location: path } });
}

/** Body of the document `prerender` emits: everything that belongs inside #root. */
function extractBody(html: string): string {
    const start = html.indexOf('<body>');
    const end = html.lastIndexOf('</body>');
    if (start === -1 || end === -1) return html;
    return html.slice(start + '<body>'.length, end);
}

Bun.serve({
    port: 4173,
    hostname: '0.0.0.0',

    // Set here as well as in the handlers, because without it Bun buffers a hostile body in full
    // before any of our code runs and gets a say about its size. This is the largest body any route
    // accepts, which is the auto.headers upload; the playground's own 16 KB cap is far below it and
    // is enforced by its handler.
    maxRequestBodySize: MAX_PACK_BYTES + 64 * 1024,

    async fetch(req, server) {
        const url = new URL(req.url);
        const { pathname } = url;

        // ── Sandbox builds
        // Before /markdown and before the static branches: the 404 fallthrough at the bottom would
        // otherwise answer a mistyped API call with dist/404.html, and a caller parsing that as
        // JSON gets a syntax error instead of a status it can act on.
        if (pathname === '/api/playground') {
            return handlePlayground(req, clientIpFrom(req, server.requestIP(req)?.address ?? ''));
        }
        if (pathname === '/api/tools/headers') {
            return handleHeaders(req, clientIpFrom(req, server.requestIP(req)?.address ?? ''));
        }

        // ── Telemetry
        // The address goes no further than the rate limit bucket inside the handler; what reaches
        // the disk is one number per day per counter. See src/api/telemetry/.
        if (pathname === '/api/telemetry/build') {
            return handleTelemetryBuild(req, clientIpFrom(req, server.requestIP(req)?.address ?? ''));
        }
        if (pathname === '/api/telemetry/event') {
            return handleTelemetryEvent(req, clientIpFrom(req, server.requestIP(req)?.address ?? ''));
        }
        if (pathname === '/api/telemetry/builds') {
            return handleTelemetryBuilds(url);
        }
        if (pathname === '/api/telemetry/streams') {
            return handleTelemetryStreams(url);
        }

        // ── Moved addresses. The browser keeps a link's #anchor across the redirect on its own.
        if (pathname === '/markdown') return movedTo(srcHref(url.searchParams.get('src') ?? ''));
        if (MOVED[pathname]) return movedTo(MOVED[pathname] + url.search);

        // ── Doc pages, rendered in the language of their address
        const docPage = pageAt(pathname);
        if (docPage?.language === 'fr' && !docPage.page.src.fr) return movedTo(docHref(docPage.page, 'en'));
        if (docPage) {
            const src = docSrc(docPage.page, docPage.language);
            const file = Bun.file(join(distDir, 'docs', src));
            const highlighted = Bun.file(join(distDir, 'highlighted', `${src}.json`));
            const doc = (await file.exists())
                ? { src, content: (await file.text()).replace(/\r\n?/g, '\n'), highlighted: (await highlighted.exists()) ? await highlighted.json() : {} }
                : null;

            const { prelude } = await prerender(
                <MarkdownContentProvider doc={doc}>
                    <StaticRouter location={pathname + url.search}>
                        <LanguageProvider>
                            <AppRoutes />
                        </LanguageProvider>
                    </StaticRouter>
                </MarkdownContentProvider>
            );
            const body = extractBody(await new Response(prelude).text());
            // `<` escaped so a `</script>` written in a guide cannot close the tag early
            const embedded = doc ? `<script id="prerendered-doc" type="application/json">${JSON.stringify({ src: doc.src, content: doc.content }).replace(/</g, '\\u003c')}</script>` : '';

            // Without this the document would ship index.html's head: same title and same
            // link preview for every page of the documentation.
            // A replacer function: the markdown is full of `$`, and a replacement string reads `$&` or `$'` as patterns.
            const output = applyPageMeta(template, markdownPageMeta(src, doc?.content ?? ''))
                .replace('<html lang="en">', `<html lang="${docPage.language}">`)
                .replace('<div id="root"></div>', () => `<div id="root">${body}</div>${embedded}`);

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

        // ── Static file serving
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
