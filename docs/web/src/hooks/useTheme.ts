import { useCallback, useEffect, useSyncExternalStore } from 'react';

export type ThemePreference = 'system' | 'light' | 'dark';

/** Also read by the inline script in index.html, which applies the theme before the first paint. */
const STORAGE_KEY = 'stewbeet:theme';
const LIGHT_QUERY = '(prefers-color-scheme: light)';

const listeners = new Set<() => void>();

/** Kept in memory as well, so the choice holds for the visit when storage is blocked. */
let current: ThemePreference | null = null;

function readPreference(): ThemePreference {
    if (current) return current;
    try {
        const stored = window.localStorage.getItem(STORAGE_KEY);
        current = stored === 'light' || stored === 'dark' ? stored : 'system';
    } catch {
        current = 'system';
    }
    return current;
}

function applyTheme(preference: ThemePreference) {
    const light = preference === 'light' || (preference === 'system' && window.matchMedia(LIGHT_QUERY).matches);
    document.documentElement.dataset.theme = light ? 'light' : 'dark';
}

function subscribe(listener: () => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
}

/** The prerendered HTML is built with 'system', so hydration starts there and then catches up. */
export function useTheme() {
    const preference = useSyncExternalStore(subscribe, readPreference, () => 'system' as const);

    useEffect(() => {
        if (preference !== 'system') return;
        const query = window.matchMedia(LIGHT_QUERY);
        const follow = () => applyTheme('system');
        query.addEventListener('change', follow);
        return () => query.removeEventListener('change', follow);
    }, [preference]);

    const setPreference = useCallback((next: ThemePreference) => {
        current = next;
        try {
            window.localStorage.setItem(STORAGE_KEY, next);
        } catch {
            // Storage disabled: the choice still lasts until the tab closes
        }
        applyTheme(next);
        listeners.forEach((listener) => listener());
    }, []);

    return { preference, setPreference };
}
