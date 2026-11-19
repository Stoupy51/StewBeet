import { createContext, useContext, useEffect, useState } from 'react';
import { getSingletonHighlighter } from 'shiki';
import type { LanguageRegistration } from '@shikijs/types';
import { MCFUNCTION_LANGUAGE, PYTHON_WITH_MCFUNCTION } from '../langs/mcfunction';
import { pythonSemantics } from '../utils/pythonSemantics';
import { mcfunctionBlocks } from '../utils/mcfunctionBlocks';

const LANGUAGE_ALIASES: Record<string, string> = {
    function: 'mcfunction',
    hs: 'haskell',
    shell: 'bash',
    yml: 'yaml',
    md: 'markdown',
    py: 'python',
};

/** One theme, or a light and a dark one written into the same markup for index.css to choose from. */
export type CodeTheme = string | { dark: string; light: string };

/** VS Code's two default themes, for code that follows the page's theme. */
export const PAGE_THEMES = { dark: 'dark-plus', light: 'light-plus' };

function languageName(language: string | LanguageRegistration): string {
    if (typeof language !== 'string') return language.name;
    const key = language.trim().toLowerCase();
    return LANGUAGE_ALIASES[key] ?? (key || 'text');
}

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
 * The block's key in the highlighting scripts/prehighlight.ts does at build time for every page
 * of the docs: FNV-1a of the language and the code.
 */
export function codeKey(language: string, code: string): string {
    const text = `${languageName(language)}\n${code}`;
    let hash = 0x811c9dc5;
    for (let index = 0; index < text.length; index++) hash = Math.imul(hash ^ text.charCodeAt(index), 0x01000193);
    return (hash >>> 0).toString(36);
}

/** Loads the language and the themes, then highlights. A language Shiki does not know comes out as plain text. */
export async function highlightCode(code: string, language: string | LanguageRegistration, theme: CodeTheme): Promise<string> {
    const themes = typeof theme === 'string' ? [theme] : [theme.dark, theme.light];
    const name = languageName(language);
    const langs = name === 'python' ? PYTHON_WITH_MCFUNCTION : [name === 'mcfunction' ? MCFUNCTION_LANGUAGE : language];
    // Created without the language: an unknown one passed to the first call would leave the shared highlighter broken for good
    const highlighter = await getSingletonHighlighter({ themes, langs: [] });
    const known = name === 'text' || await getSingletonHighlighter({ themes, langs }).then(() => true, (error) => {
        if (import.meta.env.DEV) console.warn(`[useShiki] "${name}" is shown as plain text`, error);
        return false;
    });

    return highlighter.codeToHtml(code, {
        lang: known ? name : 'text',
        // Dark+ colours go inline, so the page reads right before its theme is known, and the light ones into `--shiki-light`
        ...(typeof theme === 'string' ? { theme } : { themes: theme, defaultColor: 'dark' as const }),
        // Python strings holding commands are highlighted like the VS Code extension does.
        includeExplanation: known && name === 'python' ? 'scopeName' : false,
        transformers: [mcfunctionBlocks, pythonSemantics],
    });
}

/** The markup scripts/highlight-docs.ts wrote for the page shown, by `codeKey`: a block found there is never highlighted again. */
export const PrehighlightedCode = createContext<Record<string, string>>({});

export function useShiki(code: string, language: string | LanguageRegistration, theme: CodeTheme = 'dark-plus'): string {
    const prebuilt = useContext(PrehighlightedCode)[typeof language === 'string' ? codeKey(language, code) : ''];
    const [highlighted, setHighlighted] = useState<{ code: string; html: string } | null>(null);

    useEffect(() => {
        if (prebuilt) return;
        let isActive = true;
        highlightCode(code, language, theme)
            .then((html) => isActive && setHighlighted({ code, html }))
            .catch(() => undefined);
        return () => {
            isActive = false;
        };
    }, [prebuilt, code, language, theme]);

    return prebuilt ?? (highlighted?.code === code ? highlighted.html : plainPreHtml(code));
}
