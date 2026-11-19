/**
 * View transitions between two states of a page, and keeping the reader's place across a change
 * that rewrites the text, like a language switch. index.css animates each `kind`.
 */

/** Towards a page further down the page list or back up it, the same page in the other language, or a page picked in the phone's page list. */
export type TransitionKind = 'forward' | 'back' | 'language' | 'panel';

/** Runs `update`, the change of the DOM, as a view transition, or at once where they are missing or motion is reduced. */
export function withViewTransition(kind: TransitionKind, update: () => void): void {
    if (!('startViewTransition' in document) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        update();
        return;
    }
    document.documentElement.dataset.transition = kind;
    document.startViewTransition(update);
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
