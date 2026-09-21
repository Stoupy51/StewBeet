// @ts-check
"use strict";

// Every diagnostic the relay puts on a real project's Python, one file at a time.
//
//   SB_TESTS=sweep SB_WORKSPACE=d:/advanced_desktop/StoupGun node test/integration/run.js
//
// A measurement rather than a set of assertions. A pack that builds cleanly has no command
// mistakes, so nearly everything this lists is the extension misreading its own input: a block
// missed or cut short, a column that did not come home, padding reported as a missing argument.
// SB_FILES narrows the run to a comma-separated list of paths relative to the workspace.

const vscode = require("vscode");
const path = require("node:path");
const fs = require("node:fs");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** A file worth opening: anything that could hold a block. */
const MAY_HOLD_BLOCKS = /write_\w+\s*\(|McFunction|Function\s*\(/;

/** @param {string} dir @returns {string[]} */
function pythonFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return entry.name.startsWith(".") ? [] : pythonFiles(full);
    return entry.name.endsWith(".py") && MAY_HOLD_BLOCKS.test(fs.readFileSync(full, "utf8")) ? [full] : [];
  });
}

/** @param {vscode.Uri} uri */
function ours(uri) {
  return (vscode.languages.getDiagnostics(uri) || []).filter(d => String(d.source || "").startsWith("stewbeet"));
}

/** Wait until the relay has said the same thing for `quietMs`, or `limitMs` runs out. @param {vscode.Uri} uri */
async function settle(uri, quietMs = 2500, limitMs = 20000) {
  const startedAt = Date.now();
  let last = "";
  let since = Date.now();
  while (Date.now() - startedAt < limitMs) {
    const now = JSON.stringify(ours(uri).map(d => [d.range.start.line, d.range.start.character, d.message]));
    if (now !== last) { last = now; since = Date.now(); }
    else if (Date.now() - since >= quietMs && Date.now() - startedAt > 4000) return;
    await sleep(250);
  }
}

exports.run = async () => {
  const results = { checks: [], findings: [] };
  const note = (k, v) => { results[k] = v; results.checks.push(`${k} = ${JSON.stringify(v)}`); };

  try {
    await sleep(5000);
    const stewbeet = vscode.extensions.getExtension("stoupy.stewbeet");
    if (stewbeet && !stewbeet.isActive) await stewbeet.activate();

    const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const files = process.env.SB_FILES
      ? process.env.SB_FILES.split(",").map(f => path.join(root, f))
      : pythonFiles(path.join(root, "src"));
    note("files", files.length);

    // Spyglass lists the whole pack before it answers anything.
    const any = pythonFiles(path.join(root, "src"))[0];
    await vscode.window.showTextDocument(await vscode.workspace.openTextDocument(vscode.Uri.file(any)));
    for (let i = 0; i < 90; i++) {
      const status = await vscode.commands.executeCommand("stewbeet.diagnosticsStatus");
      if (status && status.livePasses > 0) break;
      await sleep(2000);
    }

    for (const file of files) {
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(file));
      await vscode.window.showTextDocument(doc, { preview: false });
      await vscode.commands.executeCommand("stewbeet.refreshDiagnostics");
      await settle(doc.uri);
      for (const d of ours(doc.uri)) {
        results.findings.push({
          at: `${path.relative(root, file)}:${d.range.start.line + 1}:${d.range.start.character + 1}`,
          message: d.message.slice(0, 120),
          text: doc.lineAt(d.range.start.line).text.trim().slice(0, 200),
        });
      }
      await vscode.commands.executeCommand("workbench.action.closeAllEditors");
    }

    note("findingCount", results.findings.length);
    note("VERDICT", "PASS (measurement)");
  } catch (e) {
    results.error = String(e && e.stack ? e.stack : e);
    note("VERDICT", "FAIL");
  }

  fs.writeFileSync(process.env.SB_OUT, JSON.stringify(results, null, 2));
};
