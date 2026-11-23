/**
 * Highlights every fenced block of the docs at build time, the way useShiki would in the browser,
 * and writes each page's markup by block to public/highlighted/<page>.json, which MarkdownPage
 * fetches beside the markdown and server.tsx renders from. A reader of the docs never loads a
 * highlighter, and a page shows coloured from its first frame. The files the hero's block builds
 * into go to src/generated/heroFiles.json, for the file browser of the home page, and the code of
 * its gains examples to src/generated/gainsCode.json.
 *
 * A token's colours go in a class of src/generated/codeColors.css rather than inline: the docs use
 * about 20 distinct styles over thousands of tokens. A block written the same in English and in
 * French is highlighted once.
 */
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fromMarkdown } from 'mdast-util-from-markdown';
import type { Code, Nodes } from 'mdast';
import type { ShikiTransformer } from 'shiki';
import { PAGE_THEMES, codeKey } from '../src/hooks/useShiki';
import { highlightCode } from '../src/utils/highlightCode';
import { GAIN_SNIPPETS } from '../src/components/gainsData';

const DOCS = join(import.meta.dir, '..', 'public', 'docs');
const OUTPUT = join(import.meta.dir, '..', 'public', 'highlighted');
const GENERATED = join(import.meta.dir, '..', 'src', 'generated');
const STYLESHEET = join(GENERATED, 'codeColors.css');

/** Named by a hash of the style, so a page fetched after a deploy still matches the stylesheet a reader loaded before it. */
const styleClasses = new Map<string, string>();
const STYLE_TO_CLASS: ShikiTransformer = {
    name: 'style-to-class',
    span(node) {
        const { style } = node.properties;
        if (typeof style !== 'string') return;
        const name = `c${codeKey('css', style)}`;
        styleClasses.set(name, style);
        delete node.properties.style;
        this.addClassToHast(node, name);
    },
};

function codeBlocks(node: Nodes): Code[] {
    if (node.type === 'code') return [node];
    return 'children' in node ? node.children.flatMap(codeBlocks) : [];
}

const started = performance.now();
const highlighted = new Map<string, string>();
const pages = readdirSync(DOCS, { recursive: true, encoding: 'utf-8' }).filter((path) => path.endsWith('.md'));
for (const name of pages) {
    const page: Record<string, string> = {};
    for (const { lang, value } of codeBlocks(fromMarkdown(readFileSync(join(DOCS, name), 'utf-8').replace(/\r\n?/g, '\n')))) {
        const key = codeKey(lang ?? 'text', value);
        const html = highlighted.get(key) ?? await highlightCode(value, lang ?? 'text', PAGE_THEMES, [STYLE_TO_CLASS]);
        highlighted.set(key, html);
        page[key] = html;
    }
    const output = join(OUTPUT, `${name}.json`);
    mkdirSync(dirname(output), { recursive: true });
    writeFileSync(output, JSON.stringify(page));
}

// Written by python_package/scripts/build_hero_output.py, by path under build/
const heroContents: Record<string, string> = JSON.parse(readFileSync(join(GENERATED, 'heroContents.json'), 'utf-8'));
const heroFiles: Record<string, string> = {};
for (const [path, text] of Object.entries(heroContents)) {
    heroFiles[path] = await highlightCode(text, path.endsWith('.mcfunction') ? 'mcfunction' : 'json', PAGE_THEMES, [STYLE_TO_CLASS]);
}
writeFileSync(join(GENERATED, 'heroFiles.json'), JSON.stringify(heroFiles));

const gainsCode: Record<string, string> = {};
for (const [key, { lang, code }] of Object.entries(GAIN_SNIPPETS)) {
    gainsCode[key] = await highlightCode(code, lang, PAGE_THEMES, [STYLE_TO_CLASS]);
}
writeFileSync(join(GENERATED, 'gainsCode.json'), JSON.stringify(gainsCode));

writeFileSync(STYLESHEET, [...styleClasses].map(([name, style]) => `.${name}{${style}}\n`).join(''));

console.log(`[highlight-docs] ${highlighted.size} code blocks of ${pages.length} pages highlighted with ${styleClasses.size} styles in ${Math.round(performance.now() - started)} ms`);
