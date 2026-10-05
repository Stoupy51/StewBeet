// @ts-check
"use strict";

// The colours Spyglass gives a bolt file's commands.
//
// A bolt file is not `mcfunction` to Spyglass, so on its own it colours none of it. Each run of
// commands already reaches Spyglass as a virtual document for completion and diagnostics, and its
// semantic tokens come back the same way, through the same table. The commands then look as they
// do in a `.mcfunction` Spyglass reads, and the Python around them keeps the grammar's colours.
//
// A token over text the projection changed is dropped, and the grammar's colour stays there:
// Spyglass coloured the stand-in, a value bolt computed or a mask, not what the author wrote.
//
// The provider is registered with Spyglass's own legend, read from Spyglass once it answers,
// so a type Spyglass adds needs nothing here.

const { toPython, crossesSubstitution } = require("./projection");

// Required lazily, so the translation below stays loadable under plain `node --test`.
/** @returns {typeof import("vscode")} */
function api() {
  return require("vscode");
}

/** How often to ask again for a legend while Spyglass starts, which takes minutes on a first run. */
const LEGEND_RETRY_MS = 3000;
const LEGEND_RETRIES = 40;

/** Spyglass answers nothing for a document it has not checked yet, so an empty answer is asked again this many times per document. */
const TOKEN_RETRIES = 3;
const TOKEN_RETRY_MS = 1500;

// Translation (pure)

/**
 * Spyglass's tokens for one virtual document, moved to the source document.
 *
 * A token overlapping a mask or a substituted value is dropped, and so is an `error` token at or
 * after a mask on its line, which is the parser losing its way on the stand-in. A token past the
 * end of its source line is the `\` a continued command was given.
 *
 * @param {ArrayLike<number>} data  The relative encoding the semantic tokens API returns.
 * @param {{ table: Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>, masked: Map<number, { start:number, end:number }[]> }} projection
 * @param {number[]} lineLengths  Length of each source line.
 * @param {number} errorType  Index of `error` in Spyglass's legend, -1 when it has none.
 * @returns {[number, number, number, number, number][]}  Line, character, length, type and modifiers, in source columns.
 */
function tokensBack(data, { table, masked }, lineLengths, errorType) {
  /** @type {[number, number, number, number, number][]} */
  const back = [];
  let line = 0;
  let character = 0;
  for (let i = 0; i + 4 < data.length; i += 5) {
    character = data[i] === 0 ? character + data[i + 1] : data[i + 1];
    line += data[i];
    const [length, type, modifiers] = [data[i + 2], data[i + 3], data[i + 4]];
    const runs = masked.get(line) ?? [];
    if (runs.some(run => character < run.end && character + length > run.start)) continue;
    if (type === errorType && runs.some(run => character >= run.start)) continue;
    const start = { line, character };
    const end = { line, character: character + length };
    if (crossesSubstitution(start, end, table)) continue;
    const from = toPython(start, table);
    const to = toPython(end, table);
    if (to.character > (lineLengths[line] ?? 0)) continue;
    back.push([from.line, from.character, to.character - from.character, type, modifiers]);
  }
  return back;
}

// Provider

/**
 * Colour the commands of every bolt document with Spyglass's tokens, once Spyglass has a legend to give.
 *
 * @param {import("vscode").ExtensionContext} context
 * @param {import("vscode").Event<void>} builds  Fired once a new build's maps are read, which changes what the commands resolve to.
 */
function registerSemanticTokens(context, builds) {
  const vscode = api();
  const virtual = require("./virtual");
  const changed = new vscode.EventEmitter();
  /** What each block answered, by `<source uri>#<block>`, against the text it answered for. @type {Map<string, { text: string, back: [number, number, number, number, number][] }>} */
  const answered = new Map();
  /** Empty answers asked again, per source document. @type {Map<string, number>} */
  const retried = new Map();
  let errorType = -1;
  let legendAsked = 0;
  /** @type {import("vscode").Disposable | null} */
  let registration = null;

  /** @param {import("vscode").TextDocument} doc */
  async function answersFor(doc) {
    const lengths = Array.from({ length: doc.lineCount }, (_, line) => doc.lineAt(line).text.length);
    return Promise.all(virtual.blocksOf(doc).map(async (/** @type {any} */ _, /** @type {number} */ index) => {
      const projection = await virtual.projectionFor(doc, index);
      if (!projection) return [];
      const uri = virtual.virtualUriFor(doc, index);
      const key = `${doc.uri.toString()}#${index}`;
      const cached = answered.get(key);
      if (cached && cached.text === projection.text) return cached.back;
      await vscode.workspace.openTextDocument(uri);
      /** @type {any} */
      const tokens = await vscode.commands.executeCommand("vscode.provideDocumentSemanticTokens", uri);
      if (!tokens?.data?.length) return null;
      const back = tokensBack(tokens.data, projection, lengths, errorType);
      answered.set(key, { text: projection.text, back });
      return back;
    }));
  }

  /** @param {import("vscode").TextDocument} doc */
  function askAgain(doc) {
    const key = doc.uri.toString();
    const count = retried.get(key) ?? 0;
    if (count >= TOKEN_RETRIES) return;
    retried.set(key, count + 1);
    setTimeout(() => changed.fire(undefined), TOKEN_RETRY_MS);
  }

  const provider = {
    onDidChangeSemanticTokens: changed.event,
    /** @param {import("vscode").TextDocument} doc */
    async provideDocumentSemanticTokens(doc) {
      const builder = new vscode.SemanticTokensBuilder();
      if (!vscode.workspace.getConfiguration("StewBeet").get("languageFeatures", true)) return builder.build();
      const answers = await answersFor(doc);
      if (answers.includes(null)) askAgain(doc);
      for (const token of answers.flatMap(answer => answer ?? [])) builder.push(...token);
      return builder.build();
    },
  };

  /** @param {import("vscode").TextDocument | undefined} doc */
  async function register(doc) {
    if (registration || !doc || doc.languageId !== "bolt" || virtual.blocksOf(doc).length === 0) return;
    const uri = virtual.virtualUriFor(doc, 0);
    await virtual.projectionFor(doc, 0);
    await vscode.workspace.openTextDocument(uri);
    /** @type {any} */
    const legend = await vscode.commands.executeCommand("vscode.provideDocumentSemanticTokensLegend", uri);
    if (registration) return;
    if (!legend?.tokenTypes?.length) {
      if (legendAsked++ < LEGEND_RETRIES) setTimeout(() => register(vscode.window.activeTextEditor?.document), LEGEND_RETRY_MS);
      return;
    }
    errorType = legend.tokenTypes.indexOf("error");
    registration = vscode.languages.registerDocumentSemanticTokensProvider(
      { language: "bolt" }, provider, new vscode.SemanticTokensLegend(legend.tokenTypes, legend.tokenModifiers));
    context.subscriptions.push(registration);
  }

  context.subscriptions.push(
    changed,
    vscode.window.onDidChangeActiveTextEditor(editor => register(editor?.document)),
    vscode.workspace.onDidOpenTextDocument(register),
    vscode.workspace.onDidCloseTextDocument(doc => {
      retried.delete(doc.uri.toString());
      for (const key of [...answered.keys()]) if (key.startsWith(`${doc.uri.toString()}#`)) answered.delete(key);
    }),
    builds(() => {
      retried.clear();
      changed.fire(undefined);
    }),
  );
  register(vscode.window.activeTextEditor?.document);
}

module.exports = { tokensBack, registerSemanticTokens };
