import { useLayoutEffect } from 'react';
import { useLocation, useNavigationType } from 'react-router-dom';

/**
 * Puts a new page at its top, the way a full page load would.
 *
 * The router keeps the scroll offset across a route change, so leaving a long documentation page
 * dropped the visitor halfway down the next one. Back and forward are left alone, since the browser
 * restores those itself, and so is a link carrying an anchor, which scrolls to its own section.
 */
export function useScrollToTop(): void {
    const { pathname, hash } = useLocation();
    const navigationType = useNavigationType();

    useLayoutEffect(() => {
        if (hash || navigationType === 'POP') return;
        window.scrollTo({ top: 0 });
    }, [pathname, hash, navigationType]);
}
