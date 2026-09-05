// @ts-check
"use strict";

// Virtual mcfunction documents, and the request forwarding built on them.
//
// Each mcfunction string block in a Python file is served as its own virtual
// document under the "stewbeet-mcfunction" scheme, whose content is the Python
// buffer with everything outside that block blanked out (see ./projection.js).
// Spyglass's document selector carries no scheme filter, so it attaches to
// those documents exactly as it would to a real .mcfunction file, and answers
// completion, hover, signature help and definition for them.
//
// An interpolation is filled in with what the last build resolved it to, so `function
// {ns}:utils/foo` reaches Spyglass as the path it really is. That is what makes the columns of
// a line differ between the two documents, so every position going out and every range coming
// back is translated with the table the projection returns.

const vscode = require("vscode");
const { findBlockOffsets, findInterpolationSpans } = require("./blocks");
const {
  SCHEME, project, toVirtual, toPython, explainedByMask, crossesSubstitution,
  virtualPath, blockIndexFromPath,
} = require("./projection");
const navigation = require("./navigation");
const sourcemap = require("./sourcemap");

// Constants

const CFG_KEY = "StewBeet";

/** Spyglass's own trigger characters for mcfunction, from its registerLanguage call.
 *  Any other set makes completion fire in different places than it does in a real
 *  .mcfunction file. */
const TRIGGER_CHARACTERS = [" ", "[", "=", "!", ",", "{", ":", "/", ".", '"', "'"];

/** Completion items are created by Spyglass, not by us, so VS Code never calls our
 *  resolveCompletionItem for them. Without a resolve count they arrive with no
 *  documentation and no detail. */
const ITEM_RESOLVE_COUNT = 50;

/** What a block with no substitution uses, so callers never branch on null.
 *  @type {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} */
const NO_SUBSTITUTION = new Map();

// Block lookup

/** Cache of the block scan, keyed by document URI. @type {Map<string, { version:number, blocks:{start:number,end:number}[] }>} */
const blockCache = new Map();

/**
 * The blocks of a document, rescanned only when its version changes.
 * @param {vscode.TextDocument} doc
 */
function blocksOf(doc) {
  const key = doc.uri.toString();
  const cached = blockCache.get(key);
  if (cached && cached.version === doc.version) return cached.blocks;

  const blocks = findBlockOffsets(doc.getText());
  blockCache.set(key, { version: doc.version, blocks });
  return blocks;
}

/**
 * Index of the block containing a position, or undefined when outside every block.
 * @param {vscode.TextDocument} doc
 * @param {vscode.Position} position
 * @returns {number | undefined}
 */
function blockAt(doc, position) {
  const offset = doc.offsetAt(position);
  const index = blocksOf(doc).findIndex(({ start, end }) => offset >= start && offset <= end);
  return index === -1 ? undefined : index;
}

/**
 * URI of the virtual document for one block. The originating document travels in
 * the query rather than the path, because VS Code decodes percent escapes in a
 * path and would corrupt an encoded URI embedded there.
 * @param {vscode.TextDocument} doc
 * @param {number} blockIndex
 */
function virtualUriFor(doc, blockIndex) {
  const baseName = doc.uri.path.split("/").pop() || "embedded";
  return vscode.Uri.from({
    scheme: SCHEME,
    path: virtualPath(blockIndex, baseName),
    query: doc.uri.toString(),
  });
}

// Content provider

const onDidChangeEmitter = new vscode.EventEmitter();

/** Virtual URIs handed out so far, so changes can be announced for them.
 *  @type {Map<string, { sourceUri:string, uri:vscode.Uri }>} */
const served = new Map();

/** One projection per document version and block, shared by the content provider and the
 *  forwarding. Both must agree on the columns to the character: the provider decides what
 *  Spyglass reads, and the forwarding decides where in it a position lands and where a
 *  returned range goes back to. Deriving them separately let them drift, and an untranslated
 *  range does not merely fail, it overwrites the wrong characters.
 *  @type {Map<string, { version:number, text:string, table:typeof NO_SUBSTITUTION, masked:Map<number, {start:number,end:number}[]> }>} */
const projections = new Map();

/** @param {string} sourceUri @param {number} blockIndex */
function projectionKey(sourceUri, blockIndex) {
  return `${sourceUri}#${blockIndex}`;
}

/**
 * The projection of one block, computed once per document version.
 * @param {vscode.TextDocument} doc
 * @param {number} blockIndex
 * @returns {Promise<{ version:number, text:string, table:typeof NO_SUBSTITUTION, masked:Map<number, {start:number,end:number}[]> } | null>}
 */
async function projectionFor(doc, blockIndex) {
  const key = projectionKey(doc.uri.toString(), blockIndex);
  const cached = projections.get(key);
  if (cached && cached.version === doc.version) return cached;

  const block = blocksOf(doc)[blockIndex];
  if (!block) return null;

  // The content range, not the block range: the quotes belong to Python, and handing them to a
  // datapack parser earns a diagnostic saying `"""` is not a command.
  const text = doc.getText();
  const { text: projected, table, masked } = project(
    text, block.contentStart, block.contentEnd,
    findInterpolationSpans(text, block), await generatedFor(doc, block));
  const entry = { version: doc.version, text: projected, table, masked };
  projections.set(key, entry);
  return entry;
}

/**
 * What the build wrote for each Python line of a block, or null when substitution is off.
 * @param {vscode.TextDocument} doc
 * @param {{ start:number, end:number }} block
 * @returns {Promise<Map<number, string> | null>}
 */
async function generatedFor(doc, block) {
  if (!vscode.workspace.getConfiguration(CFG_KEY).get("resolveInterpolations", true)) return null;
  if (doc.uri.scheme !== "file") return null;

  const maps = await navigation.findMaps();
  if (maps.length === 0) return null;
  return sourcemap.generatedText(
    maps, doc.uri.fsPath, doc.positionAt(block.start).line, doc.positionAt(block.end).line);
}

const contentProvider = {
  onDidChange: onDidChangeEmitter.event,

  /** @param {vscode.Uri} uri */
  async provideTextDocumentContent(uri) {
    const blockIndex = blockIndexFromPath(uri.path);
    if (blockIndex === undefined) return "";

    const sourceUri = uri.query;
    const doc = vscode.workspace.textDocuments.find(d => d.uri.toString() === sourceUri);
    if (!doc) return "";

    served.set(uri.toString(), { sourceUri, uri });
    const projection = await projectionFor(doc, blockIndex);
    return projection ? projection.text : "";
  },
};

/** @param {vscode.TextDocument} doc */
function invalidate(doc) {
  const key = doc.uri.toString();
  blockCache.delete(key);
  for (const { sourceUri, uri } of served.values()) {
    if (sourceUri === key) onDidChangeEmitter.fire(uri);
  }
}

/** @param {vscode.TextDocument} doc */
function forget(doc) {
  const key = doc.uri.toString();
  blockCache.delete(key);
  for (const [virtualKey, entry] of served) {
    if (entry.sourceUri !== key) continue;
    served.delete(virtualKey);
    wokenWith.delete(virtualKey);
  }
  for (const projectionEntry of [...projections.keys()]) {
    if (projectionEntry.startsWith(`${key}#`)) projections.delete(projectionEntry);
  }
}

/**
 * Reproject every served document, for when a build changed what the interpolations resolve to.
 * The cache is keyed by document version, and a build changes none of them, so it is dropped
 * outright rather than left to expire.
 */
function reproject() {
  projections.clear();
  wokenWith.clear();
  for (const { uri } of served.values()) onDidChangeEmitter.fire(uri);
}

// Forwarding

/**
 * Ask Spyglass a question about the block under the cursor.
 *
 * The answer comes back with the block's translation table, which every caller needs to put
 * the ranges Spyglass returns back into the Python document. `answer` is undefined when the
 * feature is off, the position is outside a block, or nothing answered, which is also what
 * happens when Spyglass is not installed.
 *
 * @param {string} command  A vscode.execute* built-in command.
 * @param {vscode.TextDocument} doc
 * @param {vscode.Position} position
 * @param {...any} extraArgs
 * @returns {Promise<{ answer: any, table: typeof NO_SUBSTITUTION }>}
 */
async function forward(command, doc, position, ...extraArgs) {
  const nothing = { answer: undefined, table: NO_SUBSTITUTION };
  if (!vscode.workspace.getConfiguration(CFG_KEY).get("languageFeatures", true)) return nothing;

  const blockIndex = blockAt(doc, position);
  if (blockIndex === undefined) return nothing;

  const uri = virtualUriFor(doc, blockIndex);
  try {
    // The projection is computed before the document is opened, so the provider serves from
    // the same cache entry this table comes from.
    const table = (await projectionFor(doc, blockIndex))?.table ?? NO_SUBSTITUTION;
    await vscode.workspace.openTextDocument(uri);
    const virtual = toVirtual({ line: position.line, character: position.character }, table);
    const answer = await vscode.commands.executeCommand(
      command, uri, new vscode.Position(virtual.line, virtual.character), ...extraArgs);
    return { answer, table };
  } catch (e) {
    console.debug(`[StewBeet] ${command} forwarding failed`, e);
    return nothing;
  }
}

// Translating answers

/**
 * A range back in the Python document.
 *
 * Always translates, because a range that only draws something (a hover box, the underline
 * ctrl+click puts under a token) is better drawn approximately than drawn over the wrong
 * characters. Both ends land honestly whenever the range wraps a whole substituted token,
 * which is the case that matters: `simplenergy.data` is 16 columns wide and `{ns}.data` is 9,
 * and translating both ends recovers exactly those 9.
 *
 * @param {any} range
 * @param {typeof NO_SUBSTITUTION} table
 * @returns {any}
 */
function pythonRange(range, table) {
  if (!range) return range;
  const start = toPython(range.start, table);
  const end = toPython(range.end, table);
  return new vscode.Range(start.line, start.character, end.line, end.character);
}

/**
 * A range that will be applied as an edit, or undefined when it overlaps a substituted span.
 *
 * The stricter half of the pair: this one rewrites the author's buffer, so an ambiguous range
 * is dropped rather than approximated. VS Code accepts `{ inserting, replacing }` wherever a
 * completion range is expected, so both shapes are handled.
 *
 * @param {any} range
 * @param {typeof NO_SUBSTITUTION} table
 * @returns {any}
 */
function pythonEditRange(range, table) {
  if (!range) return range;
  if (range.inserting || range.replacing) {
    const inserting = pythonEditRange(range.inserting, table);
    const replacing = pythonEditRange(range.replacing, table);
    return inserting && replacing ? { inserting, replacing } : undefined;
  }
  return crossesSubstitution(range.start, range.end, table) ? undefined : pythonRange(range, table);
}

/**
 * One edit back in the Python document, or undefined when its range cannot be translated.
 * @param {any} edit
 * @param {typeof NO_SUBSTITUTION} table
 */
function pythonEdit(edit, table) {
  if (!edit) return undefined;
  const range = pythonEditRange(edit.range, table);
  return range ? new vscode.TextEdit(range, edit.newText) : undefined;
}

/**
 * Put every edit a completion list carries into the Python document's coordinates.
 *
 * An edit is applied to the author's own buffer the moment they accept the item, so one whose
 * range overlaps a substituted span is dropped rather than guessed at: VS Code then falls back
 * to the word under the cursor, which it computes from the Python document itself.
 *
 * @param {any} list
 * @param {typeof NO_SUBSTITUTION} table
 */
function pythonCompletions(list, table) {
  if (!list || table.size === 0) return list;
  const items = Array.isArray(list) ? list : list.items;
  if (!Array.isArray(items)) return list;

  for (const item of items) {
    item.range = pythonEditRange(item.range, table);
    item.textEdit = pythonEdit(item.textEdit, table);
    if (!Array.isArray(item.additionalTextEdits) || item.additionalTextEdits.length === 0) continue;
    const edits = item.additionalTextEdits.map((/** @type {any} */ e) => pythonEdit(e, table));
    // One dropped edit leaves the rest inconsistent, so the whole set goes.
    item.additionalTextEdits = edits.includes(undefined) ? undefined : edits;
  }
  return list;
}

/**
 * Turn answers pointing back into the virtual document into Python locations.
 *
 * `originSelectionRange` is translated on every answer whatever its target, because it is a
 * range in the document the request came from, not in the one it points at. It is what VS Code
 * underlines under the cursor on ctrl+click, so leaving it in virtual columns underlines the
 * wrong characters even when the jump itself is right.
 *
 * A target pointing at a generated .mcfunction is otherwise left alone; rewriting those is
 * ./navigation.js's job and it needs the original file to look the map up.
 *
 * @param {any} answers
 * @param {typeof NO_SUBSTITUTION} table
 */
function pythonLocations(answers, table) {
  if (!Array.isArray(answers) || table.size === 0) return answers;
  return answers.map(entry => {
    if (entry && entry.originSelectionRange) {
      entry.originSelectionRange = pythonRange(entry.originSelectionRange, table);
    }
    const target = navigation.targetOf(entry);
    if (!target || target.uri.scheme !== SCHEME) return entry;
    return new vscode.Location(vscode.Uri.parse(target.uri.query), pythonRange(target.range, table));
  });
}

// Language providers

const completionProvider = {
  /**
   * @param {vscode.TextDocument} doc
   * @param {vscode.Position} position
   * @param {vscode.CancellationToken} _token
   * @param {vscode.CompletionContext} context
   */
  async provideCompletionItems(doc, position, _token, context) {
    const { answer, table } = await forward(
      "vscode.executeCompletionItemProvider",
      doc, position, context.triggerCharacter, ITEM_RESOLVE_COUNT,
    );
    return pythonCompletions(answer, table);
  },
};

const hoverProvider = {
  /** @param {vscode.TextDocument} doc @param {vscode.Position} position */
  async provideHover(doc, position) {
    const { answer, table } = await forward("vscode.executeHoverProvider", doc, position);
    if (!answer || answer.length === 0) return undefined;
    const hover = answer[0];
    const range = hover.range ? pythonRange(hover.range, table) : undefined;
    return range ? new vscode.Hover(hover.contents, range) : hover;
  },
};

const signatureHelpProvider = {
  /** @param {vscode.TextDocument} doc @param {vscode.Position} position */
  async provideSignatureHelp(doc, position) {
    // Signature help carries no range, so nothing here needs translating back.
    return (await forward("vscode.executeSignatureHelpProvider", doc, position)).answer;
  },
};

const definitionProvider = {
  /** @param {vscode.TextDocument} doc @param {vscode.Position} position */
  async provideDefinition(doc, position) {
    // Spyglass answers with the generated .mcfunction, which is build output nobody edits.
    // The source maps turn that into the write_* call that produced it; without a build there
    // is nothing to turn it into, and its answer is returned unchanged.
    const { answer, table } = await forward("vscode.executeDefinitionProvider", doc, position);
    return navigation.resolve(pythonLocations(answer, table));
  },
};

const referenceProvider = {
  /** @param {vscode.TextDocument} doc @param {vscode.Position} position */
  async provideReferences(doc, position) {
    const { answer, table } = await forward("vscode.executeReferenceProvider", doc, position);
    return navigation.resolve(pythonLocations(answer, table));
  },
};

// Diagnostics from the projection

/** A wake is a round trip to a language server, and a server that never answers must not be
 *  able to stop the next pass from running. */
const WAKE_TIMEOUT_MS = 3000;

/** The projected text each virtual document was last woken with, so a pass only pays for the
 *  blocks whose content actually moved. @type {Map<string, string>} */
const wokenWith = new Map();

/**
 * Give up on a promise rather than wait on it forever.
 * @template T @param {Thenable<T>} work @returns {Promise<T>}
 */
function withTimeout(work) {
  /** @type {NodeJS.Timeout} */
  let timer;
  const expiry = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error("timed out")), WAKE_TIMEOUT_MS);
  });
  return Promise.race([Promise.resolve(work), expiry]).finally(() => clearTimeout(timer));
}

/**
 * Make the language server look at a virtual document.
 *
 * Opening one is not enough, and the difference is the whole reason a block can sit there with
 * an obvious mistake and no squiggle. VS Code hands a document to a language client when
 * something asks a question about it, and lets go of it again once the collection those
 * documents live in fills up. A document in that state is still listed as open and still
 * answers nothing, so `getDiagnostics` on it stays empty and no later pass recovers it.
 *
 * One hover is the cheapest question there is, and answering it is what makes Spyglass parse
 * the document and report on it.
 *
 * @param {vscode.Uri} uri
 * @param {string} text  What the document holds, remembered so an unchanged block is skipped.
 */
async function wake(uri, text) {
  try {
    await withTimeout(vscode.workspace.openTextDocument(uri));
    await withTimeout(vscode.commands.executeCommand(
      "vscode.executeHoverProvider", uri, new vscode.Position(0, 0)));
    wokenWith.set(uri.toString(), text);
  } catch (e) {
    console.debug("[StewBeet] could not wake a virtual document", e);
  }
}

/**
 * What Spyglass says about one Python document's blocks, in the Python document's coordinates.
 *
 * The virtual documents are the honest place to ask. Their lines are in lockstep with the
 * Python, so a diagnostic needs no source map to come home, and it arrives as the author types
 * rather than after a build.
 *
 * Waking is what makes the server look at a document nobody is showing, and it is deliberately
 * not the default: the server answers a wake by publishing, and publishing is what asks for
 * the next pass, so waking on every pass spins. `"changed"` wakes the blocks whose text moved,
 * which is what an edit needs; `"all"` wakes them regardless, which is the only way back from
 * an eviction nothing announced; `"none"` reads what the server has already said.
 *
 * @param {vscode.TextDocument} doc
 * @param {{ wake: "none" | "changed" | "all" }} options
 * @returns {Promise<vscode.Diagnostic[]>}
 */
async function pythonDiagnosticsFor(doc, { wake: waking }) {
  if (!vscode.workspace.getConfiguration(CFG_KEY).get("languageFeatures", true)) return [];

  const blocks = blocksOf(doc);
  const projected = [];
  for (let blockIndex = 0; blockIndex < blocks.length; blockIndex++) {
    const projection = await projectionFor(doc, blockIndex);
    if (projection) projected.push({ uri: virtualUriFor(doc, blockIndex), projection });
  }

  // All at once: each wake is a round trip, and seventeen of them in a row is the difference
  // between reacting to a keystroke and not.
  if (waking !== "none") {
    await Promise.all(projected
      .filter(({ uri, projection }) => waking === "all" || wokenWith.get(uri.toString()) !== projection.text)
      .map(({ uri, projection }) => wake(uri, projection.text)));
  }

  const moved = [];
  for (const { uri, projection } of projected) {
    for (const diagnostic of vscode.languages.getDiagnostics(uri)) {
      if (explainedByMask(diagnostic.range.start, projection.masked)) continue;
      const start = toPython(diagnostic.range.start, projection.table);
      const end = toPython(diagnostic.range.end, projection.table);
      const copy = new vscode.Diagnostic(
        new vscode.Range(start.line, start.character, end.line, end.character),
        diagnostic.message, diagnostic.severity);
      copy.code = diagnostic.code;
      copy.source = diagnostic.source;
      moved.push(copy);
    }
  }
  return moved;
}

// Registration

/** @param {vscode.ExtensionContext} context */
function registerVirtualDocuments(context) {
  context.subscriptions.push(
    vscode.workspace.registerTextDocumentContentProvider(SCHEME, contentProvider),
    vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.languageId === "python") invalidate(e.document);
    }),
    vscode.workspace.onDidCloseTextDocument(doc => {
      if (doc.languageId === "python") forget(doc);
    }),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration(`${CFG_KEY}.resolveInterpolations`)) reproject();
    }),
    onDidChangeEmitter,
  );
}

module.exports = {
  TRIGGER_CHARACTERS,
  SCHEME,
  blocksOf,
  blockAt,
  pythonDiagnosticsFor,
  virtualUriFor,
  contentProvider,
  forward,
  reproject,
  pythonCompletions,
  completionProvider,
  hoverProvider,
  signatureHelpProvider,
  definitionProvider,
  referenceProvider,
  registerVirtualDocuments,
};
