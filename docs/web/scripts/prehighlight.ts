/**
 * Runs Shiki over the hero snippet once at build time and writes the markup to
 * src/generated/heroCode.json.
 *
 * The hero code panel is the largest contentful element on the landing page, and it used to
 * be highlighted in a useEffect: plain text painted first, then the whole block was replaced
 * with coloured markup once the highlighter and its grammar had loaded. Doing it here means
 * the correct pixels are in the prerendered HTML and the browser never loads a highlighter
 * for the landing page at all.
 *
 * The snippet is not a string constant any more: it is a region of a real StewBeet project that
 * python_package/scripts/build_hero_output.py builds for real, so the code shown and the files
 * shown beside it come from the same source and cannot disagree.
 */
import { codeToHtml, createHighlighter } from 'shiki';
import { writeFileSync, mkdirSync, readFileSync } from 'fs';
import { join } from 'path';
import { pythonSemantics } from '../src/utils/pythonSemantics';
import { MCFUNCTION_LANGUAGE } from '../src/langs/mcfunction';

/** The snippet sits in half the hero; past this a 1280px screen cuts it mid-string. */
const MAX_COLUMNS = 66;
const SOURCE = join(import.meta.dir, '..', 'playground', 'hero', 'src', 'definitions.py');
const REGION = 'hero-snippet';

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
    const tooWide = dedented.findIndex((line) => line.length > MAX_COLUMNS);
    if (tooWide !== -1) {
        throw new Error(
            `prehighlight: line ${start + 2 + tooWide} of ${SOURCE} is ${dedented[tooWide].length} columns, ` +
            `the hero panel fits ${MAX_COLUMNS}:\n    ${dedented[tooWide]}`,
        );
    }
    return dedented.join('\n');
}

const code = extractRegion(readFileSync(SOURCE, 'utf-8'), REGION);
const html = await codeToHtml(code, { lang: 'python', theme: 'dark-plus', transformers: [pythonSemantics] });

const outputDir = join(import.meta.dir, '..', 'src', 'generated');
mkdirSync(outputDir, { recursive: true });
writeFileSync(join(outputDir, 'heroCode.json'), `${JSON.stringify({ html }, null, 4)}\n`);

/**
 * The generated files the output panel shows are highlighted here too, for the same reason the
 * snippet is: the landing page must not load a highlighter. They go to their own file, which the
 * panel imports dynamically, so this markup only ever reaches a reader who clicked a file.
 *
 * build_hero_output.py writes the raw bodies and is the source of truth; this derives from them.
 *
 * Same grammar, same theme and same transformer as src/hooks/useShiki.ts, so a .mcfunction in the
 * hero and a .mcfunction in the features section below it are colored identically.
 */
const bodies: Record<string, string> = JSON.parse(readFileSync(join(outputDir, 'heroContents.json'), 'utf-8'));
const highlighter = await createHighlighter({ themes: ['dark-plus'], langs: [MCFUNCTION_LANGUAGE, 'json'] });
const highlighted: Record<string, string> = {};
for (const [path, body] of Object.entries(bodies)) {
    highlighted[path] = highlighter.codeToHtml(body, {
        lang: path.endsWith('.mcfunction') ? 'mcfunction' : 'json',
        theme: 'dark-plus',
        transformers: [pythonSemantics],
    });
}
writeFileSync(join(outputDir, 'heroContentsHtml.json'), `${JSON.stringify(highlighted, null, 4)}\n`);

const bytes = Object.values(highlighted).reduce((total, item) => total + item.length, 0);
console.log(`[prehighlight] hero snippet highlighted (${code.split('\n').length} lines, ${html.length} bytes)`);
console.log(`[prehighlight] ${Object.keys(highlighted).length} generated files highlighted (${bytes} bytes)`);
