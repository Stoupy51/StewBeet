/**
 * Per-page <head> metadata, shared by the build-time prerender (scripts/prerender.tsx)
 * and the runtime SSR server (server.tsx).
 *
 * Both of them start from the same Vite-built index.html, so without this every route
 * ships the landing page's head: one duplicated <title> across the whole site, and a
 * shared link showing the homepage blurb whatever page was actually shared.
 */
import { docHref, findDocPage, srcHref } from '../docsPages';
import type { Language } from '../context/LanguageContext';

export const SITE_ORIGIN = 'https://stewbeet.paralya.fr';

export interface PageMeta {
    /** Full <title>, reused for og:title and twitter:title. */
    title: string;
    description: string;
    /** Absolute path, e.g. `/docs/plugins/archive`. */
    path: string;
    /** Keeps a page out of the index without hiding it from crawlers following its links. */
    noindex?: boolean;
    /** The page's address in each language it is written in, for search engines to pair them. */
    alternates?: Partial<Record<Language, string>>;
}

/** Longest description before truncation: beyond this both Google and Discord cut it themselves. */
const MAX_DESCRIPTION_CHARS = 200;

const SITE_TITLE = 'StewBeet | Minecraft datapacks, generated from Python';
const SITE_DESCRIPTION =
    'StewBeet is a Beet framework for Minecraft datapacks. Define a block or an item in Python and get the models, recipes, loot tables, translations and in-game manual generated on every build.';

/** Metadata for the routes that prerender.tsx renders to a static file. */
export const STATIC_ROUTE_META: Record<string, PageMeta> = {
    '/': {
        title: SITE_TITLE,
        description: SITE_DESCRIPTION,
        path: '/',
    },
    '/docs': {
        title: 'Documentation | StewBeet',
        description:
            'Guides and plugin reference for StewBeet: getting started, defining items and blocks, writing to files, beet configuration, equations, dependencies, continuous delivery and the in-game manual.',
        path: '/docs',
    },
    '/tools': {
        title: 'Tools | StewBeet',
        description: 'Tools for StewBeet and Minecraft datapack development: the playground, the auto.headers pass over an existing datapack, and the Markdown to BBCode converter for PlanetMinecraft.',
        path: '/tools',
    },
    '/showcase': {
        title: 'Showcase | StewBeet',
        description: 'Every public datapack and library built with StewBeet, with its source: community projects first, then the packs and libraries of its author.',
        path: '/showcase',
    },
    '/credits': {
        title: 'Standing on giants | StewBeet',
        description:
            'The open-source projects StewBeet is built on: beet, mecha, bolt, Model Resolver, the Smithed ecosystem, Bookshelf, and every library the build downloads for you.',
        path: '/credits',
    },
    '/telemetry': {
        title: 'Telemetry | StewBeet',
        description:
            'What StewBeet reports after a successful build: its own version, the Python version and how long the build took. Nothing else, no identifiers, and one environment variable turns it off.',
        path: '/telemetry',
    },
    '/tools/playground': {
        title: 'Playground | StewBeet',
        description: 'Write a StewBeet definitions module in the browser and see the datapack and resource pack files it generates: models, recipes, loot tables, predicates and translations.',
        path: '/tools/playground',
    },
    '/tools/auto_headers': {
        title: 'Auto Headers | StewBeet',
        description: 'Upload a Minecraft datapack and get it back with a generated header on every function: who calls it, the execution context it runs in, and the type of every macro argument. Runs the standalone auto.headers beet plugin.',
        path: '/tools/auto_headers',
    },
    '/tools/bbcode': {
        title: 'Markdown to BBCode Converter | StewBeet',
        description: 'Convert Markdown to PlanetMinecraft BBCode in the browser: badges, lists, tables, code blocks and spoilers, with a live preview and diff.',
        path: '/tools/bbcode',
    },
    '/404': {
        title: 'Page not found | StewBeet',
        description: 'This page does not exist on the StewBeet documentation site.',
        path: '/404',
        noindex: true,
    },
};

/** Strip markdown syntax so a heading or paragraph reads correctly inside an attribute. */
function toPlainText(markdown: string): string {
    return markdown
        .replace(/<[^>]*>/g, ' ')
        .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
        .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
        .replace(/\*\*|~~|`/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

/** Cut on a word boundary rather than mid-word, which is what a truncated preview looks like. */
function truncate(text: string): string {
    if (text.length <= MAX_DESCRIPTION_CHARS) return text;
    const cut = text.slice(0, MAX_DESCRIPTION_CHARS);
    const lastSpace = cut.lastIndexOf(' ');
    return `${(lastSpace > MAX_DESCRIPTION_CHARS / 2 ? cut.slice(0, lastSpace) : cut).trimEnd()}...`;
}

/**
 * Lead paragraph of a document.
 * Plugin pages open on a `📄 Source Code:` line and only describe themselves under their
 * Overview heading, so that section wins when it exists; guides fall back to their intro.
 */
function leadParagraph(markdown: string): string {
    const body = markdown.replace(/```[\s\S]*?```/g, '');
    const overview = /^##\s+.*Overview.*$/im.exec(body);
    const sections = overview ? [body.slice(overview.index + overview[0].length), body] : [body];

    for (const section of sections) {
        for (const block of section.split(/\n\s*\n/)) {
            const line = block.trim();
            if (!line || line.startsWith('#') || line.startsWith('|')) continue;
            const text = toPlainText(line.replace(/^\s*[-*+]\s+/gm, ''));
            if (text.length >= 60) return text;
        }
    }
    return '';
}

/** What a doc address that leads to no page says about itself. */
const MISSING_DOC_META: PageMeta = {
    title: 'Page not found | StewBeet',
    description: 'This page does not exist on the StewBeet documentation site.',
    path: '/docs',
    noindex: true,
};

/** Metadata for a doc page, derived from the document the SSR server just read. */
export function markdownPageMeta(src: string | null, markdown: string): PageMeta {
    if (!src || !markdown) return MISSING_DOC_META;

    // The page list's title, so a plugin page is named in words and not by its module path
    const page = findDocPage(src);
    const heading = /^#\s+(.+)$/m.exec(markdown);
    const name = page ? page.title[src.endsWith('/fr.md') ? 'fr' : 'en'] : toPlainText(heading ? heading[1] : src.replace(/\.md$/, ''));
    const description = leadParagraph(markdown);

    return {
        title: `${name} | StewBeet`,
        description: description ? truncate(description) : `${name}: StewBeet documentation.`,
        path: srcHref(src),
        alternates: page?.src.fr ? { en: docHref(page, 'en'), fr: docHref(page, 'fr') } : undefined,
    };
}

function escapeAttribute(value: string): string {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/**
 * Replace a meta tag's content in place.
 * The callback form of `replace` matters here: descriptions contain `$` (`$ pip install ...`),
 * which a string replacement would read as a capture group reference.
 */
function setMeta(html: string, attribute: 'name' | 'property', key: string, value: string): string {
    const pattern = new RegExp(`(<meta ${attribute}="${key}" content=")[^"]*(")`);
    return html.replace(pattern, (_full, open: string, close: string) => `${open}${escapeAttribute(value)}${close}`);
}

/** Rewrite the built index.html head for one page, leaving the rest of the document untouched. */
export function applyPageMeta(html: string, meta: PageMeta): string {
    const url = `${SITE_ORIGIN}${meta.path}`;
    let output = html.replace(/<title>[^<]*<\/title>/, () => `<title>${escapeAttribute(meta.title)}</title>`);

    output = setMeta(output, 'name', 'description', meta.description);
    for (const prefix of ['og', 'twitter'] as const) {
        output = setMeta(output, 'property', `${prefix}:title`, meta.title);
        output = setMeta(output, 'property', `${prefix}:description`, meta.description);
        output = setMeta(output, 'property', `${prefix}:url`, url);
    }

    const injected = [`    <link rel="canonical" href="${escapeAttribute(url)}" />`];
    for (const [language, path] of Object.entries(meta.alternates ?? {})) {
        injected.push(`    <link rel="alternate" hreflang="${language}" href="${escapeAttribute(SITE_ORIGIN + path)}" />`);
    }
    if (meta.noindex) injected.push('    <meta name="robots" content="noindex, follow" />');
    return output.replace('</head>', `${injected.join('\n')}\n  </head>`);
}
