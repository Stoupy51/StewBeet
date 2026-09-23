import { useEffect } from 'react';

/**
 * Fades each `[data-rise]` element in the first time it scrolls into view.
 *
 * Elements already on screen (or above it) are marked risen before `data-motion` is set, so a
 * visible section never blinks. Without JavaScript, or with reduced motion, `data-motion` is never
 * set and the CSS in index.css hides nothing.
 */
export function useReveal(): void {
    useEffect(() => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        const targets = Array.from(document.querySelectorAll<HTMLElement>('[data-rise]:not([data-risen])'));
        const rise = (element: Element) => element.setAttribute('data-risen', '');
        const pending = targets.filter((element) => {
            if (element.getBoundingClientRect().top < window.innerHeight) {
                rise(element);
                return false;
            }
            return true;
        });

        document.documentElement.dataset.motion = 'on';
        const observer = new IntersectionObserver((entries) => {
            for (const entry of entries.filter((entry) => entry.isIntersecting)) {
                rise(entry.target);
                observer.unobserve(entry.target);
            }
        }, { rootMargin: '0px 0px -10% 0px' });
        pending.forEach((element) => observer.observe(element));

        return () => {
            observer.disconnect();
            delete document.documentElement.dataset.motion;
        };
    }, []);
}
