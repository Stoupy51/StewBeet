// @ts-check
"use strict";

const vscode = require("vscode");

// ─── Constants ───────────────────────────────────────────────────────────────

const FUNC_RE = /\b(write_function|write_versioned_function|write_scheduled_function|write_load_file|write_unload_file|write_tick_file)\s*\(/g;

/** Functions where the mcfunction content is the 2nd argument (after a path). */
const FUNCS_2ND_ARG = new Set([
  "write_function",
  "write_versioned_function",
  "write_scheduled_function",
]);

const CFG_KEY = "StewBeet";

// ─── Decoration types (recreated on config change) ───────────────────────────

/** @type {{ block: vscode.TextEditorDecorationType, first: vscode.TextEditorDecorationType, last: vscode.TextEditorDecorationType, single: vscode.TextEditorDecorationType } | null} */
let decos = null;

/**
 * Create the four decoration roles needed to draw a unified block rectangle.
 * Multi-line blocks use first/block/last (isWholeLine) so the bg spans edge-to-edge.
 * Single-line blocks use a precise range so the box wraps only the string.
 * 
 * @param {string} bg  Background color for the block.
 * @param {string} border  Border color for the block.
 * @param {string} borderWidth  Border width for the block (e.g. "2px").
 */
function createDecos(bg, border, borderWidth) {
  /**
   * @param {string} style Border style for the block (e.g. "solid none solid none").
   * @param {string} radius Border radius for the block (e.g. "4px 4px 0 0").
   */
  const multi = (style, radius) => vscode.window.createTextEditorDecorationType({
    backgroundColor: bg,
    isWholeLine: true,
    borderColor: border,
    borderStyle: style,
    borderWidth,
    borderRadius: radius,
  });
  return {
    first:  multi("solid solid none solid", "4px 4px 0 0"),
    block:  multi("none solid none solid",  "0"),
    last:   multi("none solid solid solid", "0 0 4px 4px"),
    single: vscode.window.createTextEditorDecorationType({
      backgroundColor: bg,
      isWholeLine: false,
      borderColor: border,
      borderStyle: "solid",
      borderWidth,
      borderRadius: "4px",
    }),
  };
}

function disposeDecos() {
  if (decos) {
    Object.values(decos).forEach(d => d.dispose());
    decos = null;
  }
}

function refreshDecos() {
  disposeDecos();
  const cfg = vscode.workspace.getConfiguration(CFG_KEY);
  if (!cfg.get("enableBlockDecorations", true)) return;
  decos = createDecos(
    cfg.get("backgroundColor", "rgba(80,40,0,0.15)"),
    cfg.get("borderColor",     "rgba(200,120,30,0.30)"),
    cfg.get("borderWidth",     "2px"),
  );
}

// ─── Extension lifecycle ─────────────────────────────────────────────────────

/** @param {vscode.ExtensionContext} context */
function activate(context) {
  refreshDecos();

  const refresh = () => {
    if (vscode.window.activeTextEditor) updateDecorations(vscode.window.activeTextEditor);
  };
  refresh();

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(editor => { if (editor) updateDecorations(editor); }),
    vscode.workspace.onDidChangeTextDocument(e => {
      const editor = vscode.window.activeTextEditor;
      if (editor && e.document === editor.document) updateDecorations(editor);
    }),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration(CFG_KEY)) { refreshDecos(); refresh(); }
    }),
  );
}

function deactivate() { disposeDecos(); }

// ─── Block detection ─────────────────────────────────────────────────────────

/**
 * Skip past the first argument of a write_* call (the path), stopping just
 * after the separating comma. Handles nested parens/brackets and strings.
 * Returns the index of the first non-whitespace character after the comma, or -1.
 * @param {string} text
 * @param {number} start  Index just after the opening '(' of the call.
 */
function skipFirstArg(text, start) {
  let i = start;
  let depth = 0;

  while (i < text.length) {
    const c = text[i];

    if (c === "(" || c === "[" || c === "{") { depth++; i++; continue; }
    if (c === ")" || c === "]" || c === "}") {
      if (depth === 0) return -1;
      depth--; i++; continue;
    }
    if (depth === 0 && c === ",") {
      i++;
      while (i < text.length && /[ \t\r\n]/.test(text[i])) i++;
      return i;
    }

    // Skip over string literals so their commas/brackets are ignored.
    if (c === '"' || c === "'") {
      const triple = c.repeat(3);
      if (text.slice(i, i + 3) === triple) {
        i += 3;
        while (i < text.length && text.slice(i, i + 3) !== triple) i++;
        i += 3;
      } else {
        i++;
        while (i < text.length && text[i] !== c && text[i] !== "\n") {
          if (text[i] === "\\") i++;
          i++;
        }
        i++;
      }
      continue;
    }

    i++;
  }
  return -1;
}

/**
 * Read the opening quote (optionally preceded by f/F) at position i,
 * skipping leading whitespace.
 * Returns { quoteStyle, quoteStart, contentStart } or null.
 * quoteStart includes the 'f' prefix if present.
 * @param {string} text
 * @param {number} i
 */
function readOpeningQuote(text, i) {
  while (i < text.length && /[ \t\r\n]/.test(text[i])) i++;
  const start = i;
  if (i < text.length && (text[i] === "f" || text[i] === "F")) i++;
  if (i >= text.length) return null;
  for (const qs of ['"""', "'''", '"', "'"]) {
    if (text.slice(i, i + qs.length) === qs) {
      return { quoteStyle: qs, quoteStart: start, contentStart: i + qs.length };
    }
  }
  return null;
}

/**
 * Find the index of the closing quote, skipping escaped characters for
 * single-line styles.
 * @param {string} text
 * @param {string} quoteStyle
 * @param {number} from
 */
function findClosingQuote(text, quoteStyle, from) {
  if (quoteStyle === '"""' || quoteStyle === "'''") {
    return text.indexOf(quoteStyle, from);
  }
  let i = from;
  while (i < text.length) {
    if (text[i] === quoteStyle) return i;
    if (text[i] === "\\") i += 2;
    else i++;
  }
  return -1;
}

/**
 * Find all mcfunction string blocks in a Python document.
 * @param {vscode.TextDocument} doc
 * @returns {{ startLine:number, startChar:number, endLine:number, endChar:number, multiline:boolean }[]}
 */
function findBlocks(doc) {
  const text = doc.getText();
  const blocks = [];

  FUNC_RE.lastIndex = 0;
  let m;
  while ((m = FUNC_RE.exec(text)) !== null) {
    const afterOpen = m.index + m[0].length;

    let contentIdx;
    if (FUNCS_2ND_ARG.has(m[1])) {
      contentIdx = skipFirstArg(text, afterOpen);
      if (contentIdx === -1) continue;
    } else {
      contentIdx = afterOpen;
    }

    const opening = readOpeningQuote(text, contentIdx);
    if (!opening) continue;

    const closeIdx = findClosingQuote(text, opening.quoteStyle, opening.contentStart);
    if (closeIdx === -1) continue;

    const startPos = doc.positionAt(opening.quoteStart);
    const endPos   = doc.positionAt(closeIdx + opening.quoteStyle.length);

    blocks.push({
      startLine: startPos.line,
      startChar: startPos.character,
      endLine:   endPos.line,
      endChar:   endPos.character,
      multiline: endPos.line > startPos.line,
    });
  }

  return blocks;
}

// ─── Decoration rendering ─────────────────────────────────────────────────────

/** @param {vscode.TextEditor} editor */
function updateDecorations(editor) {
  // Clear if disabled, not python, or no decos
  if (!editor || editor.document.languageId !== "python" || !decos) {
    if (decos) Object.values(decos).forEach(d => editor?.setDecorations(d, []));
    return;
  }

  const rFirst = [], rBlock = [], rLast = [], rSingle = [];

  for (const { startLine, startChar, endLine, endChar, multiline } of findBlocks(editor.document)) {
    if (!multiline) {
      rSingle.push(new vscode.Range(startLine, startChar, endLine, endChar));
    } else {
      rFirst.push(new vscode.Range(startLine, 0, startLine, 0));
      for (let l = startLine + 1; l < endLine; l++) rBlock.push(new vscode.Range(l, 0, l, 0));
      rLast.push(new vscode.Range(endLine, 0, endLine, 0));
    }
  }

  editor.setDecorations(decos.first,  rFirst);
  editor.setDecorations(decos.block,  rBlock);
  editor.setDecorations(decos.last,   rLast);
  editor.setDecorations(decos.single, rSingle);
}

module.exports = { activate, deactivate };
