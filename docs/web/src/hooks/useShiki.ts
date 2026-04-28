import { useEffect, useState } from 'react';
import { codeToHtml } from 'shiki';

const LANGUAGE_ALIASES: Record<string, string> = {
    function: 'mcfunction',
    mcfunction: 'mcfunction',
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

export function useShiki(code: string, language: string, theme = 'dark-plus') {
    const [html, setHtml] = useState('');

    useEffect(() => {
        let isActive = true;
        const lang = normalizeLanguage(language);

        codeToHtml(code, {
            lang,
            theme,
        })
            .then((result) => {
                if (isActive) setHtml(result);
            })
            .catch(() => {
                // If a language is unsupported, gracefully render as plain text.
                codeToHtml(code, {
                    lang: 'text',
                    theme,
                })
                    .then((result) => {
                        if (isActive) setHtml(result);
                    })
                    .catch(() => {
                        if (isActive) setHtml('');
                    });
            });

        return () => {
            isActive = false;
        };
    }, [code, language, theme]);

    return html;
}
