/**
 * View transitions between two states of a page, and keeping the reader's place across a change
 * that rewrites the text, like a language switch. index.css animates each `kind`.
 */

/** To another page, the same page in the other language, or a page picked in the phone's page list. */
export type TransitionKind = 'page' | 'language' | 'panel';

/** Runs `update`, the change of the DOM, as a view transition, or at once where they are missing or motion is reduced. */
export function withViewTransition(kind: TransitionKind, update: () => void): void {
    if (!('startViewTransition' in document) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        update();
        return;
    }
    writePixelKeyframes();
    document.documentElement.dataset.transition = kind;
    document.startViewTransition(update);
}

const CELL = 16;
const TILE_CELLS = 16;
const PIXEL_FRAMES = 10;

/**
 * Writes `doc-pixels-in`, masks showing a 16 px grid cell by cell in a random order, and
 * `doc-pixels-out`, the cells not shown yet, which index.css runs on the new and the old page.
 */
function writePixelKeyframes(): void {
    if (document.getElementById('doc-pixels')) return;
    const ranks = Array.from({ length: TILE_CELLS ** 2 }, () => Math.random());
    const mask = (isShown: (rank: number) => boolean) => {
        const cells = ranks.map((rank, cell) => isShown(rank) ? `M${(cell % TILE_CELLS) * CELL} ${Math.floor(cell / TILE_CELLS) * CELL}h${CELL}v${CELL}h-${CELL}z` : '');
        const size = CELL * TILE_CELLS;
        return `url("data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"><path d="${cells.join('')}"/></svg>`)}")`;
    };
    const keyframes = (name: string, isShown: (rank: number, progress: number) => boolean) => `@keyframes ${name} {${
        Array.from({ length: PIXEL_FRAMES + 1 }, (_, frame) => `${(frame * 100) / PIXEL_FRAMES}% { mask-image: ${mask((rank) => isShown(rank, frame / PIXEL_FRAMES))}; }`).join('')
    }}`;

    const style = document.createElement('style');
    style.id = 'doc-pixels';
    style.textContent = keyframes('doc-pixels-in', (rank, progress) => rank < progress) + keyframes('doc-pixels-out', (rank, progress) => rank >= progress);
    document.head.append(style);
}

/** The last heading above the top of the screen, -1 above the first one, and how far the reader is towards the next. */
export interface ReadingPosition {
    heading: number;
    progress: number;
}

function headingTops(): number[] {
    return [...document.querySelectorAll('#root :is(h1, h2, h3)')].map((element) => element.getBoundingClientRect().top + window.scrollY);
}

function sectionBounds(tops: number[], heading: number): [number, number] {
    return [tops[heading] ?? 0, tops[heading + 1] ?? document.documentElement.scrollHeight];
}

export function readingPosition(): ReadingPosition {
    const tops = headingTops();
    const heading = tops.filter((top) => top <= window.scrollY).length - 1;
    const [start, end] = sectionBounds(tops, heading);
    return { heading, progress: end > start ? (window.scrollY - start) / (end - start) : 0 };
}

/** Scrolls the rewritten page so the reader is as far into the same section as before. */
export function restoreReadingPosition({ heading, progress }: ReadingPosition): void {
    const [start, end] = sectionBounds(headingTops(), heading);
    window.scrollTo({ top: start + progress * (end - start), behavior: 'instant' });
}
