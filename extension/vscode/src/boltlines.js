// @ts-check
"use strict";

// What a datapack parser should see of a bolt file.
//
// The same trick ./projection.js plays on a Python string, played on a whole file: everything
// that is not a command becomes spaces, and what is left reaches Spyglass as a plain .mcfunction
// whose lines are in lockstep with the source. That is what buys back the completion and the
// ctrl+click a `.bolt` file loses by not being `mcfunction`.
//
// The classifier is not written here. Both regexes are read out of the bolt grammar this
// extension ships, so a line coloured as a command is a line projected as one, and regenerating
// the grammar from mecha's command tree updates both at once.
//
// Deliberately free of any "vscode" dependency, so it is testable under plain `node --test`.

const fs = require("fs");
const path = require("path");
const { MASK } = require("./projection");

// The grammar's own rules

/** @type {{ repository: Record<string, { begin: string }> }} */
const GRAMMAR = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "syntaxes", "bolt.tmLanguage.json"), "utf8"));

/** A line whose first word is one of mecha's root commands. Capture 1 is its indentation. */
const COMMAND_LINE = new RegExp(GRAMMAR.repository["command-statement"].begin);

/** `function <path>:` and its append, prepend and merge forms. Capture 1 is the indentation. */
const NESTING_LINE = new RegExp(GRAMMAR.repository["nesting-statement"].begin);

/** A command being typed, which no rule above matches yet and completion is most wanted on.
 *  A lone lowercase word is not a statement Python has any use for, `pass` and its siblings
 *  aside, and it is what every command looks like three keystrokes in. */
const TYPING_COMMAND = /^([ \t]*)([a-z][a-z0-9_-]*)[ \t]*$/;

/** Python statements a lone word can be, so they keep their own colours and offer no commands. */
const PYTHON_WORDS = new Set(["pass", "return", "break", "continue", "yield", "raise", "else", "try", "finally"]);

// Python inside a command

/** A string with a Python prefix, ex: `f"{self.path}/open"`. mcfunction has no string prefixes,
 *  so the prefix is what tells one from the quoted arguments a command really does take. */
const PREFIXED_STRING = /[fFrRbBuU]{1,2}(?:"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/y;

/** A call, ex: `has_item_predicate(self.item)`. Nothing in mcfunction puts a bare `(` after a word. */
const PYTHON_CALL = /[A-Za-z_]\w*[ \t]*\(/y;

/** What Python may not follow. `@s (-self.item)` is a selector and a bolt expression rather than a
 *  call named `s`, and `$(x)` is a macro placeholder rather than either. */
const NOT_A_NAME = /[\w@#$~^]/;

/** A quoted argument of a command, copied through so a `(` inside it is not read as a call. */
const QUOTED = /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/y;

// Projection

/**
 * Project a whole bolt file into the mcfunction document Spyglass should see.
 *
 * Every line keeps its number, and a kept line loses its indentation: the virtual document is a
 * flat list of commands, which is what a `.mcfunction` is, and the table gives every column back.
 *
 * @param {string} text
 * @returns {{ text: string, table: Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>, masked: Map<number, { start:number, end:number }[]> }}
 */
function projectBolt(text) {
  /** @type {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} */
  const table = new Map();
  /** @type {Map<number, { start:number, end:number }[]>} */
  const masked = new Map();

  const projected = text.split("\n").map((raw, line) => {
    const carriage = raw.endsWith("\r");
    const body = carriage ? raw.slice(0, -1) : raw;
    const kept = keptPart(body);
    if (!kept) return " ".repeat(body.length) + (carriage ? "\r" : "");

    const { text: command, runs } = maskPython(kept.text);
    if (kept.start > 0) table.set(line, [{ start: 0, pythonWidth: kept.start, virtualWidth: 0 }]);
    if (runs.length > 0) masked.set(line, runs);
    return command + (carriage ? "\r" : "");
  });

  return { text: projected.join("\n"), table, masked };
}

/**
 * The part of one line a datapack parser is meant to read, or null when the line is Python.
 *
 * A nesting statement keeps its `function <path>` and loses the `append` in front and the `:`
 * behind, both of which are mecha's own syntax rather than a command's.
 *
 * @param {string} line  One line, without its newline.
 * @returns {{ start: number, text: string } | null}  `start` is the column the text was taken from.
 */
function keptPart(line) {
  const nesting = NESTING_LINE.exec(line);
  if (nesting) {
    const start = nesting[0].length - "function".length;
    return { start, text: withoutBlockColon(line.slice(start)) };
  }

  const command = COMMAND_LINE.exec(line);
  if (command) return { start: command[1].length, text: withoutBlockColon(line.slice(command[1].length)) };

  const typing = TYPING_COMMAND.exec(line);
  if (typing && !PYTHON_WORDS.has(typing[2])) return { start: typing[1].length, text: typing[2] };

  return null;
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
 * everything after it is read as the command it is.
 *
 * @param {string} line
 * @returns {{ text: string, runs: { start:number, end:number }[] }}
 */
function maskPython(line) {
  let out = "";
  /** @type {{ start:number, end:number }[]} */
  const runs = [];

  for (let at = 0; at < line.length; ) {
    const end = pythonEndsAt(line, at);
    if (end === null) {
      const quoted = readAt(QUOTED, line, at);
      out += quoted ?? line[at];
      at += quoted ? quoted.length : 1;
      continue;
    }
    out += MASK.repeat(end - at);
    runs.push({ start: at, end });
    at = end;
  }
  return { text: out, runs };
}

/**
 * Where the Python starting at `at` ends, or null when nothing Python starts there.
 *
 * A parenthesis is Python wherever it stands, since no command has one: a call takes its name
 * with it, and `(-self.item)` on its own is bolt's own way of naming a thing.
 *
 * @param {string} line @param {number} at
 */
function pythonEndsAt(line, at) {
  const before = at > 0 ? line[at - 1] : "";
  if (!NOT_A_NAME.test(before)) {
    const prefixed = readAt(PREFIXED_STRING, line, at);
    if (prefixed) return at + prefixed.length;

    const call = readAt(PYTHON_CALL, line, at);
    if (call) return closingParen(line, at + call.length);
  }
  return line[at] === "(" && before !== "$" ? closingParen(line, at + 1) : null;
}

/** Just past the `)` closing a call whose `(` was at `from - 1`, or the end of the line.
 *  @param {string} line @param {number} from */
function closingParen(line, from) {
  let depth = 1;
  for (let at = from; at < line.length; at++) {
    const quoted = readAt(QUOTED, line, at);
    if (quoted) { at += quoted.length - 1; continue; }
    if (line[at] === "(") depth++;
    else if (line[at] === ")" && --depth === 0) return at + 1;
  }
  return line.length;
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
  projectBolt,
  keptPart,
  maskPython,
};
