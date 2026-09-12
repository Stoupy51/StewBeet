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

/** beet's own way of writing a function: `... [path] = Function(<content>)`.
 *
 * The subscript before `=` is what makes this safe to claim. `Function` alone is a beet class
 * whose name is common enough to appear in unrelated Python, while a subscripted assignment of
 * one is a datapack function and nothing else. All three spellings land here, since
 * `ctx.data.functions[p]`, `ctx.data["ns"].functions[p]` and `ctx.data[Function][p]` differ only
 * in what precedes the subscript. */
const ASSIGN_FUNCTION_RE = /(?:\.functions|\[\s*Function\s*\])\s*\[[^\]\n]*\]\s*=\s*Function\s*\(/g;

/** An append onto a function already in the pack, ex: `ctx.data.functions[p].append("say hi")`.
 *
 * `.lines` is the list of commands behind a `Function`, so `.lines.append(...)` and
 * `.lines.extend([...])` write the same content one level down. A `Function` has no `extend` of
 * its own, and claiming one would colour an `AttributeError` as if it were a command. */
const APPEND_FUNCTION_RE =
  /(?:\.functions|\[\s*Function\s*\])\s*\[[^\]\n]*\]\s*\.\s*(?:append|prepend|lines\s*\.\s*(?:append|extend))\s*\(/g;

/** An append through a StewBeet resource's own beet file, ex:
 *  `Block.from_id("x").functions.place_secondary.obj.append("say hi")`.
 *  `.obj` is the beet object behind a resource, so what follows reaches beet with no helper in
 *  between, which is why the Python side records it and this side has to see it too. */
const APPEND_OBJ_RE = /\.\s*obj\s*\.\s*(?:append|prepend|lines\s*\.\s*(?:append|extend))\s*\(/g;

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
  /** Names handed to a write_* call instead of a literal, to the offsets of the calls taking them.
   *  A name is often reused, `content` above all, so each of its blocks belongs to the call after it rather than to the first one seen. */
  const variables = new Map();
  /** @param {string} name @param {number} offset */
  const consume = name => variables.set(name, [...(variables.get(name) ?? []), m.index]);
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
      if (name) consume(name);
      continue;
    }

    const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart, opening.isFString);
    if (closeIdx === -1) continue;

    // `"\n".join(lines)` hands the commands over in `lines`, and the literal separating them holds no command of its own.
    // Reading it as one both decorates a `"\n"` and hides every line the list was built from, which is all of a loop-written function.
    const joined = readJoinArgument(text, closeIdx + opening.quoteStyle.length);
    if (joined !== null) {
      if ("name" in joined) consume(joined.name);
      else for (const entry of joined.entries) blocks.push({ ...entry, callStart: m.index });
      continue;
    }

    blocks.push({
      start: opening.quoteStart, end: closeIdx + opening.quoteStyle.length,
      contentStart: opening.contentStart, contentEnd: closeIdx, callStart: m.index,
    });
  }

  blocks.push(...findBeetWrites(text));
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
 * Find every block beet's own writers open, with no StewBeet helper involved.
 *
 * `ctx.data.functions[p] = Function("say hi")` is how a plain beet plugin writes a function, and
 * how a StewBeet one does when it wants the object rather than the helper. Both a string and the
 * entries of a list literal count, since `Function(["say a", "say b"])` is the same content
 * spelled differently.
 *
 * @param {string} text
 * @returns {{ start:number, end:number, contentStart:number, contentEnd:number, callStart:number }[]}
 */
function findBeetWrites(text) {
  const blocks = [];

  for (const pattern of [ASSIGN_FUNCTION_RE, APPEND_FUNCTION_RE, APPEND_OBJ_RE]) {
    pattern.lastIndex = 0;
    let m;
    while ((m = pattern.exec(text)) !== null) {
      const callStart = m.index;
      let at = m.index + m[0].length;

      // A list literal holds one block per entry; anything else holds at most one.
      const list = text[at] === "[";
      if (list) at++;

      for (;;) {
        while (at < text.length && (text[at] === " " || text[at] === "\t" || text[at] === "\n"
          || text[at] === "\r" || text[at] === ",")) at++;

        const opening = readOpeningQuote(text, at);
        if (!opening) break;
        const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart, opening.isFString);
        if (closeIdx === -1) break;

        blocks.push({
          start: opening.quoteStart, end: closeIdx + opening.quoteStyle.length,
          contentStart: opening.contentStart, contentEnd: closeIdx, callStart,
        });
        at = closeIdx + opening.quoteStyle.length;
        if (!list) break;
      }
    }
  }
  return blocks;
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

/**
 * What a string literal is separating, when it is the separator of a `.join(...)`.
 *
 * `write_function(path, "\n".join(lines))` is how a function built one command at a time is written, and the commands are in `lines`.
 * A generator is the other half of the idiom, `"\n".join(f"say {i}" for i in items)`, where the element is the command.
 *
 * @param {string} text
 * @param {number} i  Just past the closing quote of the literal.
 * @returns {{ name: string } | { entries: { start:number, end:number, contentStart:number, contentEnd:number }[] } | null}
 *   The name joined, the commands joined, or null when this is not a `.join(` at all.
 */
function readJoinArgument(text, i) {
  const match = /^\.[ \t]*join[ \t]*\(/.exec(text.slice(skipSpace(text, i), skipSpace(text, i) + 16));
  if (!match) return null;

  const inner = skipSpace(text, skipSpace(text, i) + match[0].length);
  const name = readArgumentName(text, inner);
  if (name) return { name };
  return { entries: text[inner] === "[" ? readListEntries(text, inner) : literalAt(text, inner) };
}

/**
 * Every string literal directly inside a list literal, as its own block.
 *
 * `lines: list[McFunction] = ["say a", "say b"]` is one command per entry, which is what the grammar already colours them as.
 * `[f"say {i}" for i in items]` is one command evaluated per item, and what comes after the `for` is plumbing rather than element, so `if name == "abc"` contributes nothing.
 *
 * @param {string} text
 * @param {number} open  Index of the `[`.
 * @returns {{ start:number, end:number, contentStart:number, contentEnd:number }[]}
 */
function readListEntries(text, open) {
  const entries = [];
  let i = open + 1;
  let depth = 0;

  while (i < text.length) {
    const c = text[i];
    if (c === "(" || c === "[" || c === "{") { depth++; i++; continue; }
    if (c === ")" || c === "}") { depth--; i++; continue; }
    if (c === "]") {
      if (depth === 0) break;
      depth--; i++; continue;
    }
    if (depth === 0 && /^for\b/.test(text.slice(i, i + 4)) && !/\w/.test(text[i - 1] ?? "")) break;
    if (c !== '"' && c !== "'") { i++; continue; }

    const opening = readOpeningQuote(text, i - stringPrefixAt(text, i).length);
    if (!opening) { i++; continue; }
    const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart, opening.isFString);
    if (closeIdx === -1) break;
    const after = closeIdx + opening.quoteStyle.length;

    // A nested entry is part of an expression rather than a command of its own.
    // So is a literal something is called on: `", ".join(parts)` is a separator, not a command.
    if (depth === 0 && text[skipSpace(text, after)] !== ".") {
      entries.push({
        start: opening.quoteStart, end: after,
        contentStart: opening.contentStart, contentEnd: closeIdx,
      });
    }
    i = after;
  }

  return entries;
}

/** The next index at or after `i` that is not whitespace. @param {string} text @param {number} i */
function skipSpace(text, i) {
  while (i < text.length && /[ \t\r\n]/.test(text[i])) i++;
  return i;
}

/** A line adding to a name: an assignment, an `+=`, or an `.append(...)` onto a list. */
const CONTRIBUTION_RE = /(?:^|\n)[ \t]*([A-Za-z_]\w*)[ \t]*(?:(?::[^=\n]*)?\+?=|\.[ \t]*append[ \t]*\()[ \t]*/g;

/**
 * The commands added to any of `names`, as blocks.
 *
 * A function assembled in a variable is written in every shape Python offers: assigned whole, grown with `+=`, appended to a line at a time, or listed.
 * All four count, and all four feed the call that later consumes the name.
 *
 * @param {string} text
 * @param {Map<string, number[]>} names  Name to the offsets of the write_* calls consuming it.
 * @returns {{ start:number, end:number, contentStart:number, contentEnd:number, callStart:number }[]}
 */
function findAssignedBlocks(text, names) {
  const blocks = [];

  CONTRIBUTION_RE.lastIndex = 0;
  let m;
  while ((m = CONTRIBUTION_RE.exec(text)) !== null) {
    const calls = names.get(m[1]);
    if (!calls) continue;

    const value = m.index + m[0].length;
    const found = text[value] === "[" ? readListEntries(text, value) : literalAt(text, value);
    if (found.length === 0) continue;

    // The call a name reaches is the first one after these commands.
    // A name reused later in the file, `content` above all, is a different function every time.
    const last = found[found.length - 1].end;
    const callStart = calls.find(offset => offset > last) ?? calls[calls.length - 1];
    for (const entry of found) blocks.push({ ...entry, callStart });
    CONTRIBUTION_RE.lastIndex = last;
  }

  return blocks;
}

/**
 * The string literal at `i`, as a one-element array, or an empty one when there is none.
 * @param {string} text
 * @param {number} i
 */
function literalAt(text, i) {
  const opening = readOpeningQuote(text, i);
  if (!opening) return [];
  const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart, opening.isFString);
  if (closeIdx === -1) return [];
  return [{
    start: opening.quoteStart, end: closeIdx + opening.quoteStyle.length,
    contentStart: opening.contentStart, contentEnd: closeIdx,
  }];
}

/**
 * Offsets of the redundant brace in every `{{` and `}}` escape inside one block.
 *
 * An f-string writes a literal brace by doubling it, so `{{"Slot":0b}}` is the NBT `{"Slot":0b}`
 * and a datapack parser handed the doubled form reports a missing key. Blanking one brace of each
 * pair leaves `{ "Slot":0b }`, which is the same compound and the same number of characters, so
 * the projection stays offset for offset with the Python.
 *
 * The opening pair blanks its second brace and the closing pair its first, which keeps each
 * remaining brace where the command's own brace really is.
 *
 * Returns [] for a non-f-string block, where `{{` is genuinely two braces.
 * @param {string} text
 * @param {{ start:number, end:number }} block  One entry from findBlockOffsets.
 * @returns {number[]}  Sorted offsets, each of one character to blank.
 */
function findEscapedBraces(text, block) {
  const opening = readOpeningQuote(text, block.start);
  if (!opening || !opening.isFString) return [];

  const found = [];
  const contentEnd = block.end - opening.quoteStyle.length;
  let i = opening.contentStart;

  while (i < contentEnd - 1) {
    const c = text[i];
    if (c === "\\") { i += 2; continue; }
    if (c === "{" && text[i + 1] === "{") { found.push(i + 1); i += 2; continue; }
    if (c === "}" && text[i + 1] === "}") { found.push(i); i += 2; continue; }
    if (c === "{") {
      // A real interpolation, whose Python may hold braces of its own.
      const after = skipInterpolation(text, i + 1);
      if (after === -1) break;
      i = after;
      continue;
    }
    i++;
  }
  return found;
}

/** Escapes standing for the character behind the backslash, so only the backslash is spelling. */
const LITERAL_ESCAPES = new Set(["\\", '"', "'"]);

/** Hex digits following the letter of each numeric escape, so the whole run is blanked together. */
const NUMERIC_ESCAPES = { x: 2, u: 4, U: 8 };

/**
 * Offsets of every character of every escape sequence inside one block that spells something
 * other than itself.
 *
 * `write_function(path, "\n")` writes an empty function, and a parser handed the two characters
 * the author typed is told, correctly, that `\n` is not a command. A string holding several
 * commands is the same thing at greater length: the escape is the line break, and the projection
 * keeps one Python line to one virtual line, so the break cannot be projected as one.
 *
 * `\\` and `\"` keep the character they stand for and blank only the backslash, the way a doubled
 * brace keeps one brace.
 *
 * Returns [] for a raw string, where a backslash is a backslash.
 * @param {string} text
 * @param {{ start:number, end:number }} block  One entry from findBlockOffsets.
 * @returns {number[]}  Sorted offsets, each of one character to blank.
 */
function findEscapes(text, block) {
  const opening = readOpeningQuote(text, block.start);
  if (!opening) return [];
  if (/[rR]/.test(text.slice(block.start, opening.contentStart))) return [];

  const found = [];
  const contentEnd = block.end - opening.quoteStyle.length;
  let i = opening.contentStart;

  while (i < contentEnd - 1) {
    if (opening.isFString && text[i] === "{") {
      if (text[i + 1] === "{") { i += 2; continue; }
      // An interpolation holds Python, which the mask covers already.
      const after = skipInterpolation(text, i + 1);
      if (after === -1) break;
      i = after;
      continue;
    }
    if (text[i] !== "\\") { i++; continue; }

    found.push(i);
    const digits = NUMERIC_ESCAPES[text[i + 1]] ?? 0;
    if (!LITERAL_ESCAPES.has(text[i + 1])) {
      for (let k = 1; k <= 1 + digits && i + k < contentEnd; k++) found.push(i + k);
    }
    i += 2 + digits;
  }
  return found;
}

/**
 * Every offset of one block whose character is Python spelling rather than a command character.
 *
 * The doubled brace of an f-string and an escape sequence are the two of them, and a consumer
 * blanking both hands the parser the command the author wrote at the columns they wrote it in.
 * @param {string} text
 * @param {{ start:number, end:number }} block  One entry from findBlockOffsets.
 * @returns {number[]}  Sorted offsets, each of one character to blank.
 */
function findBlankedOffsets(text, block) {
  return [...findEscapedBraces(text, block), ...findEscapes(text, block)].sort((a, b) => a - b);
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
  findBeetWrites,
  readArgumentName,
  findAssignedBlocks,
  findInterpolationSpans,
  findEscapedBraces,
  findEscapes,
  findBlankedOffsets,
};
