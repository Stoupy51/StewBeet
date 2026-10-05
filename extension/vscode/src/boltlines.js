// @ts-check
"use strict";

// What a datapack parser should see of a bolt file.
//
// The same trick ./projection.js plays on a Python string, played on a whole file: every line
// that is not a command becomes empty, and what is left reaches Spyglass as a plain .mcfunction
// whose lines are in lockstep with the source. That is what buys back the completion, the live
// diagnostics and the ctrl+click a `.bolt` file loses by not being `mcfunction`.
//
// The classifier is mostly not written here. Both command regexes are read out of the bolt
// grammar this extension ships, so a line coloured as a command is a line projected as one, and
// regenerating the grammar from mecha's command tree updates both at once. The one rule of our
// own is for a word one letter away from a command: `playound` earns its squiggle only by
// reaching the parser.
//
// Deliberately free of any "vscode" dependency, so it is testable under plain `node --test`.

const fs = require("fs");
const path = require("path");
const { MASK, substitute } = require("./projection");

// The grammar's own rules

/** @type {{ repository: Record<string, { begin: string }> }} */
const GRAMMAR = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "syntaxes", "bolt.tmLanguage.json"), "utf8"));

/** A line whose first word is one of mecha's root commands. Capture 1 is its indentation. */
const COMMAND_LINE = new RegExp(GRAMMAR.repository["command-statement"].begin);

/** Every word that opens a command, read off the alternation the rule above is built from. */
const COMMANDS = (/\(([a-z0-9|_-]+)\)/.exec(COMMAND_LINE.source)?.[1] ?? "").split("|");

/** `function <path>:` and its append, prepend and merge forms. Capture 1 is the indentation. */
const NESTING_LINE = new RegExp(GRAMMAR.repository["nesting-statement"].begin);

/** A macro line. Python starts no statement with `$`, so the whole line is the command's. */
const MACRO_LINE = /^([ \t]*)\$(?=\S)/;

/** A command being typed, which no rule above matches yet and completion is most wanted on.
 *  A lone lowercase word is not a statement Python has any use for, `pass` and its siblings
 *  aside, and it is what every command looks like three keystrokes in. */
const TYPING_COMMAND = /^([ \t]*)([a-z][a-z0-9_-]*)[ \t]*$/;

/** The first word of a line and whatever follows it. */
const FIRST_WORD = /^([ \t]*)([a-z][a-z0-9_]*)[ \t]+(\S.*)$/;

/** How Python carries on after a name, where a command never would: an assignment of any kind,
 *  a call, a subscript, an annotation. A lone `-` is left out of it, since `-5` after a word is
 *  a coordinate far more often than a subtraction nobody uses the result of. */
const PYTHON_CONTINUES = /^(?:[.,;:()[\]{}]|[-+*/%&|^@<>!]{0,2}=)/;

/** Python's own infix words, so `machine in MACHINES` is no command called `machine`. */
const PYTHON_INFIX = /^(?:if|else|for|in|is|and|or|not)\b/;

/** The words that open a line inside an `execute:` block, which is where a command's own
 *  subcommands are written one per line. `rotated` and `on` are each one letter from a command
 *  of their own, and neither is ever a misspelling of it. */
const EXECUTE_SUBCOMMANDS = new Set([
  "align", "anchored", "as", "at", "facing", "if", "in", "on", "positioned", "rotated", "run",
  "store", "summon", "unless",
]);

/** Words Python owns at the start of a statement, so none of them opens a command. `return` is
 *  one of them: mecha's grammar leaves that word to Python and lists no command under it. */
const PYTHON_STATEMENTS = new Set([
  "and", "as", "assert", "async", "await", "break", "case", "class", "continue", "def", "del",
  "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is",
  "lambda", "match", "nonlocal", "not", "or", "pass", "raise", "return", "try", "type", "while",
  "with", "yield",
]);

// Python inside a command

/** A string with a Python prefix, ex: `f"{self.path}/open"`. mcfunction has no string prefixes,
 *  so the prefix is what tells one from the quoted arguments a command really does take. */
const PREFIXED_STRING = /[fFrRbBuU]{1,2}(?:"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/y;

/** A call, ex: `has_item_predicate(self.item)`. Nothing in mcfunction puts a bare `(` after a word.
 *  A space before the parenthesis makes the word an argument of its own, as `float` is in `compute bolt float (1+1)`. */
const PYTHON_CALL = /[A-Za-z_]\w*\(/y;

/** What Python may not follow. `@s (-self.item)` is a selector and a bolt expression rather than a
 *  call named `s`, and `$(x)` is a macro placeholder rather than either. */
const NOT_A_NAME = /[\w@#$~^]/;

/** A quoted argument of a command, copied through so a `(` inside it is not read as a call. */
const QUOTED = /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/y;

/** The argument of `function`, when it is a dotted name rather than a resource location.
 *  `function gui.open` is the one place bolt users write a bare Python expression where a
 *  path belongs, and a path with a dot and no namespace is nothing a datapack can name. */
const FUNCTION_ATTRIBUTE = /\bfunction[ \t]+([A-Za-z_]\w*(?:\.\w+)+)(?![\w./:-])/g;

/** A resource location relative to the function being written, which mecha resolves and a
 *  datapack parser rejects: `~/` and `./` name a child of the current function, `../` a sibling.
 *  A coordinate is never followed by a slash, so `~ ~1 ~` stays a position. */
const RELATIVE_LOCATION = /(?<![^\s=,])(?:~|\.\.?)\/[\w./-]*/g;

/** How many virtual documents one bolt file is worth.
 *  One per run of commands means a keystroke reparses the run it lands in rather than the file.
 *  Past this many, runs are merged: each document is a round trip of its own on every keepalive
 *  pass, and a file of scattered one-line runs would spend more time waking than parsing. */
const MAX_BLOCKS = 8;

// Reading a file

/**
 * Every line a datapack parser is meant to read, by 0-based line number.
 *
 * The lines of a docstring are skipped whatever they say. Prose is where a line most easily
 * opens with a command word by accident, since `list the machines it knows about` has exactly
 * the shape of a command and the quotes around it are all that say it is not one.
 *
 * A line the build compiled into a command is one, whatever its first word: the root commands of
 * a newer Minecraft version and the ones a plugin adds to mecha are in no list here.
 *
 * A command goes on over the lines mecha's own rule continues it on: while a bracket it opened is
 * still open, and, in mecha's `multiline` mode, over every line indented deeper than its first,
 * unless that first line opened a block. `continues` marks every line but the last of one.
 *
 * @param {string} text
 * @param {Set<number>} [compiled]  0-based lines the last build compiled a command from.
 * @returns {Map<number, KeptLine>}
 */
function commandsOf(text, compiled = new Set()) {
  /** @type {Map<number, KeptLine>} */
  const commands = new Map();
  /** @type {string | null} */
  let inside = null;
  /** The command the previous line belongs to, while the next line may still continue it. @type {{ indent:number, depth:number } | null} */
  let open = null;

  text.split("\n").forEach((raw, line) => {
    const body = raw.endsWith("\r") ? raw.slice(0, -1) : raw;
    const prose = inside !== null;
    inside = tripleQuoteAfter(body, inside);
    if (prose) return;

    const indent = body.length - body.trimStart().length;
    if (open && body.trim() && (open.depth > 0 || indent > open.indent)) {
      /** @type {KeptLine} */ (commands.get(line - 1)).continues = true;
      commands.set(line, command(indent, body));
      open = stillOpen(open.indent, open.depth, body);
      return;
    }

    const kept = keptPart(body) ?? (compiled.has(line) && body.trim() ? command(indent, body) : null);
    if (kept) commands.set(line, kept);
    open = kept && !kept.partial ? stillOpen(indent, 0, body) : null;
  });
  return commands;
}

/** @typedef {{ start:number, text:string, partial:boolean, continues?:boolean }} KeptLine */

/**
 * What a command still has open at the end of one of its lines, or null when the next line cannot continue it.
 * A line ending in a colon at depth 0 opens a block, whose body is commands of its own.
 * @param {number} indent  Indentation of the command's first line.
 * @param {number} depth  Brackets open before this line.
 * @param {string} body  The line.
 */
function stillOpen(indent, depth, body) {
  const after = depth + bracketBalance(body);
  return after <= 0 && /:[ \t]*$/.test(body) ? null : { indent, depth: Math.max(0, after) };
}

/** Brackets a line opens minus those it closes, quoted text aside. @param {string} body */
function bracketBalance(body) {
  let balance = 0;
  for (let at = 0; at < body.length; at++) {
    const quoted = readAt(QUOTED, body, at);
    if (quoted) { at += quoted.length - 1; continue; }
    if ("([{".includes(body[at])) balance++;
    else if (")]}".includes(body[at])) balance--;
  }
  return balance;
}

/**
 * Which triple quote is still open at the end of a line, or null when none is.
 * @param {string} body  One line, without its newline.
 * @param {string | null} inside  The delimiter open when the line started.
 * @returns {string | null}
 */
function tripleQuoteAfter(body, inside) {
  let at = 0;
  while (at < body.length) {
    if (inside) {
      if (body.startsWith(inside, at)) { inside = null; at += 3; continue; }
      at += 1;
      continue;
    }
    const char = body[at];
    if (char === "#") return null;
    if (char !== '"' && char !== "'") { at += 1; continue; }

    const triple = char.repeat(3);
    if (body.startsWith(triple, at)) { inside = triple; at += 3; continue; }
    const quoted = readAt(QUOTED, body, at);
    at += quoted ? quoted.length : 1;
  }
  return inside;
}

/**
 * The runs of consecutive command lines, which are the blocks a bolt file is served as.
 * @param {Map<number, unknown>} commands  From commandsOf.
 * @returns {{ from:number, to:number }[]}  0-based line ranges, inclusive, in order.
 */
function commandBlocks(commands) {
  /** @type {{ from:number, to:number }[]} */
  const runs = [];
  for (const line of [...commands.keys()].sort((a, b) => a - b)) {
    const last = runs[runs.length - 1];
    if (last && line === last.to + 1) last.to = line;
    else runs.push({ from: line, to: line });
  }
  if (runs.length <= MAX_BLOCKS) return runs;

  const per = Math.ceil(runs.length / MAX_BLOCKS);
  return Array.from({ length: Math.ceil(runs.length / per) }, (_, group) => ({
    from: runs[group * per].from,
    to: runs[Math.min((group + 1) * per, runs.length) - 1].to,
  }));
}

// Projection

/**
 * Project a bolt file into the mcfunction document Spyglass should see.
 *
 * Every line keeps its number, a line outside the range is empty, and a kept line loses its
 * indentation: the virtual document is a flat list of commands, which is what a `.mcfunction`
 * is, and the table gives every column back. A command spread over several lines ends each but
 * its last with ` \`, the line continuation a datapack parser knows since 1.20.2.
 *
 * @param {string} text
 * @param {object} [options]
 * @param {Map<number, KeptLine> | null} [options.commands]  From commandsOf, when it is already known.
 * @param {number} [options.from]  First line of the block, 0-based.
 * @param {number} [options.to]  Last line of the block, inclusive.
 * @param {Map<number, string> | null} [options.generated]  What the build wrote per line.
 * @param {Map<number, { text: string, points: { generated: number, column: number }[] }> | null} [options.columns]
 *   Per line, the generated line and its columns that are positions on this line, see `compiledColumns`.
 * @param {Map<number, number>} [options.opaque]  Per line, the column where syntax no vanilla parser knows begins.
 * @returns {{ text: string, table: Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>, masked: Map<number, { start:number, end:number }[]> }}
 */
function projectBolt(text, { commands = null, from = 0, to = Number.MAX_SAFE_INTEGER, generated = null, columns = null, opaque = new Map() } = {}) {
  const found = commands ?? commandsOf(text);
  /** @type {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} */
  const table = new Map();
  /** @type {Map<number, { start:number, end:number }[]>} */
  const masked = new Map();
  /** Parentheses of a Python expression still open from the line before. */
  let python = 0;
  /** Whether the command this line continues has reached syntax no vanilla parser knows. */
  let unknown = false;

  const projected = text.split("\n").map((raw, line) => {
    const kept = line < from || line > to ? undefined : found.get(line);
    const continued = found.get(line - 1)?.continues ?? false;
    if (!continued) { python = 0; unknown = false; }
    if (!kept) return "";

    const cut = Math.max(0, unknown ? 0 : (opaque.get(line) ?? Infinity) - kept.start);
    const { text: command, runs, open } = maskPython(kept.text, { python, from: cut });
    python = open;
    unknown = unknown || cut < kept.text.length;
    // What follows the cut is the plugin's syntax, which stays a mask: its compiled form is mecha's output, not the author's text.
    const resolvable = runs.filter(run => run.end < cut);
    const exact = exactValues(columns?.get(line), resolvable, kept.start);
    const resolved = substitute(command, generated?.get(line), resolvable, runs, line, table, masked, null, exact);
    dedent(table, line, kept.start);
    // A word still being typed is our guess at a command, so what a parser says about it is
    // about the guess. The author has not finished writing the line they meant.
    if (kept.partial) masked.set(line, [{ start: 0, end: resolved.length }]);
    return kept.continues ? `${resolved} \\` : resolved;
  });

  return { text: projected.join("\n"), table, masked };
}

/**
 * The value the build gave each masked run whose two ends are both the end of an AST node.
 *
 * mecha keeps the position of every node through bolt's evaluation, so `int(major)` between two
 * points of the source is `1` between the same two points of the generated line, whatever mecha
 * did to the text around it. A run whose ends are not both points is left to the text alignment.
 *
 * @param {{ text: string, points: { generated: number, column: number }[] } | undefined} compiled
 * @param {{ start:number, end:number }[]} runs  Masked runs, in the columns of the kept text.
 * @param {number} offset  Column of the source line the kept text starts at.
 * @returns {Map<number, string>}  Run start to value.
 */
function exactValues(compiled, runs, offset) {
  /** @type {Map<number, string>} */
  const values = new Map();
  if (!compiled) return values;
  for (const run of runs) {
    const starts = compiled.points.filter(point => point.column === run.start + offset).map(point => point.generated);
    const ends = compiled.points.filter(point => point.column === run.end + offset).map(point => point.generated);
    if (starts.length === 0 || ends.length === 0) continue;
    const from = Math.min(...starts);
    const until = Math.max(...ends);
    if (until > from) values.set(run.start, compiled.text.slice(from, until));
  }
  return values;
}

/**
 * Give a line's spans back the columns its indentation holds, and record the indentation itself.
 * The virtual line starts at column 0 and the source line does not, which is one substitution
 * like any other: `pythonWidth` columns of source became none.
 * @param {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} table
 * @param {number} line
 * @param {number} indent
 */
function dedent(table, line, indent) {
  const spans = (table.get(line) ?? []).map(span => ({ ...span, start: span.start + indent }));
  if (indent > 0) spans.unshift({ start: 0, pythonWidth: indent, virtualWidth: 0 });
  if (spans.length > 0) table.set(line, spans);
}

/**
 * The part of one line a datapack parser is meant to read, or null when the line is Python.
 *
 * A nesting statement keeps its `function <path>` and loses the `append` in front and the `:`
 * behind, both of which are mecha's own syntax rather than a command's.
 *
 * @param {string} line  One line, without its newline.
 * @returns {{ start: number, text: string, partial: boolean } | null}  `start` is the column the text was taken from.
 */
function keptPart(line) {
  const macro = MACRO_LINE.exec(line);
  if (macro) return command(macro[1].length, line);

  const nesting = NESTING_LINE.exec(line);
  if (nesting) return command(nesting[0].length - "function".length, line);

  const found = COMMAND_LINE.exec(line);
  if (found) return command(found[1].length, line);

  const typing = TYPING_COMMAND.exec(line);
  if (typing && !PYTHON_STATEMENTS.has(typing[2])) {
    return { start: typing[1].length, text: typing[2], partial: true };
  }
  return misspelledCommand(line);
}

/**
 * A line whose first word is one letter away from a command, read as the command it was meant to be.
 *
 * `playound minecraft:block.barrel.open` is a typo, and the only thing that says so out loud is
 * a datapack parser being shown the line. One letter is the whole licence: a bolt file is full
 * of words that open a line and are not commands, from `raw` and `append` to a project's own
 * `damage_type` or `duels_map`, and every one of them would be reported as an unknown command
 * if the rule were "anything Python cannot compile". None of them is a typo of a command.
 *
 * @param {string} line
 * @returns {{ start: number, text: string, partial: boolean } | null}
 */
function misspelledCommand(line) {
  const guess = FIRST_WORD.exec(line);
  if (!guess || PYTHON_STATEMENTS.has(guess[2]) || EXECUTE_SUBCOMMANDS.has(guess[2])) return null;
  if (PYTHON_CONTINUES.test(guess[3]) || PYTHON_INFIX.test(guess[3])) return null;
  return COMMANDS.some(known => withinOneEdit(guess[2], known)) ? command(guess[1].length, line) : null;
}

/**
 * Whether one word becomes the other by adding, dropping, changing or swapping one letter.
 * Swapping is in because that is what a typo mostly is: `tellraw` is one Levenshtein edit from
 * nothing at all when the `a` and the `w` change places.
 * @param {string} word @param {string} other
 */
function withinOneEdit(word, other) {
  if (Math.abs(word.length - other.length) > 1) return false;

  let at = 0;
  let to = 0;
  let edits = 0;
  while (at < word.length && to < other.length) {
    if (word[at] === other[to]) { at++; to++; continue; }
    if (++edits > 1) return false;
    if (word.length > other.length) at++;
    else if (word.length < other.length) to++;
    else if (word[at] === other[to + 1] && word[at + 1] === other[to]) { at += 2; to += 2; }
    else { at++; to++; }
  }
  return edits + (word.length - at) + (other.length - to) <= 1;
}

/** One kept command, taken from the column it starts at. @param {number} start @param {string} line */
function command(start, line) {
  return { start, text: withoutBlockColon(line.slice(start)), partial: false };
}

/** A nested command opens a block with a trailing colon, which is not part of the command.
 *  @param {string} text */
function withoutBlockColon(text) {
  const nested = /:[ \t]*$/.exec(text);
  return nested ? text.slice(0, nested.index) : text.trimEnd();
}

/**
 * Mask the Python a command line carries, so the rest of the line still parses.
 *
 * `execute if predicate has_item_predicate(self.item) run ...` is a command with a Python call
 * where a predicate id belongs. Masking the call leaves a run of `_`, which is a legal id, so
 * everything after it is read as the command it is. What the build resolved each run to is
 * spliced back in by ./projection.js, which is what makes a masked path clickable.
 *
 * A parenthesis left open goes on over the lines that continue the command, which is how a bolt
 * expression spans lines: `python` says how many the line starts inside, and `open` how many it
 * leaves open. Everything from `from` on is masked whatever it holds.
 *
 * @param {string} line
 * @param {{ python?: number, from?: number }} [options]
 * @returns {{ text: string, runs: { start:number, end:number }[], open: number }}
 */
function maskPython(line, { python = 0, from = Infinity } = {}) {
  let out = "";
  /** @type {{ start:number, end:number }[]} */
  const runs = [];
  const paths = pathExpressions(line);
  const stop = Math.min(from, line.length);
  /** @param {number} start @param {number} end */
  const mask = (start, end) => { out += MASK.repeat(end - start); runs.push({ start, end }); };

  let { end: at, open } = python > 0 ? closingParen(line, 0, python) : { end: 0, open: 0 };
  if (at > 0) mask(0, Math.min(at, stop));
  while (at < stop) {
    const path = paths.get(at);
    const expression = path === undefined ? joinedExpression(line, at) : { end: path, open: 0 };
    if (!expression) {
      const quoted = readAt(QUOTED, line, at);
      out += quoted ?? line[at];
      at += quoted ? quoted.length : 1;
      continue;
    }
    mask(at, Math.min(expression.end, stop));
    ({ end: at, open } = expression);
  }
  // What `from` cuts off, which may begin inside an expression already masked.
  if (stop < line.length) mask(out.length, line.length);
  return { text: out, runs, open };
}

/** Where each `function <name>.<attribute>` argument and each relative location starts and ends.
 *  @param {string} line */
function pathExpressions(line) {
  /** @type {Map<number, number>} */
  const spans = new Map();
  for (const found of line.matchAll(FUNCTION_ATTRIBUTE)) {
    const start = (found.index ?? 0) + found[0].length - found[1].length;
    spans.set(start, start + found[1].length);
  }
  for (const found of line.matchAll(RELATIVE_LOCATION)) {
    spans.set(found.index ?? 0, (found.index ?? 0) + found[0].length);
  }
  return spans;
}

/**
 * Where the Python starting at `at` ends, or null when nothing Python starts there.
 *
 * A parenthesis is Python wherever it stands, since no command has one: a call takes its name
 * with it, and `(-self.item)` on its own is bolt's own way of naming a thing.
 *
 * @param {string} line @param {number} at
 * @returns {{ end: number, open: number } | null}  `open` is how many parentheses it leaves open at the end of the line.
 */
function pythonEndsAt(line, at) {
  const before = at > 0 ? line[at - 1] : "";
  if (!NOT_A_NAME.test(before)) {
    const prefixed = readAt(PREFIXED_STRING, line, at);
    if (prefixed) return { end: at + prefixed.length, open: 0 };

    const call = readAt(PYTHON_CALL, line, at);
    if (call) return closingParen(line, at + call.length);
  }
  return line[at] === "(" && before !== "$" ? closingParen(line, at + 1) : null;
}

/** An operator joining two Python operands, ex: the `/` of `(a)/(b)`. Sticky. */
const PYTHON_OPERATOR = /[ \t]*(?:\*\*|\/\/|[-+*/%@])[ \t]*/y;

/** An operand no parenthesis marks, ex: the `2` of `(a)*2`. Sticky. */
const BARE_OPERAND = /[\w.]+/y;

/**
 * The Python starting at `at` together with every operand an operator joins to it, or null when nothing Python starts there.
 * `(storage a)/(storage b)` is one expression, and masking its two halves alone leaves the `/` for a parser to report.
 * @param {string} line @param {number} at
 * @returns {{ end: number, open: number } | null}
 *
 * >>> joinedExpression("set compute default float (a)/(b)*2 run", 26)
 * { end: 35, open: 0 }
 */
function joinedExpression(line, at) {
  let expression = pythonEndsAt(line, at);
  while (expression && expression.open === 0) {
    const operator = readAt(PYTHON_OPERATOR, line, expression.end);
    if (!operator) break;
    const from = expression.end + operator.length;
    const bare = readAt(BARE_OPERAND, line, from);
    const next = pythonEndsAt(line, from) ?? (bare ? { end: from + bare.length, open: 0 } : null);
    if (!next) break;
    expression = next;
  }
  return expression;
}

/** Just past the `)` closing the parentheses open at `from`, or the end of the line and how many are still open there.
 *  @param {string} line @param {number} from @param {number} [depth] */
function closingParen(line, from, depth = 1) {
  for (let at = from; at < line.length; at++) {
    const quoted = readAt(QUOTED, line, at);
    if (quoted) { at += quoted.length - 1; continue; }
    if (line[at] === "(") depth++;
    else if (line[at] === ")" && --depth === 0) return { end: at + 1, open: 0 };
  }
  return { end: line.length, open: depth };
}

/** @param {RegExp} sticky @param {string} line @param {number} at @returns {string | null} */
function readAt(sticky, line, at) {
  sticky.lastIndex = at;
  const found = sticky.exec(line);
  return found ? found[0] : null;
}

module.exports = {
  COMMAND_LINE,
  NESTING_LINE,
  MAX_BLOCKS,
  commandsOf,
  commandBlocks,
  projectBolt,
  keptPart,
  maskPython,
};
