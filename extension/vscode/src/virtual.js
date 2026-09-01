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
// Because the projection preserves offsets, positions and every returned range
// are already correct for the Python document and are passed through untouched.

const vscode = require("vscode");
const { findBlockOffsets, findInterpolationSpans } = require("./blocks");
const { SCHEME, project, virtualPath, blockIndexFromPath } = require("./projection");

// ─── Constants──────────────

const CFG_KEY = "StewBeet";

/** Spyglass's own trigger characters for mcfunction, from its registerLanguage call.
 *  Any other set makes completion fire in different places than it does in a real
 *  .mcfunction file. */
const TRIGGER_CHARACTERS = [" ", "[", "=", "!", ",", "{", ":", "/", ".", '"', "'"];

/** Completion items are created by Spyglass, not by us, so VS Code never calls our
 *  resolveCompletionItem for them. Without a resolve count they arrive with no
 *  documentation and no detail. */
const ITEM_RESOLVE_COUNT = 50;

// ─── Block lookup───────────

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

// ─── Content provider───────

const onDidChangeEmitter = new vscode.EventEmitter();

/** Virtual URIs handed out so far, so changes can be announced for them.
 *  @type {Map<string, { sourceUri:string, uri:vscode.Uri }>} */
const served = new Map();

const contentProvider = {
  onDidChange: onDidChangeEmitter.event,

  /** @param {vscode.Uri} uri */
  provideTextDocumentContent(uri) {
    const blockIndex = blockIndexFromPath(uri.path);
    if (blockIndex === undefined) return "";

    const sourceUri = uri.query;
    const doc = vscode.workspace.textDocuments.find(d => d.uri.toString() === sourceUri);
    if (!doc) return "";

    const block = blocksOf(doc)[blockIndex];
    if (!block) return "";

    served.set(uri.toString(), { sourceUri, uri });
    const text = doc.getText();
    return project(text, block.start, block.end, findInterpolationSpans(text, block));
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
    if (entry.sourceUri === key) served.delete(virtualKey);
  }
}

// ─── Forwarding──────────────

/**
 * Ask Spyglass a question about the block under the cursor.
 * Returns undefined when the feature is off, the position is outside a block,
 * or nothing answered, which is also what happens when Spyglass is not installed.
 * @param {string} command  A vscode.execute* built-in command.
 * @param {vscode.TextDocument} doc
 * @param {vscode.Position} position
 * @param {...any} extraArgs
 */
async function forward(command, doc, position, ...extraArgs) {
  if (!vscode.workspace.getConfiguration(CFG_KEY).get("languageFeatures", true)) return undefined;

  const blockIndex = blockAt(doc, position);
  if (blockIndex === undefined) return undefined;

  const uri = virtualUriFor(doc, blockIndex);
  try {
    await vscode.workspace.openTextDocument(uri);
    return await vscode.commands.executeCommand(command, uri, position, ...extraArgs);
  } catch (e) {
    console.debug(`[StewBeet] ${command} forwarding failed`, e);
    return undefined;
  }
}

// ─── Language providers──────

const completionProvider = {
  /**
   * @param {vscode.TextDocument} doc
   * @param {vscode.Position} position
   * @param {vscode.CancellationToken} _token
   * @param {vscode.CompletionContext} context
   */
  provideCompletionItems(doc, position, _token, context) {
    return forward(
      "vscode.executeCompletionItemProvider",
      doc, position, context.triggerCharacter, ITEM_RESOLVE_COUNT,
    );
  },
};

const hoverProvider = {
  /** @param {vscode.TextDocument} doc @param {vscode.Position} position */
  async provideHover(doc, position) {
    const hovers = await forward("vscode.executeHoverProvider", doc, position);
    return hovers && hovers.length ? hovers[0] : undefined;
  },
};

const signatureHelpProvider = {
  /** @param {vscode.TextDocument} doc @param {vscode.Position} position */
  provideSignatureHelp(doc, position) {
    return forward("vscode.executeSignatureHelpProvider", doc, position);
  },
};

const definitionProvider = {
  /** @param {vscode.TextDocument} doc @param {vscode.Position} position */
  provideDefinition(doc, position) {
    return forward("vscode.executeDefinitionProvider", doc, position);
  },
};

// ─── Registration───────────

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
    onDidChangeEmitter,
  );
}

module.exports = {
  TRIGGER_CHARACTERS,
  blockAt,
  virtualUriFor,
  contentProvider,
  forward,
  completionProvider,
  hoverProvider,
  signatureHelpProvider,
  definitionProvider,
  registerVirtualDocuments,
};
