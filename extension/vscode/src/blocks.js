// @ts-check
"use strict";

// Pure text-scanning logic for locating mcfunction string blocks inside
// StewBeet write_* calls. Kept free of any "vscode" dependency so it can be
// unit-tested with plain Node (see test/blocks.test.js).

// ─── Constants──────────────

const FUNC_RE = /\b(write_function|write_versioned_function|write_scheduled_function|write_load_file|write_unload_file|write_tick_file)\s*\(/g;

/** Functions where the mcfunction content is the 2nd argument (after a path). */
const FUNCS_2ND_ARG = new Set([
  "write_function",
  "write_versioned_function",
  "write_scheduled_function",
]);

// ─── String scanning────────

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

// ─── Block detection────────

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
 * @returns {{ start:number, end:number }[]}  Offsets of each block: start is
 *   the opening quote (including prefix), end is just after the closing quote.
 */
function findBlockOffsets(text) {
  const blocks = [];

  FUNC_RE.lastIndex = 0;
  let m;
  while ((m = FUNC_RE.exec(text)) !== null) {
    const afterOpen = m.index + m[0].length;

    let contentIdx;
    if (FUNCS_2ND_ARG.has(m[1])) {
      contentIdx = skipFirstArg(text, afterOpen);
      if (contentIdx === -1) continue;
    } else {
      contentIdx = afterOpen;
    }

    const opening = readOpeningQuote(text, contentIdx);
    if (!opening) continue;

    const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart, opening.isFString);
    if (closeIdx === -1) continue;

    blocks.push({ start: opening.quoteStart, end: closeIdx + opening.quoteStyle.length });
  }

  return blocks;
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
};
