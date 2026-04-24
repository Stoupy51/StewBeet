/**
 * Post-build prerender script — run with Bun after `vite build`.
 * Renders each route to static HTML so AI crawlers and search engines
 * receive real content instead of an empty <div id="root">.
 */
import { renderToString } from 'react-dom/server';
import { StaticRouter } from 'react-router';
import { LanguageProvider } from '../src/context/LanguageContext';
import { AppRoutes } from '../src/AppRoutes';
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

const routes = ['/', '/documentation', '/markdown', '/markdown_to_pmc_bbcode'];

const distDir = join(import.meta.dir, '..', 'dist');
const template = readFileSync(join(distDir, 'index.html'), 'utf-8');

for (const route of routes) {
    const html = renderToString(
        <StaticRouter location={route}>
            <LanguageProvider>
                <AppRoutes />
            </LanguageProvider>
        </StaticRouter>
    );

    const output = template.replace(
        '<div id="root"></div>',
        `<div id="root">${html}</div>`,
    );

    if (route === '/') {
        writeFileSync(join(distDir, 'index.html'), output);
    } else {
        const routeDir = join(distDir, route.slice(1));
        mkdirSync(routeDir, { recursive: true });
        writeFileSync(join(routeDir, 'index.html'), output);
    }

    console.log(`Pre-rendered: ${route}`);
}

console.log('Pre-rendering complete.');
