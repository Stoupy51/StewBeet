import type { ShikiTransformer, ThemedToken } from 'shiki';
import { EMBEDDED_MCFUNCTION_SCOPE } from '../langs/mcfunction';

/**
 * Draws the block the VS Code extension draws around commands written inside a Python string.
 *
 * Needs `includeExplanation`, which is how a token says it came from the embedded grammar. Lines
 * are marked in the `tokens` hook, before `pythonSemantics` splits tokens and drops that
 * explanation, then classed in the `line` hook so index.css can paint the block: `mcf-line` on
 * every line, `mcf-first` and `mcf-last` where it opens and closes.
 */

interface BlockMeta {
    mcfLines?: Set<number>;
}

export function isEmbeddedMcfunction(token: ThemedToken): boolean {
    return token.explanation?.some((part) => part.scopes.some((scope) => scope.scopeName === EMBEDDED_MCFUNCTION_SCOPE)) ?? false;
}

/**
 * 1-based numbers of the lines inside a block. A blank line has no token to carry the scope, so it
 * belongs to a block when the nearest non-blank lines on both sides do.
 */
function blockLines(lines: ThemedToken[][]): Set<number> {
    const blank = lines.map((line) => line.every((token) => token.content.trim() === ''));
    const marked = lines.map((line) => line.some(isEmbeddedMcfunction));
    const nearest = (from: number, step: number): boolean => {
        for (let index = from; index >= 0 && index < lines.length; index += step) {
            if (!blank[index]) return marked[index];
        }
        return false;
    };
    return new Set(lines.flatMap((_, index) => (
        marked[index] || (blank[index] && nearest(index - 1, -1) && nearest(index + 1, 1)) ? [index + 1] : []
    )));
}

export const mcfunctionBlocks: ShikiTransformer = {
    name: 'stewbeet-mcfunction-blocks',
    tokens(lines) {
        (this.meta as BlockMeta).mcfLines = blockLines(lines);
    },
    line(node, line) {
        const lines = (this.meta as BlockMeta).mcfLines;
        if (!lines?.has(line)) return;
        this.addClassToHast(node, 'mcf-line');
        if (!lines.has(line - 1)) this.addClassToHast(node, 'mcf-first');
        if (!lines.has(line + 1)) this.addClassToHast(node, 'mcf-last');
    },
};
