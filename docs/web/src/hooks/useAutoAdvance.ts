import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { useReducedMotion } from 'framer-motion';

/**
 * Drives a set of panels that rotate on their own, reporting how far through the current one
 * it is so a caller can fill a progress bar or type out a command from the same clock.
 *
 * Tabbed sections that only respond to a click get read as static: a visitor who does not
 * realise the labels are buttons sees one panel and moves on. Rotating shows there is more
 * without asking for anything.
 *
 * Hovering or focusing freezes the clock rather than resetting it, so a long panel can be
 * read at leisure, and the whole thing stands still for anyone who asked for reduced motion.
 */

/** False while server-rendering and on the hydration pass, true once the client owns the DOM. */
const subscribeNever = () => () => {};
const useIsHydrated = () => useSyncExternalStore(subscribeNever, () => true, () => false);

export interface AutoAdvance {
    /** Panel currently on screen. */
    index: number;
    /** How far through the current panel, 0 to 1. Stays 0 until hydration. */
    progress: number;
    /** True once the visitor has taken over, if the caller asked to stop on selection. */
    stopped: boolean;
    /** Every panel shown so far, so a caller can mount a panel once and keep it. */
    visited: ReadonlySet<number>;
    /** Show a panel now. */
    select: (index: number) => void;
    /** Spread onto the element that should freeze the rotation while it is hovered or focused. */
    holdProps: {
        onMouseEnter: () => void;
        onMouseLeave: () => void;
        onFocusCapture: () => void;
        onBlurCapture: () => void;
    };
}

export interface AutoAdvanceOptions {
    /** Number of panels to cycle through. */
    count: number;
    /** Milliseconds the panel at `index` stays on screen. */
    durationFor: (index: number) => number;
    /** Stop rotating once the visitor picks a panel, rather than resuming from it. */
    stopOnSelect?: boolean;
    /** Hold at the first panel until this is true, so the rotation starts when it is watched. */
    enabled?: boolean;
}

export function useAutoAdvance({ count, durationFor, stopOnSelect = false, enabled = true }: AutoAdvanceOptions): AutoAdvance {
    const [index, setIndex] = useState(0);
    const [progress, setProgress] = useState(0);
    const [visited, setVisited] = useState<ReadonlySet<number>>(() => new Set([0]));
    const [stopped, setStopped] = useState(false);
    const hydrated = useIsHydrated();
    const prefersReducedMotion = useReducedMotion() === true;
    const heldRef = useRef(false);

    const total = durationFor(index);
    const running = hydrated && enabled && !prefersReducedMotion && !stopped;

    useEffect(() => {
        if (!running) return;

        let frame = 0;
        let start = performance.now();
        let lastTick = start;

        const tick = (now: number) => {
            if (heldRef.current) {
                start += now - lastTick;
            }
            lastTick = now;

            const elapsed = now - start;
            if (elapsed >= total) {
                setProgress(0);
                setIndex((current) => {
                    const next = (current + 1) % count;
                    setVisited((seen) => seen.has(next) ? seen : new Set(seen).add(next));
                    return next;
                });
                return;
            }
            setProgress(elapsed / total);
            frame = requestAnimationFrame(tick);
        };

        frame = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(frame);
    }, [index, running, total, count]);

    const select = useCallback((next: number) => {
        setIndex(next);
        setVisited((seen) => seen.has(next) ? seen : new Set(seen).add(next));
        setProgress(0);
        if (stopOnSelect) setStopped(true);
    }, [stopOnSelect]);

    const hold = useCallback((held: boolean) => { heldRef.current = held; }, []);

    return {
        index,
        progress: running ? progress : 0,
        stopped,
        visited,
        select,
        holdProps: {
            onMouseEnter: () => hold(true),
            onMouseLeave: () => hold(false),
            onFocusCapture: () => hold(true),
            onBlurCapture: () => hold(false),
        },
    };
}
