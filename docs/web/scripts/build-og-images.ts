/**
 * Writes the preview image a link to each page shows on Discord and other sites (1200x630,
 * public/generated/og/), with the page's title, lead and address. utils/pageMeta.ts points
 * og:image at it, under the name `ogImageName` gives the page's path.
 *
 * Satori lays the card out from a tree of styled elements and resvg rasterises its SVG. Satori
 * reads woff but not woff2, hence the static @fontsource/archivo files next to the variable font
 * the site itself loads.
 */
import { mkdirSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';
import { DOC_PAGES, PLUGIN_INDEX, SECTIONS, type DocPage, type Section } from '../src/docsPages';
import { STATIC_ROUTE_META, markdownPageMeta, ogImageName, type PageMeta } from '../src/utils/pageMeta';
import type { Language } from '../src/context/LanguageContext';

const ROOT = join(import.meta.dir, '..');
const OUTPUT = join(ROOT, 'public', 'generated', 'og');
const FONTS = join(ROOT, 'node_modules', '@fontsource', 'archivo', 'files');

/** Dark tokens of tailwind.config.js: a link preview has no theme to follow, and Discord is dark. */
const COLORS = { surface: '#0c0d0f', text: '#f2f3f5', muted: '#a3a7b0', border: '#272930' };
const SECTION_COLORS: Record<Section, string> = {
    start: '#63d96b', guides: '#7c9cff', plugins: '#f0b23c', contrib: '#fe5acc', reference: '#d98cf0', understand: '#5fd3e0',
};

const fonts = [400, 700].flatMap((weight) => ['latin', 'latin-ext'].map((subset) => ({
    name: 'Archivo',
    data: readFileSync(join(FONTS, `archivo-${subset}-${weight}-normal.woff`)),
    weight: weight as 400 | 700,
    style: 'normal' as const,
})));
const logo = `data:image/png;base64,${readFileSync(join(ROOT, 'public', 'stewbeet-logo.png')).toString('base64')}`;

type Node = { type: string; props: Record<string, unknown> };
const box = (style: Record<string, unknown>, children: (Node | string)[] | Node | string): Node => ({ type: 'div', props: { style: { display: 'flex', ...style }, children } });

/** One card: the logo, the section label in its colour, the title, the lead, the address. */
async function render(meta: PageMeta, section: { label: string; color: string } | null): Promise<Buffer> {
    const title = meta.title.replace(/ \| StewBeet$/, '');
    const lead = meta.description.length > 120 ? `${meta.description.slice(0, meta.description.lastIndexOf(' ', 117))}...` : meta.description;
    const card = box(
        { width: 1052, height: 534, flexDirection: 'column', justifyContent: 'space-between', paddingTop: 48, paddingBottom: 48, paddingLeft: 72, paddingRight: 72, background: COLORS.surface, borderLeft: `2px solid ${COLORS.border}`, borderRight: `2px solid ${COLORS.border}`, fontFamily: 'Archivo', color: COLORS.text },
        [
            box({ alignItems: 'center', gap: 20 }, [
                { type: 'img', props: { src: logo, width: 80, height: 80 } },
                box({ fontSize: 42, fontWeight: 700 }, 'StewBeet'),
                ...(section ? [box({ marginLeft: 28, alignItems: 'center', gap: 14, fontSize: 28, letterSpacing: 2, color: section.color }, [
                    box({ width: 18, height: 18, background: section.color }, []),
                    section.label.toUpperCase(),
                ])] : []),
            ]),
            box({ flexDirection: 'column', gap: 24 }, [
                box({ fontSize: title.length > 30 ? 76 : 96, fontWeight: 700, lineHeight: 1.05 }, title),
                box({ fontSize: 34, lineHeight: 1.35, color: COLORS.muted }, lead),
            ]),
            box({ fontSize: 28, color: COLORS.muted }, `stewbeet.paralya.fr${meta.path}`),
        ],
    );
    const svg = await satori(card as unknown as React.ReactNode, { width: 1200, height: 630, fonts });
    return Buffer.from(new Resvg(svg).render().asPng());
}

const started = performance.now();
mkdirSync(OUTPUT, { recursive: true });
let written = 0;

for (const meta of Object.values(STATIC_ROUTE_META).filter((meta) => meta.path !== '/' && !meta.noindex)) {
    writeFileSync(join(OUTPUT, ogImageName(meta.path)), await render(meta, null));
    written++;
}

const docPages: DocPage[] = [...DOC_PAGES, PLUGIN_INDEX];
for (const page of docPages) {
    for (const language of ['en', 'fr'] as Language[]) {
        const src = page.src[language];
        if (!src) continue;
        const meta = markdownPageMeta(src, readFileSync(join(ROOT, 'public', 'docs', src), 'utf8'));
        writeFileSync(join(OUTPUT, ogImageName(meta.path)), await render(meta, { label: SECTIONS[page.section].title[language], color: SECTION_COLORS[page.section] }));
        written++;
    }
}

console.log(`[og-images] ${written} preview images in ${Math.round(performance.now() - started)} ms`);
