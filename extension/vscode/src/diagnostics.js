// @ts-check
"use strict";

// Diagnostics on the Python that wrote the command, from two sources.
//
// The one that matters is the projection: Spyglass reports on the virtual documents in
// ./virtual.js, whose lines are in lockstep with the Python, so an error comes home with no
// build and no source map. That is `live`, and it is why nothing under the build output is
// ever opened here.
//
// The other is the generated .mcfunction files the author has open themselves. What the server
// says about each is kept in `captured`, because VS Code disposes a document nothing is
// looking at and the server drops its diagnostics with it. Where the two describe the same
// mistake, the live one wins: it knows the columns, and the generated file knows only a line.

const vscode = require("vscode");
const sourcemap = require("./sourcemap");
const navigation = require("./navigation");
const virtual = require("./virtual");

// Constants

const CFG_KEY = "StewBeet";

const COLLECTION_NAME = "stewbeet";

/** Rules silenced by default. `undeclaredSymbol` fires on every objective a dependency
 *  declares, which Spyglass cannot see, and those are far more intrusive on a Python line
 *  than in a generated file nobody opens. */
const DEFAULT_DENYLIST = ["undeclaredSymbol"];

/** Spyglass names the rule at the end of the message rather than in `code`. */
const RULE_IN_MESSAGE = /\(rule:\s*([^)\s]+)\s*\)\s*$/;

/** The server reports on a virtual document in bursts as it parses it. */
const LIVE_DEBOUNCE_MS = 120;

/** How often the blocks are woken with nothing having changed. VS Code lets go of a document
 *  nothing is showing once too many have been opened, and the server stops reporting on it
 *  with no event to say so, so the only way back is to ask again every so often. */
const KEEPALIVE_MS = 30000;

/** @type {vscode.DiagnosticCollection | undefined} */
let collection;

/** @type {vscode.OutputChannel | undefined} */
let output;

/**
 * Trace one step of the relay into the StewBeet output channel.
 * This path has several places where doing nothing looks exactly like working, so it says out
 * loud what it found: no maps, no open Python file, nothing the server would report on.
 * @param {string} message
 */
function log(message) {
  if (output) output.appendLine(`[${new Date().toISOString().slice(11, 19)}] ${message}`);
}

// What the server said

/** Diagnostics per generated file, kept after its document closes. @type {Map<string, readonly vscode.Diagnostic[]>} */
const captured = new Map();

/**
 * Record what the server currently says about one generated file.
 *
 * An empty set for a document that is no longer open means the server dropped the file when
 * VS Code collected it, not that the file became clean, so the last known set is kept. A
 * deliberate reload clears the entry first, which is what lets a fixed error disappear.
 *
 * @param {vscode.Uri} uri
 * @returns {boolean}  Whether anything changed.
 */
function capture(uri) {
  const diagnostics = vscode.languages.getDiagnostics(uri);
  const open = vscode.workspace.textDocuments.some(doc => doc.uri.toString() === uri.toString());
  if (diagnostics.length === 0 && !open && captured.has(uri.fsPath)) return false;

  captured.set(uri.fsPath, diagnostics);
  return true;
}

/** @param {vscode.Uri} uri */
function isGenerated(uri) {
  return uri.scheme === "file" && uri.fsPath.endsWith(".mcfunction");
}

/** @param {vscode.DiagnosticChangeEvent} event */
function onDiagnosticsChanged(event) {
  let touched = false;
  for (const uri of event.uris) {
    // Reading only: the server has just spoken, and waking it here would make it speak again.
    if (uri.scheme === virtual.SCHEME) { scheduleLive({ wake: "none" }); continue; }
    if (isGenerated(uri) && capture(uri)) touched = true;
  }
  if (touched) publish();
}

// Relay

/**
 * The rule a diagnostic was raised under, as a plain string.
 *
 * `code` is where the protocol puts it, as a string, a number or `{ value, target }`. Spyglass
 * leaves it empty and writes `(rule: undeclaredSymbol)` at the end of the message instead, so
 * both are read.
 *
 * @param {vscode.Diagnostic} diagnostic
 */
function ruleOf(diagnostic) {
  const code = diagnostic.code;
  if (code !== undefined && code !== null) {
    const value = typeof code === "object" ? code.value : code;
    if (value !== undefined && value !== null && String(value) !== "") return String(value);
  }
  const named = RULE_IN_MESSAGE.exec(diagnostic.message || "");
  return named ? named[1] : "";
}

/**
 * Tag a diagnostic as ours while keeping whoever raised it visible.
 * Every diagnostic on a Python file goes through this, whether it came from a generated file
 * or straight off the projection, so one glance says where it came from.
 * @param {string | undefined} source
 */
function label(source) {
  return source ? `${COLLECTION_NAME} (${source})` : COLLECTION_NAME;
}

/**
 * Move one diagnostic onto its Python line, or drop it.
 * @param {vscode.Diagnostic} diagnostic
 * @param {string} generatedPath
 * @returns {{ file: string, diagnostic: vscode.Diagnostic } | null}
 */
function relocate(diagnostic, generatedPath) {
  const origin = sourcemap.originOf(generatedPath, diagnostic.range.start.line);
  if (!origin) return null; // an unmapped line is always safe to skip (G4)

  const range = new vscode.Range(origin.line, 0, origin.line, Number.MAX_SAFE_INTEGER);
  const moved = new vscode.Diagnostic(range, diagnostic.message, diagnostic.severity);
  moved.source = label(diagnostic.source);
  moved.code = diagnostic.code;
  return { file: origin.file, diagnostic: moved };
}

/** Diagnostics read off the virtual documents, per Python file. @type {Map<string, vscode.Diagnostic[]>} */
const live = new Map();

/** When the running pass started, or 0 when none is. Bursts of edits must not stack round
 *  trips, but a pass that never finishes must not be able to stop every later one either. */
let collectingSince = 0;

/** Past this, a pass counts as lost and the next one runs regardless. */
const PASS_TIMEOUT_MS = 20000;

/** Passes made, so the status command shows a relay that is spinning as clearly as a dead one. */
let livePasses = 0;

/**
 * Ask Spyglass about every open Python file's blocks directly.
 *
 * This is the path that needs no build and no generated file: the virtual documents are open
 * already for completion, their lines are in lockstep with the Python, and the server reports
 * on them as the author types.
 */
async function collectLive() {
  // Waking a document is a round trip to the server, and an edit arrives long before the last
  // pass has finished. A skipped pass costs nothing: the wake it skipped makes the server
  // report, and that reports back here as another change.
  if (collectingSince && Date.now() - collectingSince < PASS_TIMEOUT_MS) return;
  collectingSince = Date.now();
  livePasses++;
  const wake = wakeNext;
  wakeNext = "none";
  const startedAt = Date.now();
  const collected = new Map();
  let blocks = 0;
  try {
    for (const doc of vscode.workspace.textDocuments) {
      if (doc.languageId !== "python" || doc.uri.scheme !== "file") continue;
      blocks += virtual.blocksOf(doc).length;
      const found = await virtual.pythonDiagnosticsFor(doc, { wake });
      for (const diagnostic of found) diagnostic.source = label(diagnostic.source);
      if (found.length > 0) collected.set(doc.uri.fsPath, found);
    }
  } catch (e) {
    // Never let this path fail silently: it is the one the author notices as "nothing happens".
    log(`reading the projection failed: ${e && e.stack ? e.stack : e}`);
    return;
  } finally {
    collectingSince = 0;
  }

  live.clear();
  for (const [file, found] of collected) live.set(file, found);
  log(`${wake === "none" ? "read" : `woke (${wake}) and read`} `
    + `${[...live.values()].reduce((n, d) => n + d.length, 0)} live diagnostic(s) `
    + `from ${blocks} block(s) in ${collected.size} Python file(s) in ${Date.now() - startedAt}ms`);
  publish();
}

/** What the relay currently knows, for the status command and the integration test. */
function status() {
  return {
    captured: captured.size,
    liveFiles: live.size,
    liveCount: [...live.values()].reduce((n, d) => n + d.length, 0),
    livePasses,
    openPython: vscode.workspace.textDocuments.filter(d => d.languageId === "python").length,
    published: published.length,
  };
}

/** @type {NodeJS.Timeout | undefined} */
let liveTimer;

/** How much waking the next pass owes, the strongest of what its callers asked for.
 *  @type {"none" | "changed" | "all"} */
let wakeNext = "none";

/** @type {Record<"none" | "changed" | "all", number>} */
const WAKE_RANK = { none: 0, changed: 1, all: 2 };

/**
 * Ask for a pass, coalescing the burst the server reports in into one.
 * @param {{ wake: "none" | "changed" | "all" }} options  How much waking it owes, see ./virtual.js.
 */
function scheduleLive({ wake }) {
  if (WAKE_RANK[wake] > WAKE_RANK[wakeNext]) wakeNext = wake;
  if (liveTimer) clearTimeout(liveTimer);
  liveTimer = setTimeout(() => { liveTimer = undefined; void collectLive(); }, LIVE_DEBOUNCE_MS);
}

/** What was last published, so writing it does not trigger another pass through our own event. */
let published = "";

/**
 * Rebuild the Python-side collection from both sources.
 *
 * The denylist is applied here rather than at capture time, so changing the setting takes
 * effect without waiting for a rebuild. Writing the collection fires `onDidChangeDiagnostics`,
 * which is what calls this in the first place, so an unchanged result returns before touching
 * the collection and the cycle stops.
 */
function publish() {
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

  // Live first, and a build diagnostic saying the same thing about the same line is dropped
  // rather than added beside it. Both describe one mistake; the live one knows which columns
  // it covers, and all the generated file can say is which line it was on.
  const seen = new Set();
  for (const [file, diagnostics] of live) {
    const bucket = [];
    for (const diagnostic of diagnostics) {
      if (denylist.has(ruleOf(diagnostic))) continue;
      seen.add(`${file} ${diagnostic.range.start.line} ${diagnostic.message}`);
      bucket.push(diagnostic);
    }
    if (bucket.length > 0) byPythonFile.set(file, bucket);
  }

  for (const [generatedPath, diagnostics] of captured) {
    for (const diagnostic of diagnostics) {
      if (denylist.has(ruleOf(diagnostic))) continue;
      const moved = relocate(diagnostic, generatedPath);
      if (!moved) continue;
      if (seen.has(`${moved.file} ${moved.diagnostic.range.start.line} ${moved.diagnostic.message}`)) continue;
      const bucket = byPythonFile.get(moved.file);
      if (bucket) bucket.push(moved.diagnostic);
      else byPythonFile.set(moved.file, [moved.diagnostic]);
    }
  }

  const fingerprint = JSON.stringify([...byPythonFile].map(
    ([file, diagnostics]) => [file, diagnostics.map(d => `${d.range.start.line} ${d.message}`).sort()]));
  if (fingerprint === published) return;
  published = fingerprint;
  log(`relaying ${[...byPythonFile.values()].reduce((n, d) => n + d.length, 0)} diagnostic(s) `
    + `onto ${byPythonFile.size} Python file(s), from ${captured.size} captured generated file(s)`);

  collection.clear();
  for (const [file, diagnostics] of byPythonFile) {
    collection.set(vscode.Uri.file(file), diagnostics);
  }
}

/** Capture every generated file VS Code already has diagnostics for, then publish. */
function refresh() {
  for (const [uri] of vscode.languages.getDiagnostics()) {
    if (isGenerated(uri)) capture(uri);
  }
  publish();
}

/** @param {vscode.Uri} uri */
function forget(uri) {
  if (captured.delete(uri.fsPath)) publish();
}

/**
 * Throw away everything known and ask again from scratch.
 * The escape hatch for a build that finished somewhere the watcher could not see, and the
 * first thing to try when the relay is quiet: the output channel then says why.
 */
function reload() {
  captured.clear();
  published = "";
  navigation.forgetMaps();
  sourcemap.clearCache();
  log("reload requested");
  refresh();
  scheduleLive({ wake: "all" });
}

// Registration

/**
 * Start relaying, and stop cleanly on deactivation.
 * Does nothing observable when no build is present: no map, no origin, no diagnostic moved.
 * @param {vscode.ExtensionContext} context
 */
function registerDiagnosticRelay(context) {
  collection = vscode.languages.createDiagnosticCollection(COLLECTION_NAME);
  output = vscode.window.createOutputChannel("StewBeet");
  const keepalive = setInterval(() => scheduleLive({ wake: "all" }), KEEPALIVE_MS);
  context.subscriptions.push(
    collection,
    output,
    vscode.commands.registerCommand("stewbeet.refreshDiagnostics", reload),
    vscode.commands.registerCommand("stewbeet.diagnosticsStatus", status),
    vscode.languages.onDidChangeDiagnostics(onDiagnosticsChanged),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration(CFG_KEY)) publish();
    }),
    vscode.workspace.onDidOpenTextDocument(() => scheduleLive({ wake: "changed" })),
    vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.languageId === "python") scheduleLive({ wake: "changed" });
    }),
    { dispose: () => { if (liveTimer) clearTimeout(liveTimer); } },
    { dispose: () => clearInterval(keepalive) },
  );
  refresh();
  scheduleLive({ wake: "changed" });
}

module.exports = {
  COLLECTION_NAME,
  DEFAULT_DENYLIST,
  ruleOf,
  relocate,
  refresh,
  forget,
  publish,
  reload,
  status,
  registerDiagnosticRelay,
};
