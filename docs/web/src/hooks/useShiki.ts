import { createContext, useContext, useEffect, useState } from 'react';
import type { LanguageRegistration } from '@shikijs/types';

/** One theme, or a light and a dark one written into the same markup for index.css to choose from. */
export type CodeTheme = string | { dark: string; light: string };

/** VS Code's two default themes, for code that follows the page's theme. */
export const PAGE_THEMES = { dark: 'dark-plus', light: 'light-plus' };

function escapeHtml(input: string): string {
    return input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

/** Same structure as Shiki's output, one `.line` per line, so the highlighted block replaces it without moving anything. */
function plainPreHtml(code: string): string {
    const lines = code.split(/\r?\n/).map((line) => `<span class="line">${escapeHtml(line)}</span>`).join('\n');
    return `<pre class="shiki" style="background-color:transparent"><code>${lines}</code></pre>`;
}

/**
 * The block's key in the highlighting scripts/highlight-docs.ts does at build time for every page
 * of the docs: FNV-1a of the fence's language and the code.
 */
export function codeKey(language: string, code: string): string {
    const text = `${language}\n${code}`;
    let hash = 0x811c9dc5;
    for (let index = 0; index < text.length; index++) hash = Math.imul(hash ^ text.charCodeAt(index), 0x01000193);
    return (hash >>> 0).toString(36);
}

/** The markup scripts/highlight-docs.ts wrote for the page shown, by `codeKey`: a block found there is never highlighted again. */
export const PrehighlightedCode = createContext<Record<string, string>>({});

export function useShiki(code: string, language: string | LanguageRegistration, theme: CodeTheme = 'dark-plus'): string {
    const prebuilt = useContext(PrehighlightedCode)[typeof language === 'string' ? codeKey(language, code) : ''];
    const [highlighted, setHighlighted] = useState<{ code: string; html: string } | null>(null);

    useEffect(() => {
        if (prebuilt) return;
        let isActive = true;
        import('../utils/highlightCode')
            .then(({ highlightCode }) => highlightCode(code, language, theme))
            .then((html) => isActive && setHighlighted({ code, html }))
            .catch(() => undefined);
        return () => {
            isActive = false;
        };
    }, [prebuilt, code, language, theme]);

    return prebuilt ?? (highlighted?.code === code ? highlighted.html : plainPreHtml(code));
}
