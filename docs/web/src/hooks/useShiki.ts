import { useEffect, useState } from 'react';
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

function normalizeLanguage(language: string): string {
    const key = language.trim().toLowerCase();
    return LANGUAGE_ALIASES[key] ?? (key || 'text');
}

function resolveLanguage(language: string | LanguageRegistration): string | LanguageRegistration {
    if (typeof language !== 'string') return language;
    const normalized = normalizeLanguage(language);
    return normalized === 'mcfunction' ? MCFUNCTION_LANGUAGE : normalized;
}

function getLanguageName(language: string | LanguageRegistration): string {
    if (typeof language === 'string') return language;
    return language.name ?? language.aliases?.[0] ?? 'text';
}

function escapeHtml(input: string): string {
    return input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

/** Same structure as Shiki's output, one `.line` per line, so the highlighted block replaces it without moving anything. */
function plainPreHtml(code: string): string {
    const lines = code.split('\n').map((line) => `<span class="line">${escapeHtml(line)}</span>`).join('\n');
    return `<pre class="shiki" style="background-color:transparent"><code>${lines}</code></pre>`;
}

/** One theme, or a light and a dark one written into the same markup for index.css to choose from. */
export type CodeTheme = string | { dark: string; light: string };

/** Dark+ colours go inline, so the page reads right before its theme is known, and the light ones into `--shiki-light`. */
function themeOptions(theme: CodeTheme) {
    return typeof theme === 'string' ? { theme } : { themes: theme, defaultColor: 'dark' as const };
}

export function useShiki(code: string, language: string | LanguageRegistration, theme: CodeTheme = 'dark-plus') {
    const [html, setHtml] = useState(() => plainPreHtml(code));

    useEffect(() => {
        let isActive = true;
        const resolvedLanguage = resolveLanguage(language);
        const isCustomLang = typeof resolvedLanguage !== 'string';
        const langName = (isCustomLang
            ? (resolvedLanguage as LanguageRegistration).name
            : resolvedLanguage) ?? 'text';
        const themes = typeof theme === 'string' ? [theme] : [theme.dark, theme.light];

        const isPython = langName === 'python';

        getSingletonHighlighter({
            themes,
            langs: isPython ? PYTHON_WITH_MCFUNCTION : [resolvedLanguage],
        })
            .then((highlighter) => highlighter.codeToHtml(code, {
                lang: langName,
                ...themeOptions(theme),
                // Python strings holding commands are highlighted like the VS Code extension does.
                includeExplanation: isPython ? 'scopeName' : false,
                transformers: [mcfunctionBlocks, pythonSemantics],
            }))
            .then((result) => {
                if (isActive) setHtml(result);
            })
            .catch((err) => {
                if (import.meta.env.DEV) {
                    console.warn('[useShiki] falling back to plain text', {
                        language: getLanguageName(resolvedLanguage),
                        error: err,
                    });
                }
                // If a language is unsupported, gracefully render as plain text.
                getSingletonHighlighter({
                    themes,
                    langs: ['text'],
                })
                    .then((highlighter) => highlighter.codeToHtml(code, {
                        lang: 'text',
                        ...themeOptions(theme),
                    }))
                    .then((result) => {
                        if (isActive) setHtml(result);
                    })
                    .catch(() => {
                        if (isActive) setHtml(plainPreHtml(code));
                    });
            });

        return () => {
            isActive = false;
        };
    }, [code, language, theme]);

    return html;
}
