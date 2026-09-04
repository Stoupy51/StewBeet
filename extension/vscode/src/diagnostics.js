// @ts-check
"use strict";

// Relay of build diagnostics onto the Python that wrote the command.
//
// Spyglass reports errors against the generated .mcfunction files, where the author never
// looks. This mirrors each of them onto the Python line the source map names, so a command the
// game would reject is underlined where it was written.
//
// Two rules carry the design. Every Python file's set is replaced wholesale on each change
// rather than appended to, or a rebuild leaves the author staring at errors they fixed. And a
// language server publishes diagnostics only for documents it has been handed, so a rebuild's
// files are opened here rather than waiting for the author to open one by hand.

const vscode = require("vscode");
const sourcemap = require("./sourcemap");

// ─── Constants──────────────

const CFG_KEY = "StewBeet";

const COLLECTION_NAME = "stewbeet";

/** Rules silenced by default. `undeclaredSymbol` fires on every objective a dependency
 *  declares, which Spyglass cannot see, and those are far more intrusive on a Python line
 *  than in a generated file nobody opens. */
const DEFAULT_DENYLIST = ["undeclaredSymbol"];

/** One rebuild rewrites every function in the pack, and each write arrives as its own event. */
const DEBOUNCE_MS = 400;

/** Opening a document parses it, so a full rebuild is spread over several passes rather than
 *  freezing the window for the length of one. */
const MAX_PER_PASS = 150;

/** @type {vscode.DiagnosticCollection | undefined} */
let collection;

// ─── Relay──────────────────

/**
 * The rule a diagnostic was raised under, as a plain string.
 * `code` is a string, a number, or `{ value, target }` depending on the server.
 * @param {vscode.Diagnostic} diagnostic
 */
function ruleOf(diagnostic) {
  const code = diagnostic.code;
  if (code === undefined || code === null) return "";
  return String(typeof code === "object" ? code.value : code);
}

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

/** What was last published, so writing it does not trigger another pass through our own event. */
let published = "";

/**
 * Rebuild the relayed set from every generated file VS Code currently has diagnostics for.
 *
 * Reading the whole picture each time is what makes the replacement safe: a file that no
 * longer produces any diagnostic simply stops appearing, and its squiggles go with it.
 *
 * Writing the collection fires `onDidChangeDiagnostics`, which is what calls this in the first
 * place, so an unchanged result returns before touching the collection and the cycle stops.
 */
function refresh() {
  if (!collection) return;
  const config = vscode.workspace.getConfiguration(CFG_KEY);
  if (!config.get("sourceMapDiagnostics", true)) {
    if (published === "") return;
    published = "";
    collection.clear();
    return;
  }
  const denylist = new Set(config.get("diagnosticRuleDenylist", DEFAULT_DENYLIST));

  /** @type {Map<string, vscode.Diagnostic[]>} */
  const byPythonFile = new Map();
  for (const [uri, diagnostics] of vscode.languages.getDiagnostics()) {
    if (uri.scheme !== "file" || !uri.fsPath.endsWith(".mcfunction")) continue;
    for (const diagnostic of diagnostics) {
      if (denylist.has(ruleOf(diagnostic))) continue;
      const moved = relocate(diagnostic, uri.fsPath);
      if (!moved) continue;
      const bucket = byPythonFile.get(moved.file);
      if (bucket) bucket.push(moved.diagnostic);
      else byPythonFile.set(moved.file, [moved.diagnostic]);
    }
  }

  const fingerprint = JSON.stringify([...byPythonFile].map(
    ([file, diagnostics]) => [file, diagnostics.map(d => `${d.range.start.line} ${d.message}`).sort()]));
  if (fingerprint === published) return;
  published = fingerprint;

  collection.clear();
  for (const [file, diagnostics] of byPythonFile) {
    collection.set(vscode.Uri.file(file), diagnostics);
  }
}

// ─── Loading what changed────

/** Generated files a build touched, waiting to be handed to the language server. @type {Set<string>} */
const pending = new Set();

/** @type {NodeJS.Timeout | undefined} */
let timer;

/**
 * Note that a build rewrote some generated functions.
 *
 * Nothing happens until the writes stop coming, so one rebuild produces one pass instead of
 * one per file.
 *
 * @param {vscode.Uri[]} uris
 */
function notifyGeneratedChanged(uris) {
  for (const uri of uris) pending.add(uri.toString());
  if (pending.size === 0) return;
  if (timer) clearTimeout(timer);
  timer = setTimeout(drain, DEBOUNCE_MS);
}

/**
 * Hand the next batch of changed files to the language server, then relay what it says.
 * `openTextDocument` loads a document without showing it, which is all a server needs to
 * start publishing diagnostics for it.
 */
async function drain() {
  timer = undefined;
  if (!vscode.workspace.getConfiguration(CFG_KEY).get("sourceMapDiagnostics", true)) {
    pending.clear();
    return;
  }

  const batch = [...pending].slice(0, MAX_PER_PASS);
  for (const key of batch) pending.delete(key);

  for (const key of batch) {
    try {
      await vscode.workspace.openTextDocument(vscode.Uri.parse(key));
    } catch (e) {
      console.debug(`[StewBeet] could not load ${key}`, e);
    }
  }
  refresh();

  // What did not fit waits for another pass rather than being dropped.
  if (pending.size > 0) timer = setTimeout(drain, DEBOUNCE_MS);
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
      if (e.affectsConfiguration(CFG_KEY)) refresh();
    }),
    { dispose: () => { if (timer) clearTimeout(timer); pending.clear(); } },
  );
  refresh();
}

module.exports = {
  COLLECTION_NAME,
  DEFAULT_DENYLIST,
  ruleOf,
  relocate,
  refresh,
  notifyGeneratedChanged,
  registerDiagnosticRelay,
};
