/**
 * Post-build prerender script: run with Bun after `vite build`.
 * Renders each route to static HTML so AI crawlers and search engines
 * receive real content instead of an empty <div id="root">.
 *
 * Uses `prerender` from react-dom/static rather than renderToString: the routes in
 * AppRoutes are React.lazy, and renderToString cannot suspend, so it aborted every
 * route to client rendering and emitted an empty shell.
 */
import { prerender } from 'react-dom/static';
import { StaticRouter } from 'react-router';
import { LanguageProvider } from '../src/context/LanguageContext';
import { AppRoutes } from '../src/AppRoutes';
import { applyPageMeta, STATIC_ROUTE_META } from '../src/utils/pageMeta';
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

// '/404' matches the catch-all route in AppRoutes; server.tsx serves the file it produces
// with a real 404 status instead of answering unknown paths with the landing page.
const routes = Object.keys(STATIC_ROUTE_META);

const distDir = join(import.meta.dir, '..', 'dist');
const template = readFileSync(join(distDir, 'index.html'), 'utf-8');

// Save the original Vite-built index.html as a template for the SSR server (server.tsx).
// Must be done before the '/' route overwrites dist/index.html with pre-rendered content.
writeFileSync(join(distDir, '_template.html'), template);

/** Body of the document `prerender` emits: everything that belongs inside #root. */
function extractBody(html: string): string {
    const start = html.indexOf('<body>');
    const end = html.lastIndexOf('</body>');
    if (start === -1 || end === -1) return html;
    return html.slice(start + '<body>'.length, end);
}

for (const route of routes) {
    const { prelude } = await prerender(
        <StaticRouter location={route}>
            <LanguageProvider>
                <AppRoutes />
            </LanguageProvider>
        </StaticRouter>
    );
    const body = extractBody(await new Response(prelude).text());

    const output = applyPageMeta(template, STATIC_ROUTE_META[route]).replace(
        '<div id="root"></div>',
        `<div id="root">${body}</div>`,
    );

    if (route === '/') {
        writeFileSync(join(distDir, 'index.html'), output);
    } else if (route === '/404') {
        writeFileSync(join(distDir, '404.html'), output);
    } else {
        const routeDir = join(distDir, route.slice(1));
        mkdirSync(routeDir, { recursive: true });
        writeFileSync(join(routeDir, 'index.html'), output);
    }

    console.log(`Pre-rendered: ${route} (${body.length} chars)`);
}

console.log('Pre-rendering complete.');
