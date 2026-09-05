// @ts-check
"use strict";

// A measurement, not an assertion: what the live diagnostics path actually sees in the flow a
// real editor produces, where nothing ever opens a virtual document on purpose.
//
//   SB_TESTS=probe node test/integration/run.js
//
// It answers three questions the unit tests cannot:
//   1. Do the virtual documents the relay opens stay open?
//   2. Does Spyglass report on them without anybody asking a question first?
//   3. Does loading generated files evict them, which is what a rebuild does?

const vscode = require("vscode");
const path = require("node:path");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** @param {vscode.TextDocument} py @param {number} blockIndex */
function virtualUriFor(py, blockIndex) {
  return vscode.Uri.from({
    scheme: "stewbeet-mcfunction",
    path: `/${blockIndex}/demo.py.mcfunction`,
    query: py.uri.toString(),
  });
}

/** @param {vscode.TextDocument} py */
function snapshot(py) {
  const open = [];
  const diagnostics = [];
  for (let i = 0; i < 4; i++) {
    const uri = virtualUriFor(py, i);
    if (vscode.workspace.textDocuments.some(d => d.uri.toString() === uri.toString())) open.push(i);
    const found = vscode.languages.getDiagnostics(uri) || [];
    if (found.length > 0) diagnostics.push(`${i}: ${found.map(d => `${d.range.start.line}:${d.range.start.character}`).join(",")}`);
  }
  const ours = (vscode.languages.getDiagnostics(py.uri) || [])
    .filter(d => String(d.source || "").startsWith("stewbeet"));
  return {
    virtualDocsOpen: open,
    virtualDiagnostics: diagnostics,
    onPython: ours.map(d => `${d.range.start.line}:${d.range.start.character} ${d.message.slice(0, 30)}`),
  };
}

exports.run = async () => {
  const results = { checks: [] };
  const note = (k, v) => { results[k] = v; results.checks.push(`${k} = ${JSON.stringify(v)}`); };

  try {
    await sleep(5000);
    const stewbeet = vscode.extensions.getExtension("stoupy.stewbeet");
    if (stewbeet && !stewbeet.isActive) await stewbeet.activate();

    const root = vscode.workspace.workspaceFolders[0].uri.fsPath;

    // Warm Spyglass up on a real file, the way opening any datapack file does.
    const real = vscode.Uri.file(path.join(root, "data", "probe", "function", "beta.mcfunction"));
    await vscode.workspace.openTextDocument(real);
    for (let i = 0; i < 40; i++) {
      const list = await vscode.commands.executeCommand(
        "vscode.executeCompletionItemProvider", real, new vscode.Position(0, 0), undefined, 50);
      if (list && list.items && list.items.length > 0) { note("spyglassReadyAfterSeconds", i * 2); break; }
      await sleep(2000);
    }

    // From here on, exactly what an author does: open the Python file and look at it.
    const py = await vscode.workspace.openTextDocument(vscode.Uri.file(path.join(root, "demo.py")));
    await vscode.window.showTextDocument(py, { preview: false });

    for (const seconds of [3, 8, 15, 25]) {
      await sleep(seconds * 1000 - (seconds === 3 ? 0 : 0));
      note(`passive_after_${seconds}s`, snapshot(py));
    }

    note("passive_status", await vscode.commands.executeCommand("stewbeet.diagnosticsStatus"));

    // Now an edit, which is what makes the author say "it does not react".
    const edit = new vscode.WorkspaceEdit();
    edit.insert(py.uri, new vscode.Position(21, 0), "say typed\n");
    await vscode.workspace.applyEdit(edit);
    await sleep(6000);
    note("afterEdit", snapshot(py));

    // Does asking a question wake it up? This is the difference between the harness and the editor.
    await vscode.commands.executeCommand(
      "vscode.executeCompletionItemProvider", py.uri, new vscode.Position(21, 5), " ", 50);
    await sleep(6000);
    note("afterCompletionAsked", snapshot(py));

    // A rebuild loads generated files. VS Code holds at most 50 documents opened this way.
    const filler = [];
    for (let i = 0; i < 60; i++) {
      filler.push(await vscode.workspace.openTextDocument({ content: `# filler ${i}`, language: "plaintext" }));
    }
    await sleep(4000);
    note("afterSixtyDocumentsOpened", snapshot(py));

    // Does it come back on its own? This is the difference between a slow path and a dead one.
    await sleep(15000);
    note("recovery_after15s", snapshot(py));
    note("recovery_status", await vscode.commands.executeCommand("stewbeet.diagnosticsStatus"));

    const edit2 = new vscode.WorkspaceEdit();
    edit2.insert(py.uri, new vscode.Position(0, 0), "# touched" + String.fromCharCode(10));
    await vscode.workspace.applyEdit(edit2);
    await sleep(10000);
    note("recovery_afterEdit", snapshot(py));

    await vscode.commands.executeCommand("stewbeet.refreshDiagnostics");
    await sleep(10000);
    note("recovery_afterRefreshCommand", snapshot(py));

    // Which request is enough to make the server look at a document nobody is showing?
    // Cheapest first: the answer decides what the diagnostics pass will send.
    for (let i = 0; i < 4; i++) {
      await vscode.commands.executeCommand("vscode.executeHoverProvider", virtualUriFor(py, i), new vscode.Position(0, 0));
    }
    await sleep(6000);
    note("wakeBy_hover", snapshot(py));

    for (let i = 0; i < 4; i++) {
      await vscode.commands.executeCommand("vscode.executeDocumentSymbolProvider", virtualUriFor(py, i));
    }
    await sleep(6000);
    note("wakeBy_documentSymbol", snapshot(py));

    for (let i = 0; i < 4; i++) {
      await vscode.commands.executeCommand(
        "vscode.executeCompletionItemProvider", virtualUriFor(py, i), new vscode.Position(0, 0), undefined, 1);
    }
    await sleep(6000);
    note("wakeBy_completion", snapshot(py));

    note("final_status", await vscode.commands.executeCommand("stewbeet.diagnosticsStatus"));
    note("VERDICT", "PASS (measurement only)");
  } catch (e) {
    results.error = String(e && e.stack ? e.stack : e);
    note("VERDICT", "FAIL");
  }

  require("node:fs").writeFileSync(process.env.SB_OUT, JSON.stringify(results, null, 2));
};
