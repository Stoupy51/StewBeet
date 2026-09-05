// @ts-check
"use strict";

// A clickable lens above each mcfunction block that the last build turned into a function.
//
// Navigation across the boundary already exists as commands; a lens is what makes it visible
// without knowing the palette. A block that produced nothing in the current build gets no
// lens at all, so a project with no build looks exactly as it did before.

const vscode = require("vscode");
const path = require("path");
const navigation = require("./navigation");
const { blocksOf } = require("./virtual");
const sourcemap = require("./sourcemap");

// Constants

const CFG_KEY = "StewBeet";

// Provider

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
 * What a block produced, or null when the current build knows nothing about it.
 *
 * Two shapes of origin exist. Commands written inline map line by line, so the answer sits on
 * one of the block's own lines. Commands arriving in a variable are all attributed to the call
 * itself, so the answer sits on the call line. Both are tried.
 *
 * @param {Map<number, { file: string, line: number }>} origins
 * @param {vscode.TextDocument} doc
 * @param {{ start:number, end:number }} block
 * @param {number} callLine
 * @returns {{ file: string, line: number } | null}
 */
function targetOfBlock(origins, doc, block, callLine) {
  const found = origins.get(callLine);
  if (found) return found;

  const last = doc.positionAt(block.end).line;
  for (let line = doc.positionAt(block.start).line; line <= last; line++) {
    const inside = origins.get(line);
    if (inside) return inside;
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

    // One lens per `write_*` call, never one per command.
    //
    // The map records an origin for every generated line, and for a block written inline that
    // is every line of the block, so reading the map alone puts a lens on all twenty lines of
    // a function. The blocks say which call each of them feeds, and that call is the one place
    // a reader wants the link, whether the commands sit in the call or in a variable above it.
    const origins = sourcemap.originLinesFor(maps, doc.uri.fsPath);
    if (origins.size === 0) return [];

    const lenses = [];
    const placed = new Set();
    for (const block of blocksOf(doc)) {
      const line = doc.positionAt(block.callStart).line;
      if (placed.has(line)) continue;

      const target = targetOfBlock(origins, doc, block, line);
      if (!target) continue;
      placed.add(line);
      lenses.push(new vscode.CodeLens(new vscode.Range(line, 0, line, 0), {
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
