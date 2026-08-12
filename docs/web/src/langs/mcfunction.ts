import type { LanguageRegistration } from '@shikijs/types';
import mcfunctionGrammar from './mcfunction.tmLanguage.json';

/**
 * Shiki bundles no `mcfunction` grammar, so the site ships its own and registers it as a custom
 * language.
 *
 * It lives here rather than next to one of its callers because there are two: `useShiki` uses it
 * in the browser for documentation and the features section, and `scripts/prehighlight.ts` uses it
 * at build time for the hero's generated files. One registration means one set of colours, which
 * is the whole point: the same `.mcfunction` has to look the same everywhere on the site.
 */
export const MCFUNCTION_LANGUAGE: LanguageRegistration = {
    ...(mcfunctionGrammar as unknown as LanguageRegistration),
    name: 'mcfunction',
    // Do not include the language name itself as alias to avoid circular alias resolution.
    aliases: ['function'],
};
