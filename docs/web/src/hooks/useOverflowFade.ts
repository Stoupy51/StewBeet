import { useCallback } from 'react';

/**
 * A callback ref that sets `data-more` on a scroll container while content remains below its
 * visible area, so the CSS in index.css fades its bottom edge. A clean cut through a line of code
 * reads as broken; a fade reads as "keep scrolling". Scrolled to the end, or with nothing to
 * scroll, the fade goes away. Being a ref, it follows a container that unmounts and comes back.
 */
export function useOverflowFade() {
    return useCallback((element: HTMLElement | null) => {
        if (!element) return;

        const update = () => {
            element.toggleAttribute('data-more', element.scrollHeight - element.scrollTop - element.clientHeight > 1);
        };
        update();
        element.addEventListener('scroll', update, { passive: true });
        const observer = new ResizeObserver(update);
        observer.observe(element);
        Array.from(element.children).forEach((child) => observer.observe(child));

        return () => {
            element.removeEventListener('scroll', update);
            observer.disconnect();
        };
    }, []);
}
