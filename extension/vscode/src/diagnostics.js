// @ts-check
"use strict";

// Relay of build diagnostics onto the Python that wrote the command.
//
// Spyglass reports errors against the generated .mcfunction files, where the author never
// looks. This mirrors each of them onto the Python line the source map names, so a command the
// game would reject is underlined where it was written.
//
// The design turns on one fact: a language server only reports on documents it has been
// handed, and VS Code disposes a document nothing is looking at. So a rebuild's files are
// opened here, and what the server says about each one is kept in `captured` rather than read
// live. Without that, the squiggles vanish the moment VS Code collects the document again.

const vscode = require("vscode");
const sourcemap = require("./sourcemap");
const navigation = require("./navigation");
const virtual = require("./virtual");

// ─── Constants──────────────

const CFG_KEY = "StewBeet";

const COLLECTION_NAME = "stewbeet";

/** Rules silenced by default. `undeclaredSymbol` fires on every objective a dependency
 *  declares, which Spyglass cannot see, and those are far more intrusive on a Python line
 *  than in a generated file nobody opens. */
const DEFAULT_DENYLIST = ["undeclaredSymbol"];

/** Spyglass names the rule at the end of the message rather than in `code`. */
const RULE_IN_MESSAGE = /\(rule:\s*([^)\s]+)\s*\)\s*$/;

/** One rebuild rewrites every function in the pack, and each write arrives as its own event. */
const DEBOUNCE_MS = 400;

/** Opening a document parses it, so a full rebuild is spread over several passes rather than
 *  freezing the window for the length of one. Only the functions an open Python file produced
 *  are ever loaded, so this is a ceiling on a pathological file, not the usual size. */
const MAX_PER_PASS = 40;

/** How long a loaded batch is held. Releasing it immediately lets VS Code collect the
 *  documents before the server has looked at them, and nothing is ever reported. */
const HOLD_MS = 8000;

/** The server reports on a virtual document in bursts as it parses it. */
const LIVE_DEBOUNCE_MS = 120;

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

// ─── What the server said───

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
    if (uri.scheme === virtual.SCHEME) { scheduleLive(); continue; }
    if (isGenerated(uri) && capture(uri)) touched = true;
  }
  if (touched) publish();
}

// ─── Relay──────────────────

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

/**
 * Ask Spyglass about every open Python file's blocks directly.
 *
 * This is the path that needs no build and no generated file: the virtual documents are open
 * already for completion, their lines are in lockstep with the Python, and the server reports
 * on them as the author types.
 */
async function collectLive() {
  const collected = new Map();
  let blocks = 0;
  try {
    for (const doc of vscode.workspace.textDocuments) {
      if (doc.languageId !== "python" || doc.uri.scheme !== "file") continue;
      blocks += virtual.blocksOf(doc).length;
      const found = await virtual.pythonDiagnosticsFor(doc);
      for (const diagnostic of found) diagnostic.source = label(diagnostic.source);
      if (found.length > 0) collected.set(doc.uri.fsPath, found);
    }
  } catch (e) {
    // Never let this path fail silently: it is the one the author notices as "nothing happens".
    log(`reading the projection failed: ${e && e.stack ? e.stack : e}`);
    return;
  }

  live.clear();
  for (const [file, found] of collected) live.set(file, found);
  log(`read ${[...live.values()].reduce((n, d) => n + d.length, 0)} live diagnostic(s) `
    + `from ${blocks} block(s) in ${collected.size} Python file(s)`);
  publish();
}

/** What the relay currently knows, for the status command and the integration test. */
function status() {
  return {
    captured: captured.size,
    liveFiles: live.size,
    liveCount: [...live.values()].reduce((n, d) => n + d.length, 0),
    openPython: vscode.workspace.textDocuments.filter(d => d.languageId === "python").length,
    published: published.length,
  };
}

/** @type {NodeJS.Timeout | undefined} */
let liveTimer;

/** Spyglass reports in bursts as it parses, so this coalesces them into one pass. */
function scheduleLive() {
  if (liveTimer) clearTimeout(liveTimer);
  liveTimer = setTimeout(() => { liveTimer = undefined; void collectLive(); }, LIVE_DEBOUNCE_MS);
}

/** What was last published, so writing it does not trigger another pass through our own event. */
let published = "";

/**
 * Rebuild the Python-side collection from everything captured so far.
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
  for (const [generatedPath, diagnostics] of captured) {
    for (const diagnostic of diagnostics) {
      if (denylist.has(ruleOf(diagnostic))) continue;
      const moved = relocate(diagnostic, generatedPath);
      if (!moved) continue;
      const bucket = byPythonFile.get(moved.file);
      if (bucket) bucket.push(moved.diagnostic);
      else byPythonFile.set(moved.file, [moved.diagnostic]);
    }
  }

  for (const [file, diagnostics] of live) {
    const bucket = byPythonFile.get(file) ?? [];
    const seen = new Set(bucket.map(d => `${d.range.start.line} ${d.message}`));
    for (const diagnostic of diagnostics) {
      if (denylist.has(ruleOf(diagnostic))) continue;
      // A build error and a live one can be the same error seen twice.
      if (seen.has(`${diagnostic.range.start.line} ${diagnostic.message}`)) continue;
      bucket.push(diagnostic);
    }
    if (bucket.length > 0) byPythonFile.set(file, bucket);
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

// ─── Loading what changed────

/** Generated files a build touched, waiting to be handed to the language server. @type {Set<string>} */
const pending = new Set();

/** @type {NodeJS.Timeout | undefined} */
let timer;

/** The batch being analysed, held so VS Code does not collect it first. @type {vscode.TextDocument[]} */
let held = [];

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
 * Every generated file the currently open Python documents produced.
 *
 * This is the bound that keeps the relay cheap. A pack holds hundreds of generated functions
 * and a rebuild rewrites all of them, but the author can only see squiggles in a file they
 * have open, so nothing else is worth handing to the server.
 *
 * @returns {Promise<Set<string>>}  Lowercased paths.
 */
async function worthLoading() {
  const open = vscode.workspace.textDocuments.filter(
    doc => doc.languageId === "python" && doc.uri.scheme === "file");
  if (open.length === 0) {
    log("nothing to load: no Python file is open");
    return new Set();
  }

  const maps = await navigation.findMaps();
  const wanted = new Set();
  for (const doc of open) {
    for (const file of sourcemap.generatedFilesFor(maps, doc.uri.fsPath)) wanted.add(file.toLowerCase());
  }
  log(`${open.length} Python file(s) open, ${maps.length} map(s) known, ${wanted.size} generated file(s) worth loading`);
  return wanted;
}

/**
 * Hand the next batch of changed files to the language server.
 * `openTextDocument` loads a document without showing it, which is all a server needs to start
 * reporting on it. Each file's previous result is dropped first, so an error that was fixed
 * disappears instead of lingering.
 */
async function drain() {
  timer = undefined;
  if (!vscode.workspace.getConfiguration(CFG_KEY).get("sourceMapDiagnostics", true)) {
    pending.clear();
    return;
  }

  const wanted = await worthLoading();
  const batch = [];
  for (const key of [...pending]) {
    const uri = vscode.Uri.parse(key);
    if (!wanted.has(uri.fsPath.toLowerCase())) { pending.delete(key); continue; }
    if (batch.length >= MAX_PER_PASS) break;
    pending.delete(key);
    batch.push(uri);
  }

  for (const uri of batch) {
    captured.delete(uri.fsPath);
    try {
      held.push(await vscode.workspace.openTextDocument(uri));
    } catch (e) {
      log(`could not load ${uri.fsPath}: ${e}`);
    }
  }
  log(`loaded ${batch.length} generated file(s), ${pending.size} still queued`);
  if (batch.length > 0) publish();

  setTimeout(release, HOLD_MS);
  // What did not fit waits for another pass rather than being dropped.
  if (pending.size > 0) timer = setTimeout(drain, DEBOUNCE_MS);
}

/**
 * Throw away every captured result and load again from scratch.
 * The escape hatch for a build that finished somewhere the watcher could not see, and the
 * first thing to try when the relay is quiet: the output channel then says why.
 */
async function reload() {
  captured.clear();
  published = "";
  navigation.forgetMaps();
  sourcemap.clearCache();
  log("reload requested");
  scheduleLive();
  for (const doc of vscode.workspace.textDocuments) await notifyPythonOpened(doc);
  if (!timer) timer = setTimeout(drain, 0);
}

/**
 * Load what a Python file produced, for when it is opened after the build that wrote it.
 * @param {vscode.TextDocument} doc
 */
async function notifyPythonOpened(doc) {
  if (doc.languageId !== "python" || doc.uri.scheme !== "file") return;
  const maps = await navigation.findMaps();
  const produced = sourcemap.generatedFilesFor(maps, doc.uri.fsPath);
  if (produced.length > 0) notifyGeneratedChanged(produced.map(file => vscode.Uri.file(file)));
}

/** Let VS Code collect the batch again, once the server has had time to look at it. */
function release() {
  held = [];
}

// ─── Registration───────────

/**
 * Start relaying, and stop cleanly on deactivation.
 * Does nothing observable when no build is present: no map, no origin, no diagnostic moved.
 * @param {vscode.ExtensionContext} context
 */
function registerDiagnosticRelay(context) {
  collection = vscode.languages.createDiagnosticCollection(COLLECTION_NAME);
  output = vscode.window.createOutputChannel("StewBeet");
  context.subscriptions.push(
    collection,
    output,
    vscode.commands.registerCommand("stewbeet.refreshDiagnostics", reload),
    vscode.commands.registerCommand("stewbeet.diagnosticsStatus", status),
    vscode.languages.onDidChangeDiagnostics(onDiagnosticsChanged),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration(CFG_KEY)) publish();
    }),
    vscode.workspace.onDidOpenTextDocument(doc => { void notifyPythonOpened(doc); scheduleLive(); }),
    vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.languageId === "python") scheduleLive();
    }),
    { dispose: () => { if (liveTimer) clearTimeout(liveTimer); } },
    { dispose: () => { if (timer) clearTimeout(timer); pending.clear(); release(); } },
  );
  refresh();
  for (const doc of vscode.workspace.textDocuments) void notifyPythonOpened(doc);
  scheduleLive();
}

module.exports = {
  COLLECTION_NAME,
  DEFAULT_DENYLIST,
  ruleOf,
  relocate,
  refresh,
  forget,
  publish,
  notifyGeneratedChanged,
  notifyPythonOpened,
  reload,
  status,
  registerDiagnosticRelay,
};
