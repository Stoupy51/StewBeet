// @ts-check
"use strict";

// Telling a bolt file from a vanilla one, so Spyglass is not asked to parse a `for` loop.
//
// A project can enable bolt syntax inside `.mcfunction` files, and StewBeet's own minimal
// template does: `src/data/minimal/function/hello.mcfunction` opens with `for i in range(1, 6):`.
// That file is language id `mcfunction`, so Spyglass parses it, fails, and underlines most of it.
// Nothing can remove another extension's diagnostics, so the fix is to stop the file being
// `mcfunction` at all: it becomes `bolt`, which Spyglass does not select and this extension's
// bolt grammar does.
//
// Deliberately free of any "vscode" dependency, so the detection is testable under plain
// `node --test` against real files.

const fs = require("fs");
const path = require("path");
const { SOURCE_MAPPING_URL } = require("./sourcemap");

// Constants

/** Spyglass reads the first of these it finds in a project root. Its own order, kept. */
const SPYGLASS_CONFIG_NAMES = ["spyglass.json", ".spyglassrc", ".spyglassrc.json"];

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
  /^\s*(?:append\s+|prepend\s+|merge\s+)?(?:execute|function)\b[^#]*:\s*(?:#.*)?$/,
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
 * @param {string} filePath
 * @param {string[]} outputRoots  Absolute paths that hold build output, may be empty.
 * @returns {boolean}
 */
function isBuildOutput(filePath, outputRoots) {
  const normalized = filePath.replace(/\\/g, "/").toLowerCase();
  return outputRoots.some(root => {
    const prefix = root.replace(/\\/g, "/").toLowerCase().replace(/\/+$/, "");
    return normalized.startsWith(`${prefix}/`);
  });
}

// Telling Spyglass to skip the file

// Changing an open document's language id stops Spyglass answering *for that document*, and it is
// not enough on its own: Spyglass indexes a data pack off disk, so it reports a bolt file it has
// never been asked to open. Nothing removes another extension's diagnostics, but Spyglass has an
// `env.exclude` list of its own, and that does silence them. Configuring it is the supported fix,
// and it belongs to the project rather than to this extension, so it is offered and never forced.

/**
 * The Spyglass config a project root uses, existing or to be created.
 * @param {string} root
 * @returns {string}
 */
function spyglassConfigPath(root) {
  const existing = SPYGLASS_CONFIG_NAMES.find(name => fs.existsSync(path.join(root, name)));
  return path.join(root, existing ?? ".spyglassrc.json");
}

/**
 * The pattern naming one file, relative to a project root, in the shape Spyglass matches.
 * `getRels` hands picomatch a forward-slash relative path whatever the platform.
 * @param {string} root
 * @param {string} file
 * @returns {string}
 */
function excludePatternFor(root, file) {
  return path.relative(root, file).split(path.sep).join("/");
}

/**
 * A Spyglass config with `patterns` added to `env.exclude`, or null when it already had them all.
 *
 * Everything else in the file is carried through untouched: it is the project's config, and it
 * may hold dependencies and feature switches this extension knows nothing about.
 *
 * @param {any} config  The parsed config, or an empty object when there is none yet.
 * @param {string[]} patterns
 * @returns {any | null}
 */
function withExclusions(config, patterns) {
  const base = config && typeof config === "object" ? config : {};
  const env = base.env && typeof base.env === "object" ? base.env : {};
  const exclude = Array.isArray(env.exclude) ? env.exclude : [];

  const missing = patterns.filter(pattern => !exclude.includes(pattern));
  if (missing.length === 0) return null;
  return { ...base, env: { ...env, exclude: [...exclude, ...missing] } };
}

/**
 * Add exclusions to a project's Spyglass config, creating it when there is none.
 *
 * @param {string} root  The project root, which is where Spyglass looks.
 * @param {string[]} files  Absolute paths to exclude.
 * @returns {{ path: string, added: string[] } | null} null when nothing needed adding.
 */
function addExclusions(root, files) {
  const configPath = spyglassConfigPath(root);
  let current = {};
  if (fs.existsSync(configPath)) {
    try {
      current = JSON.parse(fs.readFileSync(configPath, "utf8"));
    } catch (e) {
      console.debug(`[StewBeet] ${configPath} is not readable JSON, leaving it alone`, e);
      return null;
    }
  }

  const patterns = files.map(file => excludePatternFor(root, file));
  const updated = withExclusions(current, patterns);
  if (!updated) return null;

  fs.writeFileSync(configPath, `${JSON.stringify(updated, null, 2)}\n`, "utf8");
  return { path: configPath, added: patterns };
}

module.exports = {
  BOLT_LINES,
  SCAN_LIMIT,
  SPYGLASS_CONFIG_NAMES,
  looksLikeBolt,
  isBuildOutput,
  spyglassConfigPath,
  excludePatternFor,
  withExclusions,
  addExclusions,
};
