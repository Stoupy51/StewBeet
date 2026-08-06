import { useLayoutEffect, useRef } from 'react';
import type { RefObject } from 'react';

/**
 * Decides (once per page load)whether the entrance animation runs, and marks the element
 * that hosts it.
 *
 * The attribute is written in a layout effect rather than through React state, for two
 * reasons. It runs before the browser paints, so nothing shows its finished state and then
 * jumps back to the start; and because the DOM is touched directly, the prerendered markup
 * React hydrates against is untouched: a visitor with no JavaScript, or a crawler that does
 * not run it, gets the finished page rather than a stage waiting for a cue.
 */

const SESSION_KEY = 'stewbeet:intro-played';

/** Memoised so every part of the entrance agrees, whichever asks first. */
let decision: boolean | null = null;

/**
 * The animation is a flourish, not a gate: anything that argues against it means skip.
 * Safe to call from effects only. It records that the intro has been shown.
 */
export function introWillPlay(): boolean {
    if (decision !== null) return decision;
    if (typeof window === 'undefined') return false;

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

/**
 * Returns a ref to attach to the element hosting the entrance. The hook owns the ref rather
 * than accepting one, because marking a node reachable from a hook argument counts as
 * mutating that argument.
 */
export function useIntro<T extends HTMLElement>(): RefObject<T | null> {
    const host = useRef<T | null>(null);

    useLayoutEffect(() => {
        const element = host.current;
        if (element && introWillPlay()) {
            element.dataset.intro = 'play';
        }
    }, []);

    return host;
}
