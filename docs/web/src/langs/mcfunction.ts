import type { LanguageRegistration } from '@shikijs/types';
import mcfunctionGrammar from './mcfunction.tmLanguage.json';
import embeddedGrammar from '../../../../extension/vscode/syntaxes/mcfunction-embedded.tmLanguage.json';
import injectionGrammar from '../../../../extension/vscode/syntaxes/mcfunction-injection.tmLanguage.json';

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

/** The commands inside a Python string, read straight from the VS Code extension's grammar. */
const MCFUNCTION_EMBEDDED_LANGUAGE: LanguageRegistration = {
    ...(embeddedGrammar as unknown as LanguageRegistration),
    name: 'mcfunction-embedded',
};

/**
 * The extension's injection into `source.python`: it finds `write_function(..., """...""")` and the
 * other helpers, and hands the string body to the embedded grammar above.
 */
const MCFUNCTION_INJECTION: LanguageRegistration = {
    ...(injectionGrammar as unknown as LanguageRegistration),
    name: 'stewbeet-mcfunction-injection',
    injectTo: ['source.python'],
    embeddedLangs: ['mcfunction-embedded'],
};

/**
 * What to load for a Python block. The injection must be registered before Python is first
 * compiled, since a grammar picks up its injections once, so they always travel together.
 */
export const PYTHON_WITH_MCFUNCTION: (string | LanguageRegistration)[] = [MCFUNCTION_EMBEDDED_LANGUAGE, MCFUNCTION_INJECTION, 'python'];

/** Scope the embedded grammar gives to every command inside a Python string. */
export const EMBEDDED_MCFUNCTION_SCOPE = 'source.mcfunction.embedded';
