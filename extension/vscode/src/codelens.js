// @ts-check
"use strict";

// A clickable lens above each mcfunction block that the last build turned into a function.
//
// Navigation across the boundary already exists as commands; a lens is what makes it visible
// without knowing the palette. A block that produced nothing in the current build gets no
// lens at all, so a project with no build looks exactly as it did before.

const vscode = require("vscode");
const navigation = require("./navigation");
const { blocksOf } = require("./virtual");
const { functionIdOf, targetOfBlock, lensAnchors } = require("./lenses");
const sourcemap = require("./sourcemap");

// Constants

const CFG_KEY = "StewBeet";

// Provider

const onDidChangeEmitter = new vscode.EventEmitter();

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

const boltLensProvider = {
  onDidChangeCodeLenses: onDidChangeEmitter.event,

  /**
   * The other half of the header lens, for a source file that is not Python.
   * A `.bolt` module, or a `.mcfunction` holding bolt, reaches what the build made of it.
   * @param {vscode.TextDocument} doc
   */
  async provideCodeLenses(doc) {
    if (!vscode.workspace.getConfiguration(CFG_KEY).get("codeLens", true)) return [];
    if (doc.uri.scheme !== "file") return [];

    const maps = await navigation.findMaps();
    if (maps.length === 0) return [];

    // A generated file is not a source of anything, so it never appears in the reverse index
    // and this costs one lookup before returning nothing.
    const origins = sourcemap.originLinesFor(maps, doc.uri.fsPath);
    if (origins.size === 0) return [];

    return lensAnchors(origins).map(({ line, target }) => new vscode.CodeLens(
      new vscode.Range(line, 0, line, 0), {
        title: `$(go-to-file) ${functionIdOf(target.file)}`,
        tooltip: target.file,
        command: "stewbeet.goToGenerated",
        arguments: [target],
      }));
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
    // `mcfunction` as well as `bolt`, so a source file keeps its lens whether or not the
    // language switch in bolt.js decided it was bolt. On a generated file this finds nothing.
    vscode.languages.registerCodeLensProvider({ language: "bolt" }, boltLensProvider),
    vscode.languages.registerCodeLensProvider({ language: "mcfunction", scheme: "file" }, boltLensProvider),
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
  boltLensProvider,
  refreshCodeLenses,
  registerCodeLenses,
};
