import { useEffectEvent, useLayoutEffect, useRef } from 'react';
import { useLocation, useNavigationType } from 'react-router-dom';
import { pageAt } from '../docsPages';

/**
 * Puts a new page at its top, the way a full page load would.
 *
 * The router keeps the scroll offset across a route change, so leaving a long documentation page
 * dropped the visitor halfway down the next one. Back and forward are left alone, since the browser
 * restores those itself, and so is a link carrying an anchor, which scrolls to its own section.
 * Only a new path counts, and not one from a doc page to another: the doc reader scrolls once the
 * next page is ready to replace the one on screen.
 */
export function useScrollToTop(): void {
    const { pathname, hash } = useLocation();
    const navigationType = useNavigationType();
    const previousPath = useRef(pathname);
    const scrollsToTop = useEffectEvent(() => !hash && navigationType !== 'POP' && !(pageAt(previousPath.current) && pageAt(pathname)));

    useLayoutEffect(() => {
        if (scrollsToTop()) window.scrollTo({ top: 0, behavior: 'instant' });
        previousPath.current = pathname;
    }, [pathname]);
}
