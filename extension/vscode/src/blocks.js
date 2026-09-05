// @ts-check
"use strict";

// Pure text-scanning logic for locating mcfunction string blocks inside
// StewBeet write_* calls. Kept free of any "vscode" dependency so it can be
// unit-tested with plain Node (see test/blocks.test.js).

// Constants

/** The StewBeet functions that take mcfunction content. */
const WRITE_FUNCS = [
  "write_function",
  "write_versioned_function",
  "write_scheduled_function",
  "write_load_file",
  "write_unload_file",
  "write_tick_file",
];

/** A call to any of them, or to any name in `names`. */
function callRegex(names = WRITE_FUNCS) {
  return new RegExp(`\\b(${names.join("|")})\\s*\\(`, "g");
}

const FUNC_RE = callRegex();

/** Functions where the mcfunction content is the 2nd argument (after a path). */
const FUNCS_2ND_ARG = new Set([
  "write_function",
  "write_versioned_function",
  "write_scheduled_function",
]);

/** A `def`, with its parameter list, so a project's own wrappers can be found. */
const DEF_RE = /\bdef\s+([A-Za-z_]\w*)\s*\(([^)]*)\)/g;

/** A parameter annotated McFunction, ex: `content: McFunction = ""`. */
const MCFUNCTION_PARAM_RE = /^\s*[A-Za-z_]\w*\s*:\s*McFunction\b/;

// String scanning

/**
 * Return the string prefix letters (e.g. "f", "rf") sitting immediately before
 * a quote, or "" when the preceding letters don't form a Python string prefix.
 * @param {string} text
 * @param {number} quoteIdx  Index of the opening quote character.
 */
function stringPrefixAt(text, quoteIdx) {
  let j = quoteIdx;
  while (j > 0 && /[A-Za-z]/.test(text[j - 1])) j--;
  const run = text.slice(j, quoteIdx);
  return /^[rRbBuUfF]{1,2}$/.test(run) ? run : "";
}

/**
 * Find the index of the closing quote of a string whose content starts at `from`.
 * For f-strings, `{...}` interpolations are skipped entirely: they may contain
 * nested strings (including triple-quoted f-strings) whose quotes must not be
 * mistaken for the closing quote.
 * @param {string} text
 * @param {string} quoteStyle  One of `"""`, `'''`, `"`, `'`.
 * @param {number} from  Index of the first content character.
 * @param {boolean} [isFString]
 * @returns {number}  Index of the closing quote, or -1 if unterminated.
 */
function findClosingQuote(text, quoteStyle, from, isFString = false) {
  const multiline = quoteStyle.length === 3;
  let i = from;
  while (i < text.length) {
    if (text.startsWith(quoteStyle, i)) return i;
    const c = text[i];
    if (!multiline && c === "\n") return -1;
    if (c === "\\") { i += 2; continue; }
    if (isFString && c === "{") {
      if (text[i + 1] === "{") { i += 2; continue; } // literal {{
      i = skipInterpolation(text, i + 1);
      if (i === -1) return -1;
      continue;
    }
    i++;
  }
  return -1;
}

/**
 * Skip a Python f-string interpolation body, starting just after its `{`.
 * Handles nested parens/brackets/braces and nested string literals.
 * @param {string} text
 * @param {number} i  Index just after the opening `{`.
 * @returns {number}  Index just after the matching `}`, or -1.
 */
function skipInterpolation(text, i) {
  let depth = 0;
  while (i < text.length) {
    const c = text[i];
    if (c === "}") {
      if (depth === 0) return i + 1;
      depth--; i++; continue;
    }
    if (c === "(" || c === "[" || c === "{") { depth++; i++; continue; }
    if (c === ")" || c === "]") { depth--; i++; continue; }
    if (c === '"' || c === "'") {
      const style = text.startsWith(c.repeat(3), i) ? c.repeat(3) : c;
      const isF = /[fF]/.test(stringPrefixAt(text, i));
      const close = findClosingQuote(text, style, i + style.length, isF);
      if (close === -1) return -1;
      i = close + style.length;
      continue;
    }
    i++;
  }
  return -1;
}

// Block detection

/**
 * Skip past the first argument of a write_* call (the path), stopping just
 * after the separating comma. Handles nested parens/brackets and strings.
 * Returns the index of the first non-whitespace character after the comma, or -1.
 * @param {string} text
 * @param {number} start  Index just after the opening '(' of the call.
 */
function skipFirstArg(text, start) {
  let i = start;
  let depth = 0;

  while (i < text.length) {
    const c = text[i];

    if (c === "(" || c === "[" || c === "{") { depth++; i++; continue; }
    if (c === ")" || c === "]" || c === "}") {
      if (depth === 0) return -1;
      depth--; i++; continue;
    }
    if (depth === 0 && c === ",") {
      i++;
      while (i < text.length && /[ \t\r\n]/.test(text[i])) i++;
      return i;
    }

    // Skip over string literals so their commas/brackets are ignored.
    if (c === '"' || c === "'") {
      const style = text.startsWith(c.repeat(3), i) ? c.repeat(3) : c;
      const isF = /[fF]/.test(stringPrefixAt(text, i));
      const close = findClosingQuote(text, style, i + style.length, isF);
      if (close === -1) return -1;
      i = close + style.length;
      continue;
    }

    i++;
  }
  return -1;
}

/**
 * Read the opening quote (optionally preceded by a string prefix like f/rf)
 * at position i, skipping leading whitespace.
 * Returns { quoteStyle, quoteStart, contentStart, isFString } or null.
 * quoteStart includes the prefix if present.
 * @param {string} text
 * @param {number} i
 */
function readOpeningQuote(text, i) {
  while (i < text.length && /[ \t\r\n]/.test(text[i])) i++;
  const start = i;
  let isFString = false;
  while (i < text.length && i - start < 2 && /[A-Za-z]/.test(text[i])) {
    if (text[i] === "f" || text[i] === "F") isFString = true;
    i++;
  }
  for (const qs of ['"""', "'''", '"', "'"]) {
    if (text.startsWith(qs, i)) {
      return { quoteStyle: qs, quoteStart: start, contentStart: i + qs.length, isFString };
    }
  }
  return null;
}

/**
 * Find all mcfunction string blocks in Python source text.
 * @param {string} text
 * @returns {{ start:number, end:number, contentStart:number, contentEnd:number }[]}
 *   `start` is the opening quote with its prefix and `end` is just past the closing quote,
 *   which is what a decoration should cover. `contentStart` and `contentEnd` bound the
 *   commands alone: the quotes are Python, and a projection that hands them to a datapack
 *   parser gets told, correctly, that `\"\"\"` is not a command. `callStart` is the offset of
 *   the `write_*` call these commands reach, which is the block itself when they are written
 *   inline and a line further down when they arrive in a variable.
 */
function findBlockOffsets(text) {
  const blocks = [];
  /** Names handed to a write_* call instead of a literal, mapped to that call's offset. */
  const variables = new Map();
  const wrappers = mcfunctionWrappers(text);
  const callRe = wrappers.size === 0 ? FUNC_RE : callRegex([...wrappers.keys(), ...WRITE_FUNCS]);

  callRe.lastIndex = 0;
  let m;
  while ((m = callRe.exec(text)) !== null) {
    const afterOpen = m.index + m[0].length;

    const argIndex = wrappers.has(m[1]) ? wrappers.get(m[1]) : Number(FUNCS_2ND_ARG.has(m[1]));
    let contentIdx = afterOpen;
    for (let skipped = 0; skipped < argIndex; skipped++) {
      contentIdx = skipFirstArg(text, contentIdx);
      if (contentIdx === -1) break;
    }
    if (contentIdx === -1) continue;

    const opening = readOpeningQuote(text, contentIdx);
    if (!opening) {
      const name = readArgumentName(text, contentIdx);
      if (name && !variables.has(name)) variables.set(name, m.index);
      continue;
    }

    const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart, opening.isFString);
    if (closeIdx === -1) continue;

    blocks.push({
      start: opening.quoteStart, end: closeIdx + opening.quoteStyle.length,
      contentStart: opening.contentStart, contentEnd: closeIdx, callStart: m.index,
    });
  }

  if (variables.size > 0) blocks.push(...findAssignedBlocks(text, variables));
  return blocks.sort((a, b) => a.start - b.start);
}

/**
 * The project's own functions taking commands, mapped to which argument carries them.
 *
 * `def write(path: str, cont: McFunction)` makes `write("say hi")`'s second argument a block,
 * the same as `write_function`'s. A grammar cannot do this, since the `def` and the call share
 * no text, but a scan of the whole document can.
 *
 * @param {string} text
 * @returns {Map<string, number>}  0-based index of the annotated parameter.
 *
 * >>> mcfunctionWrappers("def w(p: str, c: McFunction): pass")
 * Map(1) { 'w' => 1 }
 */
function mcfunctionWrappers(text) {
  const found = new Map();
  DEF_RE.lastIndex = 0;
  let m;
  while ((m = DEF_RE.exec(text)) !== null) {
    const params = splitParams(m[2]);
    const index = params.findIndex(p => MCFUNCTION_PARAM_RE.test(p));
    // `self` never carries commands, and counting it would shift every call site's argument.
    const offset = /^\s*(self|cls)\s*(?:[,:]|$)/.test(params[0] ?? "") ? 1 : 0;
    if (index >= offset) found.set(m[1], index - offset);
  }
  return found;
}

/**
 * Split a parameter list on the commas that separate parameters.
 *
 * @param {string} params  Everything between the parentheses of a `def`.
 * @returns {string[]}
 *
 * >>> splitParams("a: dict[str, int], b: McFunction")
 * [ 'a: dict[str, int]', ' b: McFunction' ]
 */
function splitParams(params) {
  const parts = [];
  let depth = 0;
  let start = 0;
  for (let i = 0; i < params.length; i++) {
    const c = params[i];
    if (c === "[" || c === "{" || c === "(") depth++;
    else if (c === "]" || c === "}" || c === ")") depth--;
    else if (c === "," && depth === 0) { parts.push(params.slice(start, i)); start = i + 1; }
  }
  parts.push(params.slice(start));
  return parts;
}

/**
 * The name of a whole argument, when the argument is exactly one identifier.
 *
 * `write_function(path, content)` hands the commands over in a variable, which is how a third
 * of a real project's blocks are written. Anything else, a call or an expression, is not a
 * name we could find an assignment for, so it returns null.
 *
 * @param {string} text
 * @param {number} i  First character of the argument, whitespace included.
 * @returns {string | null}
 */
function readArgumentName(text, i) {
  while (i < text.length && /[ \t\r\n]/.test(text[i])) i++;
  const start = i;
  while (i < text.length && /[A-Za-z0-9_]/.test(text[i])) i++;
  if (i === start || /[0-9]/.test(text[start])) return null;

  let after = i;
  while (after < text.length && /[ \t\r\n]/.test(text[after])) after++;
  return text[after] === ")" || text[after] === "," ? text.slice(start, i) : null;
}

/** An assignment to a bare name, with an optional type annotation, `=` or `+=`. */
const ASSIGN_RE = /(?:^|\n)[ \t]*([A-Za-z_]\w*)[ \t]*(?::[^=\n]*)?\+?=[ \t]*/g;

/**
 * The string literals assigned to any of `names`, as blocks.
 *
 * Both `content = """..."""` and a later `content += """..."""` count, since building a
 * function by appending is as common as writing it in one go.
 *
 * @param {string} text
 * @param {Map<string, number>} names  Name to the offset of the write_* call that consumes it.
 * @returns {{ start:number, end:number, contentStart:number, contentEnd:number, callStart:number }[]}
 */
function findAssignedBlocks(text, names) {
  const blocks = [];

  ASSIGN_RE.lastIndex = 0;
  let m;
  while ((m = ASSIGN_RE.exec(text)) !== null) {
    if (!names.has(m[1])) continue;

    const opening = readOpeningQuote(text, m.index + m[0].length);
    if (!opening) continue;
    const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart, opening.isFString);
    if (closeIdx === -1) continue;

    blocks.push({
      start: opening.quoteStart, end: closeIdx + opening.quoteStyle.length,
      contentStart: opening.contentStart, contentEnd: closeIdx,
      callStart: /** @type {number} */ (names.get(m[1])),
    });
    ASSIGN_RE.lastIndex = closeIdx + opening.quoteStyle.length;
  }

  return blocks;
}

/**
 * Find the `{...}` interpolation spans inside one block, braces included.
 * Those spans hold Python, not mcfunction, so a consumer projecting the block
 * into an mcfunction document must mask them.
 * Returns [] for a non-f-string block, which has no interpolations by definition.
 * @param {string} text
 * @param {{ start:number, end:number }} block  One entry from findBlockOffsets.
 * @returns {{ start:number, end:number }[]}  Sorted, non-overlapping.
 */
function findInterpolationSpans(text, block) {
  const opening = readOpeningQuote(text, block.start);
  if (!opening || !opening.isFString) return [];

  const spans = [];
  const contentEnd = block.end - opening.quoteStyle.length;
  let i = opening.contentStart;

  while (i < contentEnd) {
    const c = text[i];
    if (c === "\\") { i += 2; continue; }
    if (c !== "{") { i++; continue; }
    if (text[i + 1] === "{") { i += 2; continue; } // literal {{
    const after = skipInterpolation(text, i + 1);
    if (after === -1) break;
    spans.push({ start: i, end: Math.min(after, contentEnd) });
    i = after;
  }

  return spans;
}

module.exports = {
  FUNC_RE,
  FUNCS_2ND_ARG,
  stringPrefixAt,
  findClosingQuote,
  skipInterpolation,
  skipFirstArg,
  readOpeningQuote,
  findBlockOffsets,
  readArgumentName,
  findAssignedBlocks,
  findInterpolationSpans,
};
