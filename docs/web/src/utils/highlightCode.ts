/**
 * Shiki with the mcfunction grammars and the transformers that colour code like the VS Code
 * extension. Loaded only when a block was not highlighted at build time: the grammars live in
 * extension/vscode, outside docs/web, so the server image does not have them.
 */
import { getSingletonHighlighter, type ShikiTransformer } from 'shiki';
import type { LanguageRegistration } from '@shikijs/types';
import { MCFUNCTION_LANGUAGE, PYTHON_WITH_MCFUNCTION } from '../langs/mcfunction';
import { pythonSemantics } from './pythonSemantics';
import { mcfunctionBlocks } from './mcfunctionBlocks';
import type { CodeTheme } from '../hooks/useShiki';

const LANGUAGE_ALIASES: Record<string, string> = {
    function: 'mcfunction',
    hs: 'haskell',
    shell: 'bash',
    yml: 'yaml',
    md: 'markdown',
    py: 'python',
};

function languageName(language: string | LanguageRegistration): string {
    if (typeof language !== 'string') return language.name;
    const key = language.trim().toLowerCase();
    return LANGUAGE_ALIASES[key] ?? (key || 'text');
}

/** Loads the language and the themes, then highlights. A language Shiki does not know comes out as plain text. */
export async function highlightCode(code: string, language: string | LanguageRegistration, theme: CodeTheme, transformers: ShikiTransformer[] = []): Promise<string> {
    const themes = typeof theme === 'string' ? [theme] : [theme.dark, theme.light];
    const name = languageName(language);
    const langs = name === 'python' ? PYTHON_WITH_MCFUNCTION : [name === 'mcfunction' ? MCFUNCTION_LANGUAGE : language];
    // Created without the language: an unknown one passed to the first call would leave the shared highlighter broken for good
    const highlighter = await getSingletonHighlighter({ themes, langs: [] });
    const known = name === 'text' || await getSingletonHighlighter({ themes, langs }).then(() => true, (error) => {
        if (import.meta.env.DEV) console.warn(`[highlightCode] "${name}" is shown as plain text`, error);
        return false;
    });

    return highlighter.codeToHtml(code, {
        lang: known ? name : 'text',
        // Dark+ colours go inline, so the page reads right before its theme is known, and the light ones into `--shiki-light`
        ...(typeof theme === 'string' ? { theme } : { themes: theme, defaultColor: 'dark' as const }),
        // Python strings holding commands are highlighted like the VS Code extension does.
        includeExplanation: known && name === 'python' ? 'scopeName' : false,
        transformers: [mcfunctionBlocks, pythonSemantics, ...transformers],
    });
}
