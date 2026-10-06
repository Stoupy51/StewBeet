// @ts-check
"use strict";

// Dropping what Spyglass reports on a bolt source, which it parses as mcfunction and underlines throughout.
//
// Spyglass keeps its language client to itself, but the collection that client publishes into is an
// instance of the extension host's DiagnosticCollection, and every extension in the host shares its
// prototype. Filtering `set` there keeps the file in Spyglass's index: the function it defines stays
// declared for the files that call it, and only the parse errors on its bolt lines are lost.
// The collection has a generated name, so Spyglass's diagnostics are told apart by their source.

const fs = require("fs");
const vscode = require("vscode");
const { looksLikeBolt, isBuildOutput } = require("./bolt");
const sourcemap = require("./sourcemap");
const navigation = require("./navigation");

// Constants

/** What Spyglass's diagnostics name as their source, followed by the game version. */
const SPYGLASS_SOURCE = "spyglassmc";

const CFG_KEY = "StewBeet";

// Registration

/**
 * Filter Spyglass's diagnostics on bolt sources for as long as the extension is active.
 *
 * Bolt-ness follows the same rule as the language id switch: the build's maps first, the text for
 * a project not built yet, never a file the build wrote, and nothing when `boltInMcfunction` is off.
 *
 * @param {vscode.ExtensionContext} context
 * @param {vscode.Event<void>} onBuild
 */
function registerSpyglassFilter(context, onBuild) {
  const probe = vscode.languages.createDiagnosticCollection("stewbeet-probe");
  /** @type {any} */
  let owner = Object.getPrototypeOf(probe);
  while (owner && !Object.prototype.hasOwnProperty.call(owner, "set")) owner = Object.getPrototypeOf(owner);
  probe.dispose();
  if (!owner) return;

  const original = owner.set;
  /** Spyglass's collection, known once it has published. @type {vscode.DiagnosticCollection | undefined} */
  let spyglass;
  /** @type {Map<string, boolean>} */
  const verdicts = new Map();

  /** @param {vscode.Uri} uri */
  function isBolt(uri) {
    if (uri.scheme !== "file" || !uri.fsPath.endsWith(".mcfunction")) return false;
    const cfg = vscode.workspace.getConfiguration(CFG_KEY);
    if (!cfg.get("boltInMcfunction", true)) return false;
    const known = verdicts.get(uri.fsPath);
    if (known !== undefined) return known;

    const configured = cfg.get("buildOutput", "");
    const outputs = typeof configured === "string" && configured ? [configured] : [];
    // The source map index is cached from the first list it is given, so it is never asked before the maps are found.
    const maps = navigation.knownMaps();
    const verdict = !isBuildOutput(uri.fsPath, outputs)
      && ((maps.length > 0 && sourcemap.isBoltSource(maps, uri.fsPath)) || looksLikeBolt(readText(uri.fsPath)));
    verdicts.set(uri.fsPath, verdict);
    return verdict;
  }

  /**
   * @param {vscode.DiagnosticCollection} collection
   * @param {vscode.Uri} uri
   * @param {readonly vscode.Diagnostic[] | undefined} list
   */
  function kept(collection, uri, list) {
    if (!list || !list.some(fromSpyglass)) return list;
    spyglass = collection;
    return isBolt(uri) ? list.filter(d => !fromSpyglass(d)) : list;
  }

  /**
   * @this {vscode.DiagnosticCollection}
   * @param {vscode.Uri | readonly [vscode.Uri, readonly vscode.Diagnostic[] | undefined][]} first
   * @param {readonly vscode.Diagnostic[] | undefined} [diagnostics]
   */
  owner.set = function (first, diagnostics) {
    if (Array.isArray(first)) return original.call(this, first.map(([uri, list]) => [uri, kept(this, uri, list)]));
    return original.call(this, first, kept(this, /** @type {vscode.Uri} */ (first), diagnostics));
  };

  /** Judge every file again, and clear what Spyglass already published on those that turned out to be bolt. */
  async function rejudge() {
    await navigation.findMaps();
    verdicts.clear();
    if (!spyglass) return;
    /** @type {[vscode.Uri, vscode.Diagnostic[]][]} */
    const cleared = [];
    spyglass.forEach((uri, list) => { if (isBolt(uri)) cleared.push([uri, list.filter(d => !fromSpyglass(d))]); });
    original.call(spyglass, cleared);
  }

  context.subscriptions.push(
    { dispose: () => { owner.set = original; } },
    onBuild(rejudge),
    vscode.workspace.onDidSaveTextDocument(rejudge),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration(`${CFG_KEY}.boltInMcfunction`) || e.affectsConfiguration(`${CFG_KEY}.buildOutput`)) rejudge();
    }),
  );
}

/** @param {vscode.Diagnostic} diagnostic */
function fromSpyglass(diagnostic) {
  return String(diagnostic.source ?? "").startsWith(SPYGLASS_SOURCE);
}

/**
 * A file's text, empty when it cannot be read, which is a deleted file Spyglass is clearing.
 * @param {string} filePath
 * @returns {string}
 */
function readText(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return "";
  }
}

module.exports = {
  SPYGLASS_SOURCE,
  registerSpyglassFilter,
};
