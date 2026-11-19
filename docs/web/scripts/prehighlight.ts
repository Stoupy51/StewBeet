/**
 * Runs Shiki over the hero snippets once at build time and writes the markup to
 * src/generated/heroCode.json, one entry per tab of the code panel.
 *
 * The hero code panel is the largest contentful element on the landing page, and it used to
 * be highlighted in a useEffect: plain text painted first, then the whole block was replaced
 * with coloured markup once the highlighter and its grammar had loaded. Doing it here means
 * the correct pixels are in the prerendered HTML and the browser never loads a highlighter
 * for the landing page at all.
 *
 * Each snippet is a `# region hero-<id>` of a real StewBeet project that
 * python_package/scripts/build_hero_output.py builds for real, so the code shown and the files
 * shown beside it come from the same source and cannot disagree.
 */
import { codeToHtml, type ShikiTransformer } from 'shiki';
import { writeFileSync, mkdirSync, readFileSync } from 'fs';
import { join } from 'path';
import { pythonSemantics } from '../src/utils/pythonSemantics';

/** The snippet sits in half the hero; past this a 1280px screen cuts it mid-string. */
const MAX_COLUMNS = 66;
const SOURCE = join(import.meta.dir, '..', 'playground', 'hero', 'src', 'definitions.py');
/** Numbers each line from 0 in `--line`, which staggers the build animation in index.css. */
const LINE_INDEX: ShikiTransformer = {
    line(node, line) {
        node.properties.style = `--line:${line - 1}`;
    },
};
const REGION_MARKER = /^\s*# region (hero-[\w-]+)\s*$/gm;

/**
 * The lines between `# region <name>` and `# endregion <name>`, dedented by their common indent.
 *
 * The region lives inside `beet_default`, so it is indented at rest and has to be dedented to be
 * shown. Both markers are required: a renamed or deleted one fails the build here rather than
 * silently shipping a hero with no code in it.
 */
export function extractRegion(source: string, name: string): string {
    const lines = source.split('\n');
    const start = lines.findIndex((line) => line.trim() === `# region ${name}`);
    const end = lines.findIndex((line) => line.trim() === `# endregion ${name}`);
    if (start === -1) throw new Error(`prehighlight: missing "# region ${name}" in ${SOURCE}`);
    if (end === -1) throw new Error(`prehighlight: missing "# endregion ${name}" in ${SOURCE}`);
    if (end < start) throw new Error(`prehighlight: "# endregion ${name}" comes before its "# region ${name}"`);

    const body = lines.slice(start + 1, end);
    while (body.length && !body[0].trim()) body.shift();
    while (body.length && !body[body.length - 1].trim()) body.pop();
    if (!body.length) throw new Error(`prehighlight: region "${name}" is empty`);

    const indent = Math.min(...body.filter((line) => line.trim()).map((line) => line.length - line.trimStart().length));
    const dedented = body.map((line) => line.slice(indent));

    // The width budget used to live in a doc comment, which is another way of saying it was not
    // enforced. Failing here is what keeps the hero from silently overflowing.
    // Hero.tsx sets the panel's tab-size to 4, so a tab is 4 of these columns.
    const columns = (line: string) => line.replace(/\t/g, '    ').length;
    const tooWide = dedented.findIndex((line) => columns(line) > MAX_COLUMNS);
    if (tooWide !== -1) {
        throw new Error(
            `prehighlight: line ${start + 2 + tooWide} of ${SOURCE} is ${columns(dedented[tooWide])} columns, ` +
            `the hero panel fits ${MAX_COLUMNS}:\n    ${dedented[tooWide]}`,
        );
    }
    return dedented.join('\n');
}

/**
 * One tab per region, in file order. The id is what heroTree.json leaves name in `snippet`, and the
 * label is the snippet's first identifier (`Block`, `CustomOreGeneration`), so the tab reads as code.
 * The line count sizes the hero panels to the longest snippet.
 */
const source = readFileSync(SOURCE, 'utf-8');
const names = Array.from(source.matchAll(REGION_MARKER), (match) => match[1]);
if (!names.length) throw new Error(`prehighlight: no "# region hero-<id>" marker in ${SOURCE}`);
const snippets = await Promise.all(names.map(async (name) => {
    const code = extractRegion(source, name);
    return {
        id: name.slice('hero-'.length),
        label: code.match(/^[A-Za-z_]\w*/)?.[0] ?? name,
        lines: code.split('\n').length,
        html: await codeToHtml(code, { lang: 'python', themes: { dark: 'dark-plus', light: 'light-plus' }, defaultColor: 'dark', transformers: [pythonSemantics, LINE_INDEX] }),
    };
}));

const outputDir = join(import.meta.dir, '..', 'src', 'generated');
mkdirSync(outputDir, { recursive: true });
writeFileSync(join(outputDir, 'heroCode.json'), `${JSON.stringify({ snippets }, null, 4)}\n`);

console.log(`[prehighlight] ${snippets.length} hero snippets highlighted (${snippets.map((snippet) => snippet.id).join(', ')})`);
