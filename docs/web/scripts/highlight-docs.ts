/**
 * Highlights every fenced block of the docs at build time, the way useShiki would in the browser,
 * and writes each page's markup by block to public/highlighted/<page>.json, which MarkdownPage
 * fetches beside the markdown and server.tsx renders from. A reader of the docs never loads a
 * highlighter, and a page shows coloured from its first frame.
 *
 * A block written the same in English and in French is highlighted once.
 */
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fromMarkdown } from 'mdast-util-from-markdown';
import type { Code, Nodes } from 'mdast';
import { PAGE_THEMES, codeKey } from '../src/hooks/useShiki';
import { highlightCode } from '../src/utils/highlightCode';

const DOCS = join(import.meta.dir, '..', 'public', 'docs');
const OUTPUT = join(import.meta.dir, '..', 'public', 'highlighted');

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
        const html = highlighted.get(key) ?? await highlightCode(value, lang ?? 'text', PAGE_THEMES);
        highlighted.set(key, html);
        page[key] = html;
    }
    const output = join(OUTPUT, `${name}.json`);
    mkdirSync(dirname(output), { recursive: true });
    writeFileSync(output, JSON.stringify(page));
}

console.log(`[highlight-docs] ${highlighted.size} code blocks of ${pages.length} pages highlighted in ${Math.round(performance.now() - started)} ms`);
