// @ts-check
"use strict";

const vscode = require("vscode");
const { findBlockOffsets } = require("./blocks");

// ─── Constants ───────────────────────────────────────────────────────────────

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
 * Find all mcfunction string blocks in a Python document.
 * Scanning logic lives in ./blocks.js (pure, unit-tested).
 * @param {vscode.TextDocument} doc
 * @returns {{ startLine:number, startChar:number, endLine:number, endChar:number, multiline:boolean }[]}
 */
function findBlocks(doc) {
  return findBlockOffsets(doc.getText()).map(({ start, end }) => {
    const startPos = doc.positionAt(start);
    const endPos   = doc.positionAt(end);
    return {
      startLine: startPos.line,
      startChar: startPos.character,
      endLine:   endPos.line,
      endChar:   endPos.character,
      multiline: endPos.line > startPos.line,
    };
  });
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
