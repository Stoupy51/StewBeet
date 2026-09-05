// @ts-check
"use strict";

// The same measurement as ./probe.js, run against a real pack instead of the fixture.
//
//   SB_TESTS=simplenergy SB_WORKSPACE=d:/advanced_desktop/SimplEnergy \
//   SB_GUARD=d:/advanced_desktop/SimplEnergy/src/utils/machines.py node test/integration/run.js
//
// A fixture with four blocks and three generated files answers none of the questions a pack of
// 270 functions and 117 source maps raises. This types a typo into a real file, times how long
// the squiggle takes to appear, types the fix, and times how long it takes to go.

const vscode = require("vscode");
const path = require("node:path");
const fs = require("node:fs");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** Editor line 245, 0-based. */
const TYPO_LINE = 244;
const CORRECT = "execute store result score #height {ns}.data run data get entity @s Pos[1]";
const BROKEN = "execute store reslt score #height {ns}.data run data get entity @s Pos[1]";

/** @param {vscode.TextDocument} doc */
function ours(doc) {
  return (vscode.languages.getDiagnostics(doc.uri) || [])
    .filter(d => String(d.source || "").startsWith("stewbeet"));
}

/** @param {vscode.TextDocument} doc */
function onTypoLine(doc) {
  return ours(doc).filter(d => d.range.start.line === TYPO_LINE);
}

/**
 * How long until a condition holds, or -1 if it never does.
 * @param {() => boolean} condition
 */
async function timeUntil(condition, limitMs = 40000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < limitMs) {
    if (condition()) return Date.now() - startedAt;
    await sleep(250);
  }
  return -1;
}

/** @param {vscode.TextDocument} doc @param {string} text */
async function setLine(doc, text) {
  const edit = new vscode.WorkspaceEdit();
  edit.replace(doc.uri, doc.lineAt(TYPO_LINE).range, text);
  await vscode.workspace.applyEdit(edit);
}

exports.run = async () => {
  const results = { checks: [] };
  const failures = [];
  const note = (k, v) => { results[k] = v; results.checks.push(`${k} = ${JSON.stringify(v)}`); };
  const expect = (name, ok, detail) => {
    note(name, ok ? "PASS" : `FAIL ${detail === undefined ? "" : JSON.stringify(detail)}`);
    if (!ok) failures.push(name);
  };

  try {
    await sleep(5000);
    const stewbeet = vscode.extensions.getExtension("stoupy.stewbeet");
    if (stewbeet && !stewbeet.isActive) await stewbeet.activate();

    const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const file = path.join(root, "src", "utils", "machines.py");
    note("workspace", root);

    // Spyglass lists the whole pack before it answers anything, and on this one that is slow.
    const anyGenerated = path.join(root, "build", "datapack", "data", "simplenergy",
      "function", "advancements", "first_join.mcfunction");
    let ready = -1;
    if (fs.existsSync(anyGenerated)) {
      await vscode.workspace.openTextDocument(vscode.Uri.file(anyGenerated));
      const startedAt = Date.now();
      for (let i = 0; i < 60; i++) {
        const list = await vscode.commands.executeCommand("vscode.executeCompletionItemProvider",
          vscode.Uri.file(anyGenerated), new vscode.Position(0, 0), undefined, 5);
        if (list && list.items && list.items.length > 0) { ready = Date.now() - startedAt; break; }
        await sleep(2000);
      }
    }
    note("spyglassReadyMs", ready);

    const py = await vscode.workspace.openTextDocument(vscode.Uri.file(file));
    await vscode.window.showTextDocument(py, { preview: false });
    note("blocksInFile", (await vscode.commands.executeCommand("stewbeet.diagnosticsStatus")) && undefined);

    const firstMs = await timeUntil(() => ours(py).length > 0);
    note("firstDiagnosticsAfterMs", firstMs);
    note("statusAfterOpen", await vscode.commands.executeCommand("stewbeet.diagnosticsStatus"));
    note("totalOnFile", ours(py).length);
    note("onTypoLineWhileCorrect", onTypoLine(py).map(d => `${d.range.start.character}: ${d.message.slice(0, 45)}`));

    expect("the correct line is not flagged", onTypoLine(py).length === 0,
      onTypoLine(py).map(d => d.message.slice(0, 60)));

    // Break it, exactly as the author did.
    await setLine(py, BROKEN);
    const appearedMs = await timeUntil(() => onTypoLine(py).length > 0);
    note("typoAppearedAfterMs", appearedMs);
    note("typoDiagnostics", onTypoLine(py).map(d => `${d.range.start.character}: ${d.message.slice(0, 45)}`));
    expect("the typo is reported", appearedMs >= 0, appearedMs);

    // Fix it. This is the half that stayed frozen.
    await setLine(py, CORRECT);
    const clearedMs = await timeUntil(() => onTypoLine(py).length === 0);
    note("typoClearedAfterMs", clearedMs);
    note("stillOnTypoLine", onTypoLine(py).map(d => `${d.range.start.character}: ${d.message.slice(0, 45)}`));
    expect("fixing the line clears the error", clearedMs >= 0,
      onTypoLine(py).map(d => d.message.slice(0, 60)));

    note("finalStatus", await vscode.commands.executeCommand("stewbeet.diagnosticsStatus"));
    note("finalTotalOnFile", ours(py).length);
    note("everythingOnFile", ours(py).map(d => `${d.range.start.line + 1}:${d.range.start.character} ${d.message.slice(0, 60)}`));

    // Nothing changing must cost nothing.
    const before = (await vscode.commands.executeCommand("stewbeet.diagnosticsStatus")).livePasses;
    await sleep(15000);
    const after = (await vscode.commands.executeCommand("stewbeet.diagnosticsStatus")).livePasses;
    note("idlePasses", after - before);
    expect("the relay is quiet while nothing changes", after - before <= 4, after - before);

    note("VERDICT", failures.length === 0 ? "PASS" : `FAIL: ${failures.join(", ")}`);
  } catch (e) {
    results.error = String(e && e.stack ? e.stack : e);
    note("VERDICT", "FAIL");
  }

  fs.writeFileSync(process.env.SB_OUT, JSON.stringify(results, null, 2));
};
