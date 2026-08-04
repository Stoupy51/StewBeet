/**
 * Runs Shiki over the hero snippet once at build time and writes the markup to
 * src/generated/heroCode.json.
 *
 * The hero code panel is the largest contentful element on the landing page, and it used to
 * be highlighted in a useEffect: plain text painted first, then the whole block was replaced
 * with coloured markup once the highlighter and its grammar had loaded. Doing it here means
 * the correct pixels are in the prerendered HTML and the browser never loads a highlighter
 * for the landing page at all.
 */
import { codeToHtml } from 'shiki';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import { HERO_CODE } from '../src/components/heroCode';

const html = await codeToHtml(HERO_CODE, { lang: 'python', theme: 'dark-plus' });

const outputDir = join(import.meta.dir, '..', 'src', 'generated');
mkdirSync(outputDir, { recursive: true });
writeFileSync(join(outputDir, 'heroCode.json'), `${JSON.stringify({ html }, null, 4)}\n`);

console.log(`[prehighlight] hero snippet highlighted (${html.length} bytes)`);
