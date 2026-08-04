import type { ShikiTransformer, ThemedToken } from 'shiki';

/**
 * Adds the colours VS Code gets from Pylance and Shiki cannot.
 *
 * Shiki highlights with a TextMate grammar, which matches patterns rather than resolving
 * symbols, so it emits `DIAMOND_PICKAXE = VanillaEquipments.PICKAXE.value[DefaultOre.DIAMOND]`
 * as a single foreground-coloured token. VS Code colours that line from semantic tokens
 * supplied by a language server — something that cannot run in a browser or a build script.
 *
 * The gap is closed here by splitting plain tokens on identifier boundaries and colouring
 * each by shape, which is what the eye is reading anyway: SCREAMING_SNAKE is a constant,
 * PascalCase is a type, and a name directly before `(` is being called.
 *
 * Only tokens the grammar left as plain foreground or variable-blue are touched, so strings,
 * comments, numbers and keywords keep the colours the grammar already resolved correctly.
 */

/** Dark Plus semantic colours, matching what Pylance produces in VS Code. */
const CONSTANT = '#4FC1FF';
const TYPE = '#4EC9B0';
const FUNCTION = '#DCDCAA';

/** Colours the grammar assigns to unresolved identifiers, and which we may reassign. */
const PLAIN = new Set(['#D4D4D4', '#9CDCFE']);

/** Builtin types the grammar only recognises in some positions, e.g. `dict` in an annotation. */
const BUILTIN_TYPES = new Set([
    'dict', 'list', 'set', 'tuple', 'frozenset', 'int', 'float', 'complex',
    'bool', 'bytes', 'bytearray', 'object', 'type',
]);

/** Names that look like calls but are language constructs the grammar already styles. */
const KEYWORDS = new Set([
    'if', 'else', 'elif', 'for', 'while', 'return', 'yield', 'import', 'from', 'as',
    'def', 'class', 'with', 'try', 'except', 'finally', 'raise', 'assert', 'lambda',
    'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False', 'print',
]);

const IDENTIFIER = /[A-Za-z_][A-Za-z0-9_]*/g;

function classify(name: string, followedByCall: boolean): string | null {
    if (KEYWORDS.has(name)) return null;
    if (BUILTIN_TYPES.has(name)) return TYPE;
    // SCREAMING_SNAKE_CASE — module constants and enum members alike.
    if (/^[A-Z][A-Z0-9_]*$/.test(name) && name.length > 1) return CONSTANT;
    if (/^[A-Z][A-Za-z0-9_]*$/.test(name)) return TYPE;
    if (followedByCall) return FUNCTION;
    return null;
}

/** Splits one plain token into runs, giving identifiers their semantic colour. */
function splitToken(token: ThemedToken): ThemedToken[] {
    const text = token.content;
    const pieces: ThemedToken[] = [];
    let cursor = 0;

    IDENTIFIER.lastIndex = 0;
    for (let match = IDENTIFIER.exec(text); match !== null; match = IDENTIFIER.exec(text)) {
        const name = match[0];
        const start = match.index;
        // A `(` straight after the name — allowing no space — means it is being called.
        const color = classify(name, text[start + name.length] === '(');
        if (color === null) continue;

        if (start > cursor) {
            pieces.push({ ...token, content: text.slice(cursor, start), offset: token.offset + cursor });
        }
        pieces.push({ ...token, content: name, offset: token.offset + start, color });
        cursor = start + name.length;
    }

    if (pieces.length === 0) return [token];
    if (cursor < text.length) {
        pieces.push({ ...token, content: text.slice(cursor), offset: token.offset + cursor });
    }
    return pieces;
}

/**
 * Examples:
 *   >>> // "ORES_CONFIGS: dict[" becomes three tokens: constant, plain, type
 *   >>> // "generate_everything(x)" becomes a function-coloured name plus plain punctuation
 */
export const pythonSemantics: ShikiTransformer = {
    name: 'python-semantics',
    tokens(lines) {
        if (this.options.lang !== 'python') return;
        return lines.map((line) =>
            line.flatMap((token) => (token.color && PLAIN.has(token.color) ? splitToken(token) : [token])),
        );
    },
};
