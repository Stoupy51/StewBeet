/**
 * Writes the shareable "who makes what" diagram to public/img/stack/, for every language and theme:
 * an animated SVG for the web and GitHub, and a PNG for Discord and forums, which do not animate SVG.
 *
 * The PNG is a screenshot taken by a local Chrome or Edge, skipped when none is found; set CHROME_PATH
 * to point at one. Outputs are committed, so run this after editing src/components/stackDiagram.ts.
 */
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'fs';
import { join, resolve } from 'path';
import { pathToFileURL } from 'url';
import { STACK_PALETTES, STACK_SIZE, STACK_TEXT, stackDiagramSvg } from '../src/components/stackDiagram';
import type { Language } from '../src/context/LanguageContext';

const OUTPUT_DIR: string = join(import.meta.dir, '..', 'public', 'img', 'stack');
const FONT_PATH: string = join(import.meta.dir, '..', 'node_modules', '@fontsource-variable', 'ibm-plex-sans', 'files', 'ibm-plex-sans-latin-wght-normal.woff2');

const BROWSER_CANDIDATES: string[] = [
    process.env.CHROME_PATH ?? '',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
];

const fontFaceCss = `@font-face { font-family: 'IBM Plex Sans Variable'; font-weight: 100 700; src: url(data:font/woff2;base64,${readFileSync(FONT_PATH).toString('base64')}) format('woff2'); }`;
const browser = BROWSER_CANDIDATES.find((path) => path && existsSync(path));

mkdirSync(OUTPUT_DIR, { recursive: true });

for (const language of Object.keys(STACK_TEXT) as Language[]) {
    for (const theme of ['dark', 'light'] as const) {
        const name = `stewbeet-stack.${language}.${theme}`;
        const palette = STACK_PALETTES[theme];
        writeFileSync(join(OUTPUT_DIR, `${name}.svg`), stackDiagramSvg({ language, palette, autoplay: true, fontFaceCss }));
        if (!browser) continue;

        // The PNG is taken from a still copy, so the screenshot never catches the animation halfway
        const still = join(OUTPUT_DIR, `${name}.still.svg`);
        writeFileSync(still, stackDiagramSvg({ language, palette, autoplay: false, fontFaceCss }));
        Bun.spawnSync([
            browser, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
            `--window-size=${STACK_SIZE.width},${STACK_SIZE.height}`,
            `--screenshot=${resolve(OUTPUT_DIR, `${name}.png`)}`,
            pathToFileURL(still).href,
        ]);
        rmSync(still);
    }
}

console.log(browser ? `Stack diagrams written to ${OUTPUT_DIR}` : 'SVGs written; no Chrome or Edge found, PNGs skipped (set CHROME_PATH)');
