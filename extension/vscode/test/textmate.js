// @ts-check
"use strict";

// The TextMate engine VS Code itself uses, loaded with this extension's grammars and the real
// MagicPython the bolt grammar and the Python injection both build on. Shared by tokenize.test.js,
// which drives the Python injection, and bolt.test.js, which drives source.bolt.
//
// Needs `npm install` for vscode-textmate and vscode-oniguruma, and a VS Code install to read
// MagicPython from. Missing either, `load` resolves to a string and every caller skips rather than
// failing: the suite reports what it could not check instead of pretending it passed.

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const SYNTAXES = path.join(__dirname, "..", "syntaxes");

/** VS Code ships MagicPython inside its own install, under a version-stamped directory. */
function findPythonGrammar() {
  const roots = [
    process.env.VSCODE_EXE && path.dirname(process.env.VSCODE_EXE),
    "D:\\Programs\\Microsoft VS Code",
    "C:\\Program Files\\Microsoft VS Code",
    path.join(os.homedir(), "AppData", "Local", "Programs", "Microsoft VS Code"),
    "/usr/share/code",
    "/Applications/Visual Studio Code.app/Contents/Resources",
  ].filter(Boolean);
  const tail = path.join("resources", "app", "extensions", "python", "syntaxes", "MagicPython.tmLanguage.json");
  for (const root of roots) {
    const direct = path.join(String(root), tail);
    if (fs.existsSync(direct)) return direct;
    // Some installs interpose a version-stamped directory between the root and `resources`.
    for (const entry of fs.existsSync(String(root)) ? fs.readdirSync(String(root)) : []) {
      const nested = path.join(String(root), entry, tail);
      if (fs.existsSync(nested)) return nested;
    }
  }
  return null;
}

/**
 * Build a tokenizer rooted at one scope.
 * @param {string} rootScope
 * @returns {Promise<{ tokenize: (source: string) => { text: string, scopes: string[] }[][] } | string>}
 */
async function load(rootScope) {
  let vsctm, oniguruma;
  try {
    vsctm = require("vscode-textmate");
    oniguruma = require("vscode-oniguruma");
  } catch {
    return "vscode-textmate and vscode-oniguruma are not installed; run `npm install`";
  }
  const python = findPythonGrammar();
  if (!python) return "no VS Code install found to read MagicPython from; set VSCODE_EXE";

  await oniguruma.loadWASM(fs.readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm")).buffer);
  const files = {
    "source.python": python,
    "source.mcfunction.embedded": path.join(SYNTAXES, "mcfunction-embedded.tmLanguage.json"),
    "stewbeet.mcfunction-injection": path.join(SYNTAXES, "mcfunction-injection.tmLanguage.json"),
    "source.bolt": path.join(SYNTAXES, "bolt.tmLanguage.json"),
  };
  const registry = new vsctm.Registry({
    onigLib: Promise.resolve({
      createOnigScanner: (/** @type {string[]} */ s) => new oniguruma.OnigScanner(s),
      createOnigString: (/** @type {string} */ s) => new oniguruma.OnigString(s),
    }),
    loadGrammar: (/** @type {string} */ scope) => Promise.resolve(
      files[scope] ? vsctm.parseRawGrammar(fs.readFileSync(files[scope], "utf8"), files[scope]) : null,
    ),
    getInjections: (/** @type {string} */ scope) => (scope === "source.python" ? ["stewbeet.mcfunction-injection"] : undefined),
  });
  const grammar = await registry.loadGrammar(rootScope);

  return {
    tokenize(source) {
      let state = vsctm.INITIAL;
      return source.split("\n").map(line => {
        const result = grammar.tokenizeLine(line, state);
        state = result.ruleStack;
        return result.tokens
          .map((/** @type {{ startIndex: number, endIndex: number, scopes: string[] }} */ t) =>
            ({ text: line.substring(t.startIndex, t.endIndex), scopes: t.scopes }))
          .filter((/** @type {{ text: string }} */ t) => t.text.trim());
      });
    },
  };
}

/** Scopes of the first token whose text is exactly `word`, across every line. */
function scopesOf(lines, word) {
  for (const line of lines) {
    const hit = line.find(t => t.text === word);
    if (hit) return hit.scopes;
  }
  return null;
}

module.exports = { load, scopesOf, SYNTAXES };
