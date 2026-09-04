// @ts-check
"use strict";

// A clickable lens above each mcfunction block that the last build turned into a function.
//
// Navigation across the boundary already exists as commands; a lens is what makes it visible
// without knowing the palette. A block that produced nothing in the current build gets no
// lens at all, so a project with no build looks exactly as it did before.

const vscode = require("vscode");
const path = require("path");
const { blocksOf } = require("./virtual");
const navigation = require("./navigation");
const sourcemap = require("./sourcemap");

// ─── Constants──────────────

const CFG_KEY = "StewBeet";

// ─── Provider───────────────

const onDidChangeEmitter = new vscode.EventEmitter();

/**
 * The resource location a generated path spells, for the lens to name the target.
 * Falls back to the file name for a layout the convention does not cover.
 * @param {string} generatedPath
 */
function functionIdOf(generatedPath) {
  const parts = generatedPath.replace(/\\/g, "/").split("/");
  const data = parts.lastIndexOf("data");
  const folder = parts.findIndex((part, i) => i > data && (part === "function" || part === "functions"));
  if (data === -1 || folder === -1 || folder <= data + 1) return path.basename(generatedPath);
  return `${parts[data + 1]}:${parts.slice(folder + 1).join("/").replace(/\.mcfunction$/, "")}`;
}

/**
 * The first generated location any line of a block produced, or null when it produced nothing.
 * @param {string[]} maps
 * @param {string} pythonPath
 * @param {number} from
 * @param {number} to
 * @returns {{ file: string, line: number } | null}
 */
function targetOfBlock(maps, pythonPath, from, to) {
  for (let line = from; line <= to; line++) {
    const [target] = sourcemap.generatedFrom(maps, pythonPath, line);
    if (target) return target;
  }
  return null;
}

const codeLensProvider = {
  onDidChangeCodeLenses: onDidChangeEmitter.event,

  /** @param {vscode.TextDocument} doc */
  async provideCodeLenses(doc) {
    if (!vscode.workspace.getConfiguration(CFG_KEY).get("codeLens", true)) return [];
    if (doc.uri.scheme !== "file") return [];

    const maps = await navigation.findMaps();
    if (maps.length === 0) return [];

    const lenses = [];
    for (const block of blocksOf(doc)) {
      const first = doc.positionAt(block.start).line;
      const target = targetOfBlock(maps, doc.uri.fsPath, first, doc.positionAt(block.end).line);
      if (!target) continue;
      lenses.push(new vscode.CodeLens(new vscode.Range(first, 0, first, 0), {
        title: `$(go-to-file) ${functionIdOf(target.file)}`,
        tooltip: target.file,
        command: "stewbeet.goToGenerated",
        arguments: [target],
      }));
    }
    return lenses;
  },
};

/** Ask VS Code for the lenses again, for when a build changed what the blocks produce. */
function refreshCodeLenses() {
  onDidChangeEmitter.fire(undefined);
}

/** @param {vscode.ExtensionContext} context */
function registerCodeLenses(context) {
  context.subscriptions.push(
    vscode.languages.registerCodeLensProvider({ language: "python" }, codeLensProvider),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration(`${CFG_KEY}.codeLens`)) refreshCodeLenses();
    }),
    onDidChangeEmitter,
  );
}

module.exports = {
  functionIdOf,
  targetOfBlock,
  codeLensProvider,
  refreshCodeLenses,
  registerCodeLenses,
};
