import { useEffect, useState } from 'react';
import { getSingletonHighlighter } from 'shiki';
import type { LanguageRegistration } from '@shikijs/types';
import mcfunctionGrammar from '../langs/mcfunction.tmLanguage.json';

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

const MCFUNCTION_LANGUAGE: LanguageRegistration = {
    ...(mcfunctionGrammar as unknown as LanguageRegistration),
    name: 'mcfunction',
    // Do not include the language name itself as alias to avoid circular alias resolution.
    aliases: ['function'],
};

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

function plainPreHtml(code: string): string {
    return `<pre class="shiki" style="background-color:transparent"><code>${escapeHtml(code)}</code></pre>`;
}

export function useShiki(code: string, language: string | LanguageRegistration, theme = 'dark-plus') {
    const [html, setHtml] = useState(() => plainPreHtml(code));

    useEffect(() => {
        let isActive = true;
        const resolvedLanguage = resolveLanguage(language);
        const isCustomLang = typeof resolvedLanguage !== 'string';
        const langName = (isCustomLang
            ? (resolvedLanguage as LanguageRegistration).name
            : resolvedLanguage) ?? 'text';

        getSingletonHighlighter({
            themes: [theme],
            langs: [resolvedLanguage],
        })
            .then((highlighter) => highlighter.codeToHtml(code, {
                lang: langName,
                theme,
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
                    themes: [theme],
                    langs: ['text'],
                })
                    .then((highlighter) => highlighter.codeToHtml(code, {
                        lang: 'text',
                        theme,
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
