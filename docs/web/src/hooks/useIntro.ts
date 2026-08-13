import { useLayoutEffect } from 'react';

/**
 * Decides (once per page load) whether the entrance animation runs, and marks the document
 * that hosts it.
 *
 * The decision normally happens in the inline script at the top of index.html, before the
 * browser paints anything. It has to: the prerendered markup React hydrates against contains
 * the finished page, so an attribute written from JavaScript that loads later would show the
 * hero, then rewind it to the start of the animation in full view of the visitor.
 *
 * This hook covers the one case that script skips, a visitor who landed on another page and
 * navigated home, where the hero is created by React and never painted finished first.
 */

const SESSION_KEY = 'stewbeet:intro-played';

/** Memoised so every part of the entrance agrees, whichever asks first. */
let decision: boolean | null = null;

declare global {
    interface Window {
        /** Written by the inline script in index.html, before the first paint. */
        stewbeetIntro?: boolean;
    }
}

/**
 * The animation is a flourish, not a gate: anything that argues against it means skip.
 * Safe to call from effects only. It records that the intro has been shown.
 */
export function introWillPlay(): boolean {
    if (decision !== null) return decision;
    if (typeof window === 'undefined') return false;

    // The inline script already decided for anyone who loaded the home page directly
    if (typeof window.stewbeetIntro === 'boolean') {
        decision = window.stewbeetIntro;
        return decision;
    }

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        decision = false;
        return decision;
    }
    try {
        decision = sessionStorage.getItem(SESSION_KEY) === null;
        sessionStorage.setItem(SESSION_KEY, '1');
    } catch {
        // Private mode with storage disabled: play it, just do not remember.
        decision = true;
    }
    return decision;
}

/** Marks the document so the `[data-intro="play"]` rules in index.css match. */
export function useIntro(): void {
    useLayoutEffect(() => {
        if (introWillPlay()) {
            document.documentElement.dataset.intro = 'play';
        }
    }, []);
}
