/**
 * Search index builder — run with Bun before `vite` (dev) and `vite build`.
 *
 * Emits public/search-index.en.json and public/search-index.fr.json, one entry per
 * markdown heading section plus one entry per Python API symbol. The site itself
 * fetches markdown from GitHub at view time, so this is the only place where the
 * documentation text is available to the client-side search.
 *
 * Landing-page sections are NOT indexed here: SearchModal matches them directly
 * against the i18n translations, which are already bundled.
 *
 * Also emits public/sitemap.xml, since walking the documentation tree is exactly the
 * work a complete sitemap needs and a hand-maintained one listed 5 of the 37 pages.
 */
import { readdirSync, readFileSync, statSync, writeFileSync } from 'fs';
import { join, relative, sep } from 'path';
import { inflateSync } from 'zlib';
import { headingTextToSlug } from '../src/utils/slugify';
import { SITE_ORIGIN, STATIC_ROUTE_META } from '../src/utils/pageMeta';

interface Entry {
    /** Entry kind: markdown guide, plugin page, or Python API symbol. */
    t: 'doc' | 'plugin' | 'api';
    /** `src` query param for /markdown (doc, plugin), or Sphinx-relative uri (api). */
    p: string;
    /** Document label shown in the result row. */
    d: string;
    /** Heading (or symbol name). */
    h: string;
    /** Anchor slug within the document, may be empty. */
    a: string;
    /** Searchable body text. */
    b: string;
}

const scriptDir: string = import.meta.dir;
const webDir: string = join(scriptDir, '..');
const docsDir: string = join(webDir, 'public', 'docs');
const repoRoot: string = join(webDir, '..', '..');
const pythonRoot: string = join(repoRoot, 'python_package');
const outDir: string = join(webDir, 'public');

const SPHINX_BASE = 'https://stoupy51.github.io/StewBeet/latest/';
const OBJECTS_INV_URL = `${SPHINX_BASE}objects.inv`;

// ── Markdown ──────────────────────────────────────────────────────────────────

/** Strip markdown syntax noise while keeping every searchable word (code included). */
function toPlainText(markdown: string): string {
    return markdown
        .replace(/<!--[\s\S]*?-->/g, ' ')
        .replace(/<[^>]*>/g, ' ')
        .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
        .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
        .replace(/^\s*[-*+]\s+/gm, ' ')
        .replace(/[*_~>|]/g, ' ')
        .replace(/`/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

/** Split a markdown document into one entry per heading section. */
function sectionize(markdown: string, base: Omit<Entry, 'h' | 'a' | 'b'>): Entry[] {
    const entries: Entry[] = [];
    let heading = '';
    let anchor = '';
    let buffer: string[] = [];
    let inFence = false;

    const flush = () => {
        const body = toPlainText(buffer.join('\n'));
        if (body || heading) {
            entries.push({ ...base, h: heading, a: anchor, b: body });
        }
        buffer = [];
    };

    for (const line of markdown.split(/\r?\n/)) {
        if (/^\s*(```|~~~)/.test(line)) {
            inFence = !inFence;
            buffer.push(line);
            continue;
        }
        const match = !inFence && /^(#{1,6})\s+(.+)$/.exec(line);
        if (match) {
            flush();
            heading = toPlainText(match[2]);
            anchor = headingTextToSlug(match[2]);
            continue;
        }
        buffer.push(line);
    }
    flush();
    return entries;
}

/** Collect plugin pages — English only, so they go into every language index. */
function collectPlugins(): Entry[] {
    const dir = join(docsDir, 'plugins');
    const entries: Entry[] = [];
    for (const file of readdirSync(dir)) {
        if (!file.endsWith('.md')) continue;
        const name = file.slice(0, -3);
        const markdown = readFileSync(join(dir, file), 'utf-8');
        entries.push(...sectionize(markdown, { t: 'plugin', p: `plugins/${file}`, d: name }));
    }
    return entries;
}

/** Collect the numbered guides for one language (`<n>_<name>/<lang>.md`). */
function collectGuides(lang: 'en' | 'fr'): Entry[] {
    const entries: Entry[] = [];
    for (const item of readdirSync(docsDir, { withFileTypes: true })) {
        if (!item.isDirectory() || !/^\d+_/.test(item.name)) continue;
        const path = join(docsDir, item.name, `${lang}.md`);
        try {
            statSync(path);
        } catch {
            continue;
        }
        const markdown = readFileSync(path, 'utf-8');
        entries.push(...sectionize(markdown, { t: 'doc', p: `${item.name}/${lang}.md`, d: item.name }));
    }
    return entries;
}

// ── Python API ────────────────────────────────────────────────────────────────

/** Best-effort map of `module.Symbol` -> first docstring line, for module-level defs/classes. */
function collectDocstrings(): Map<string, string> {
    const found = new Map<string, string>();

    const walk = (dir: string): void => {
        for (const item of readdirSync(dir, { withFileTypes: true })) {
            const path = join(dir, item.name);
            if (item.isDirectory()) {
                if (item.name !== '__pycache__') walk(path);
                continue;
            }
            if (!item.name.endsWith('.py')) continue;

            const module = relative(pythonRoot, path)
                .slice(0, -3)
                .split(sep)
                .join('.')
                .replace(/\.__init__$/, '');
            const lines = readFileSync(path, 'utf-8').split(/\r?\n/);

            for (let i = 0; i < lines.length; i++) {
                const match = /^(?:async\s+)?(?:def|class)\s+(\w+)/.exec(lines[i]);
                if (!match) continue;

                // Skip over a possibly multi-line signature to reach the docstring.
                for (let j = i + 1; j < Math.min(i + 20, lines.length); j++) {
                    const doc = /^\s*[rfub]*"""(.*)$/.exec(lines[j]);
                    if (!doc) continue;
                    const first = doc[1].replace(/"""$/, '').trim() || (lines[j + 1] ?? '').trim();
                    if (first) found.set(`${module}.${match[1]}`, first.replace(/"""$/, '').trim());
                    break;
                }
            }
        }
    };

    walk(join(pythonRoot, 'stewbeet'));
    return found;
}

/**
 * Read the Sphinx inventory published by python_package/scripts/create_docs.py.
 * Gives every documented symbol with its exact page + anchor, so no URL guessing.
 * Returns an empty list when the site is unreachable (offline builds still work).
 */
async function collectApiSymbols(): Promise<Entry[]> {
    let raw: Buffer;
    try {
        const response = await fetch(OBJECTS_INV_URL, { signal: AbortSignal.timeout(15_000) });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        raw = Buffer.from(await response.arrayBuffer());
    } catch (error) {
        console.warn(`[search-index] Could not fetch ${OBJECTS_INV_URL} (${error}); skipping API symbols.`);
        return [];
    }

    // Four plain-text header lines, then a zlib stream.
    let offset = 0;
    for (let i = 0; i < 4; i++) {
        offset = raw.indexOf(0x0a, offset) + 1;
    }

    const docstrings = collectDocstrings();
    const entries: Entry[] = [];

    for (const line of inflateSync(raw.subarray(offset)).toString('utf-8').split('\n')) {
        const match = /^(.+?)\s+(\S+):(\S+)\s+(-?\d+)\s+(\S+)\s+(.*)$/.exec(line);
        if (!match) continue;

        const [, name, domain, role, , uri] = match;
        if (domain !== 'py') continue;

        const dot = name.lastIndexOf('.');
        // Private members (_abc_impl, __init__...) are noise in a documentation search
        if (name.slice(dot + 1).startsWith('_')) continue;

        const parent = role === 'module' || dot < 0 ? name : name.slice(0, dot);
        const symbol = role === 'module' || dot < 0 ? name : name.slice(dot + 1);
        const description = docstrings.get(name);

        // `uri` keeps Sphinx's `$` placeholder (expanded to the full name client-side)
        // and stays relative to SPHINX_BASE — both keep the index small.
        entries.push({
            t: 'api',
            p: uri,
            d: parent,
            h: symbol,
            a: '',
            b: `${role}${description ? ` ${description}` : ''}`,
        });
    }
    return entries;
}

// ── Sitemap ───────────────────────────────────────────────────────────────────

/** Same encoding the site's own links use, so a crawler never sees two URLs for one page. */
function srcToUrl(src: string): string {
    return `${SITE_ORIGIN}/markdown?src=${encodeURIComponent(src)}`.replace(/&/g, '&amp;');
}

function writeSitemap(docSrcs: Set<string>): void {
    const lastmod = new Date().toISOString().slice(0, 10);
    const urls: { loc: string; changefreq: string; priority: string }[] = [
        ...Object.values(STATIC_ROUTE_META)
            .filter((meta) => !meta.noindex)
            .map((meta) => ({
                loc: `${SITE_ORIGIN}${meta.path}`,
                changefreq: 'weekly',
                priority: meta.path === '/' ? '1.0' : meta.path === '/documentation' ? '0.9' : '0.5',
            })),
        ...[...docSrcs].sort().map((src) => ({
            loc: srcToUrl(src),
            changefreq: 'weekly',
            priority: '0.7',
        })),
    ];

    const body = urls
        .map(({ loc, changefreq, priority }) =>
            `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n` +
            `    <changefreq>${changefreq}</changefreq>\n    <priority>${priority}</priority>\n  </url>`,
        )
        .join('\n');

    writeFileSync(
        join(outDir, 'sitemap.xml'),
        `<?xml version="1.0" encoding="UTF-8"?>\n` +
        `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>\n`,
    );
    console.log(`[sitemap] ${urls.length} URLs -> public/sitemap.xml`);
}

// ── Output ────────────────────────────────────────────────────────────────────

const plugins: Entry[] = collectPlugins();
const api: Entry[] = await collectApiSymbols();
const docSrcs = new Set<string>(plugins.map((entry) => entry.p));

for (const lang of ['en', 'fr'] as const) {
    const guides = collectGuides(lang);
    for (const entry of guides) docSrcs.add(entry.p);
    const entries = [...guides, ...plugins, ...api];
    const path = join(outDir, `search-index.${lang}.json`);
    const json = JSON.stringify({ generated: new Date().toISOString(), apiBase: SPHINX_BASE, entries });
    writeFileSync(path, json);
    console.log(
        `[search-index] ${lang}: ${entries.length} entries ` +
        `(${guides.length} guide, ${plugins.length} plugin, ${api.length} api) ` +
        `-> ${(json.length / 1024).toFixed(0)} KB`,
    );
}

writeSitemap(docSrcs);
