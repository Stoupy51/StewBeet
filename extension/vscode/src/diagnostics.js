// @ts-check
"use strict";

// Relay of build diagnostics onto the Python that wrote the command.
//
// Spyglass reports errors against the generated .mcfunction files, where the author never
// looks. This mirrors each of them onto the Python line the source map names, so a command the
// game would reject is underlined where it was written.
//
// The grouping rule is the important one: every Python file's set is replaced wholesale on each
// change rather than appended to, or a rebuild leaves the author staring at errors they fixed.

const vscode = require("vscode");
const sourcemap = require("./sourcemap");

// ─── Constants──────────────

const CFG_KEY = "StewBeet";

const COLLECTION_NAME = "stewbeet";

/** @type {vscode.DiagnosticCollection | undefined} */
let collection;

// ─── Relay──────────────────

/**
 * Move one diagnostic onto its Python line, or drop it.
 *
 * The map carries no column precision for the generated side, so the whole Python line is
 * marked rather than a range that would be confidently wrong. The original `source` is kept
 * inside the new one so the author can still see who complained.
 *
 * @param {vscode.Diagnostic} diagnostic
 * @param {string} generatedPath
 * @returns {{ file: string, diagnostic: vscode.Diagnostic } | null}
 */
function relocate(diagnostic, generatedPath) {
  const origin = sourcemap.originOf(generatedPath, diagnostic.range.start.line);
  if (!origin) return null; // an unmapped line is always safe to skip (G4)

  const range = new vscode.Range(origin.line, 0, origin.line, Number.MAX_SAFE_INTEGER);
  const moved = new vscode.Diagnostic(range, diagnostic.message, diagnostic.severity);
  moved.source = diagnostic.source ? `${COLLECTION_NAME} (${diagnostic.source})` : COLLECTION_NAME;
  moved.code = diagnostic.code;
  return { file: origin.file, diagnostic: moved };
}

/**
 * Rebuild the relayed set from every generated file VS Code currently has diagnostics for.
 *
 * Reading the whole picture each time is what makes the replacement safe: a file that no
 * longer produces any diagnostic simply stops appearing, and its squiggles go with it.
 */
function refresh() {
  if (!collection) return;
  if (!vscode.workspace.getConfiguration(CFG_KEY).get("sourceMapDiagnostics", true)) {
    collection.clear();
    return;
  }

  /** @type {Map<string, vscode.Diagnostic[]>} */
  const byPythonFile = new Map();
  for (const [uri, diagnostics] of vscode.languages.getDiagnostics()) {
    if (uri.scheme !== "file" || !uri.fsPath.endsWith(".mcfunction")) continue;
    for (const diagnostic of diagnostics) {
      const moved = relocate(diagnostic, uri.fsPath);
      if (!moved) continue;
      const bucket = byPythonFile.get(moved.file);
      if (bucket) bucket.push(moved.diagnostic);
      else byPythonFile.set(moved.file, [moved.diagnostic]);
    }
  }

  collection.clear();
  for (const [file, diagnostics] of byPythonFile) {
    collection.set(vscode.Uri.file(file), diagnostics);
  }
}

// ─── Registration───────────

/**
 * Start relaying, and stop cleanly on deactivation.
 * Does nothing observable when no build is present: no map, no origin, no diagnostic moved.
 * @param {vscode.ExtensionContext} context
 */
function registerDiagnosticRelay(context) {
  collection = vscode.languages.createDiagnosticCollection(COLLECTION_NAME);
  context.subscriptions.push(
    collection,
    vscode.languages.onDidChangeDiagnostics(refresh),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration(`${CFG_KEY}.sourceMapDiagnostics`)) refresh();
    }),
  );
  refresh();
}

module.exports = {
  COLLECTION_NAME,
  relocate,
  refresh,
  registerDiagnosticRelay,
};
