// @ts-check
"use strict";

// Telling a bolt file from a vanilla one, so Spyglass is not asked to parse a `for` loop.
//
// A project can enable bolt syntax inside `.mcfunction` files, and StewBeet's own minimal
// template does: `src/data/minimal/function/hello.mcfunction` opens with `for i in range(1, 6):`.
// That file is language id `mcfunction`, so Spyglass parses it, fails, and underlines most of it.
// The file becomes `bolt`, which Spyglass does not select and this extension's bolt grammar does,
// and `spyglassfilter` drops what Spyglass still reports on it from its index.
//
// Deliberately free of any "vscode" dependency, so the detection is testable under plain
// `node --test` against real files.

const fs = require("fs");
const { SOURCE_MAPPING_URL } = require("./sourcemap");

// Constants

/** Lines that are bolt and cannot be vanilla mcfunction, in the order they are worth testing.
 *
 * Precision matters far more than recall here. Missing a bolt file leaves it exactly as it is
 * today, while a false positive takes a working vanilla file away from Spyglass, which is a
 * real loss of completion and diagnostics. Every pattern below is impossible in mcfunction:
 * no command is named `def`, `class`, `for`, `while` or `if`, no command is followed by `=`,
 * and no command line ends in a colon outside mecha's nesting. */
const BOLT_LINES = [
  /^\s*(?:from\s+[\w./:-]+\s+import\b|import\s+[\w./:-]+)/,
  /^\s*(?:def|class)\s+\w+/,
  /^\s*(?:for|while|if|elif|else|try|except|finally|with)\b[^#]*:\s*(?:#.*)?$/,
  /^\s*[A-Za-z_]\w*(?:\.\w+)*\s*(?:[-+*/%|&^]|\/\/|\*\*|>>|<<)?=(?!=)/,
  /^\s*[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)+\s*=(?!=)/,
  /^\s*(?:append\s+|prepend\s+|merge\s+)?(?:execute|function)\b[^#]*:\s*(?:#.*)?$/,
  // A nested function opened at the end of an `execute` written over several lines, and a path relative to the current function.
  /\bfunction\s+[^\s#]+:\s*(?:#.*)?$/,
  /\bfunction\s+(?:~|\.\.?)\//,
  // An `execute` alone on its line is the first line of one written over several, which vanilla cannot do.
  /^\s*execute\s*$/,
  // An f-string where a command takes a value, which is Python by its prefix alone.
  /[\s:,[{(]f"[^"\n]*\{/,
  // A body opened on one line and closed on another, which is mecha's nested resources:
  // `enchantment ns:name {` and the JSON that follows. Vanilla closes every NBT and JSON
  // argument on the line that opens it, so a trailing brace cannot be a command.
  /^\s*[^#$\s][^#]*\{\s*$/,
];

/** How much of a file is read before giving up. A bolt construct in the first few hundred lines
 *  is what every real bolt file has; scanning a 10 MB generated pack file to prove a negative is
 *  not worth the pause it would add to opening one. */
const SCAN_LIMIT = 400;

// Detection

/**
 * Whether a document's text is bolt rather than vanilla mcfunction.
 *
 * @param {string} text
 * @returns {boolean}
 */
function looksLikeBolt(text) {
  // A build's own output is never bolt, whatever it contains: mecha has already compiled it.
  // Only a build written by an older StewBeet names its map in a comment; `isBuildOutput` is
  // what recognises the rest.
  if (text.includes(SOURCE_MAPPING_URL)) return false;

  const lines = text.split("\n", SCAN_LIMIT);
  for (const raw of lines) {
    const line = raw.replace(/\r$/, "");
    const trimmed = line.trimStart();
    if (trimmed === "" || trimmed.startsWith("#") || trimmed.startsWith("$")) continue;
    if (BOLT_LINES.some(pattern => pattern.test(line))) return true;
  }
  return false;
}

/**
 * Whether a path sits inside a build output rather than in the project's sources.
 *
 * A generated function is not bolt even when the module that wrote it was, and switching one
 * would take it away from Spyglass, which is the one thing generated output genuinely wants.
 *
 * A sidecar map beside the file says the same thing without any configuration: only a build
 * writes one, and it is the signal that survives when `buildOutput` names nothing.
 *
 * @param {string} filePath
 * @param {string[]} outputRoots  Absolute paths that hold build output, may be empty.
 * @returns {boolean}
 */
function isBuildOutput(filePath, outputRoots) {
  const normalized = filePath.replace(/\\/g, "/").toLowerCase();
  const named = outputRoots.some(root => {
    const prefix = root.replace(/\\/g, "/").toLowerCase().replace(/\/+$/, "");
    return normalized.startsWith(`${prefix}/`);
  });
  return named || fs.existsSync(`${filePath}.map`);
}

module.exports = {
  BOLT_LINES,
  SCAN_LIMIT,
  looksLikeBolt,
  isBuildOutput,
};
