/**
 * Writes the shareable "who makes what" diagram to public/img/stack/, for every language and theme:
 * an animated SVG for the web and GitHub, a PNG for forums, and for the dark theme a looping GIF and
 * MP4 of the finished diagram with its spark running, since Discord previews neither SVG nor its motion.
 *
 * Images are screenshots taken by a local Chrome or Edge, skipped when none is found; set CHROME_PATH
 * to point at one. The GIF and MP4 also need ffmpeg on the PATH. Outputs are committed, so run this
 * after editing src/components/stackDiagram.ts.
 */
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join, resolve } from 'path';
import { pathToFileURL } from 'url';
import { STACK_PALETTES, STACK_SIZE, STACK_TEXT, stackDiagramSvg } from '../src/components/stackDiagram';
import type { Language } from '../src/context/LanguageContext';

const OUTPUT_DIR: string = join(import.meta.dir, '..', 'public', 'img', 'stack');
const FONT_PATH: string = join(import.meta.dir, '..', 'node_modules', '@fontsource-variable', 'archivo', 'files', 'archivo-latin-wght-normal.woff2');

/** One turn of the spark, in seconds: the GIF loops on it, and the 0.8 s flow fits it four times. */
const LOOP_SECONDS = 3.2;
const FPS = 20;

const BROWSER_CANDIDATES: string[] = [
    process.env.CHROME_PATH ?? '',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
];

const fontFaceCss = `@font-face { font-family: 'Archivo Variable'; font-weight: 100 900; src: url(data:font/woff2;base64,${readFileSync(FONT_PATH).toString('base64')}) format('woff2'); }`;
const browser = BROWSER_CANDIDATES.find((path) => path && existsSync(path));
const ffmpeg = Bun.which('ffmpeg');

function screenshot(svg: string, png: string, scale: number): void {
    const page = `${png}.svg`;
    writeFileSync(page, svg);
    Bun.spawnSync([
        browser!, '--headless=new', '--disable-gpu', '--hide-scrollbars', `--force-device-scale-factor=${scale}`,
        `--window-size=${STACK_SIZE.width},${STACK_SIZE.height}`, `--screenshot=${resolve(png)}`, pathToFileURL(page).href,
    ]);
    rmSync(page);
}

/** The finished diagram with the spark and the flow frozen `seconds` into their loop. */
const frameAt = (still: string, seconds: number) => still.replace('</style>', `
.stk .stk-spark { display: inline; filter: drop-shadow(0 0 4px currentColor); animation: stk-current ${LOOP_SECONDS}s linear -${seconds}s infinite paused; }
.stk .stk-flow { display: inline; animation: stk-flow 0.8s linear -${seconds}s infinite paused; }
</style>`);

function writeLoop(still: string, name: string): void {
    const frames = mkdtempSync(join(tmpdir(), 'stk-'));
    const count = Math.round(LOOP_SECONDS * FPS);
    for (let index = 0; index < count; index++) {
        screenshot(frameAt(still, index / FPS), join(frames, `${String(index).padStart(3, '0')}.png`), 1);
    }
    const input = ['-framerate', String(FPS), '-i', join(frames, '%03d.png')];
    Bun.spawnSync([ffmpeg!, '-y', '-loglevel', 'error', ...input, '-vf', 'split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=none', '-loop', '0', join(OUTPUT_DIR, `${name}.gif`)]);
    Bun.spawnSync([ffmpeg!, '-y', '-loglevel', 'error', '-stream_loop', '3', ...input, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', join(OUTPUT_DIR, `${name}.mp4`)]);
    rmSync(frames, { recursive: true });
}

mkdirSync(OUTPUT_DIR, { recursive: true });

for (const language of Object.keys(STACK_TEXT) as Language[]) {
    for (const theme of ['dark', 'light'] as const) {
        const name = `stewbeet-stack.${language}.${theme}`;
        const palette = STACK_PALETTES[theme];
        writeFileSync(join(OUTPUT_DIR, `${name}.svg`), stackDiagramSvg({ language, palette, autoplay: true, fontFaceCss }));
        if (!browser) continue;

        // Taken from a still copy, so a screenshot never catches the build-up halfway
        const still = stackDiagramSvg({ language, palette, autoplay: false, fontFaceCss });
        screenshot(still, join(OUTPUT_DIR, `${name}.png`), 2);
        if (theme === 'dark' && ffmpeg) writeLoop(still, name);
    }
}

console.log(!browser ? 'SVGs written; no Chrome or Edge found, images skipped (set CHROME_PATH)'
    : ffmpeg ? `Stack diagrams written to ${OUTPUT_DIR}` : 'SVGs and PNGs written; no ffmpeg found, GIF and MP4 skipped');
