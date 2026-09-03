// @ts-check
"use strict";

// End-to-end check that the extension's forwarded providers answer inside
// StewBeet mcfunction blocks. Runs inside a VS Code extension host with the
// real extension and the real Spyglass installed; see ./README.md to launch it.
//
// It doubles as the regression guard for the assumption the whole design rests
// on: Spyglass's document selector carries no scheme filter, so it attaches to
// our virtual documents. If a future Spyglass release adds one, every provider
// silently stops answering and only this test notices.

const vscode = require("vscode");
const fs = require("node:fs");
const path = require("node:path");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const label = (it) => (typeof it.label === "string" ? it.label : it.label && it.label.label) || "";

// demo.py, 0-based. Line 3 is "execute as @a run say hi", line 4 "function probe:alpha".
const IN_COMMAND = new vscode.Position(3, "execute as @a run ".length);
const ON_SELECTOR = new vscode.Position(3, "execute as @a".length - 1);
const IN_PATH = new vscode.Position(4, "function probe:".length);
const ON_PATH = new vscode.Position(4, "function probe:al".length);
const OUTSIDE_BLOCK = new vscode.Position(7, 5);

/** @param {vscode.Uri} uri @param {vscode.Position} pos @param {string} [trigger] */
async function completionsAt(uri, pos, trigger) {
  const list = await vscode.commands.executeCommand(
    "vscode.executeCompletionItemProvider", uri, pos, trigger, 50);
  return list && list.items ? list.items : [];
}

/** Wait until Spyglass answers on a real .mcfunction, so a slow start is not read as a failure. */
async function waitForSpyglass(uri, results) {
  for (let attempt = 1; attempt <= 40; attempt++) {
    const items = await completionsAt(uri, new vscode.Position(0, 0));
    if (items.length > 0) {
      results.spyglassReadyAfterSeconds = attempt * 2;
      return items;
    }
    await sleep(2000);
  }
  return [];
}

/** openTextDocument is Canceled while the extension host is still wiring up. */
async function openWithRetry(uri, attempts = 15) {
  let last;
  for (let i = 0; i < attempts; i++) {
    try { return await vscode.workspace.openTextDocument(uri); }
    catch (e) { last = e; await sleep(1000); }
  }
  throw last;
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
    if (stewbeet && !stewbeet.isActive) { try { await stewbeet.activate(); } catch (e) { note("activateError", String(e)); } }

    const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const realUri = vscode.Uri.file(path.join(root, "data", "probe", "function", "beta.mcfunction"));
    await openWithRetry(realUri);
    const control = await waitForSpyglass(realUri, results);
    note("control_realFileCompletions", control.length);
    if (control.length === 0) {
      note("VERDICT", "INCONCLUSIVE: Spyglass never answered on a real .mcfunction file");
      fs.writeFileSync(process.env.SB_OUT, JSON.stringify(results, null, 2));
      return;
    }

    const py = await openWithRetry(vscode.Uri.file(path.join(root, "demo.py")));
    note("pythonLanguageId", py.languageId);
    await sleep(2000);

    // The headline ask: completion mid-command inside a write_function string.
    const inBlock = await completionsAt(py.uri, IN_COMMAND, " ");
    note("us1_completionsInBlock", inBlock.length);
    note("us1_sample", inBlock.slice(0, 8).map(label));
    expect("US1 completion inside a block", inBlock.length > 0);
    expect("US1 offers vanilla commands", inBlock.some(i => label(i) === "say"), inBlock.slice(0, 5).map(label));

    // Project symbols, which is what makes `function <tab>` useful.
    const paths = await completionsAt(py.uri, IN_PATH, ":");
    note("us1_projectSymbols", paths.map(label).slice(0, 10));
    expect("US1 offers the project's own function paths", paths.some(i => label(i).includes("alpha")), paths.map(label).slice(0, 10));

    // Outside a block the providers must stay out of the way.
    // Assert on commands that are NOT words in demo.py, otherwise VS Code's
    // word-based suggestions supply "say" and "execute" on their own and the
    // check fails without the extension having done anything.
    await vscode.workspace.getConfiguration("editor")
      .update("wordBasedSuggestions", "off", vscode.ConfigurationTarget.Workspace);
    await sleep(1000);
    const SPYGLASS_ONLY = ["advancement", "attribute", "ban-ip", "bossbar", "clone"];
    const outside = await completionsAt(py.uri, OUTSIDE_BLOCK);
    const leaked = outside.filter(i => SPYGLASS_ONLY.includes(label(i)));
    note("us1_outsideBlockItems", outside.map(label).slice(0, 10));
    expect("US1 no mcfunction items outside a block", leaked.length === 0, leaked.map(label));

    // ...and the same tokens must be present inside a block, so the check above
    // cannot pass merely because Spyglass went quiet.
    const inBlockAgain = await completionsAt(py.uri, IN_COMMAND, " ");
    expect("US1 control: those tokens do appear inside a block",
      inBlockAgain.some(i => SPYGLASS_ONLY.includes(label(i))), inBlockAgain.map(label).slice(0, 10));

    // US2: hover and signature help.
    const hovers = await vscode.commands.executeCommand("vscode.executeHoverProvider", py.uri, ON_SELECTOR);
    note("us2_hoverResults", (hovers || []).length);
    expect("US2 hover answers inside a block", (hovers || []).length > 0);

    const sig = await vscode.commands.executeCommand("vscode.executeSignatureHelpProvider", py.uri, IN_COMMAND);
    note("us2_signatureHelp", sig ? (sig.signatures || []).length : "none");

    // US3: definition crosses back to the Python that wrote the command.
    //
    // Step A landed in the generated alpha.mcfunction, which is build output nobody edits.
    // The fixture ships alpha.mcfunction.map beside it, so step C rewrites the answer to
    // demo.py. Delete that map and the old behaviour comes back, which is the fallback.
    const defs = await vscode.commands.executeCommand("vscode.executeDefinitionProvider", py.uri, ON_PATH);
    const answers = defs || [];
    // Records which of the two shapes actually arrives, since both are handled and neither is
    // guaranteed by the API. See src/navigation.js targetOf.
    note("us3_answerShape", answers.length === 0 ? "none" : (answers[0].targetUri ? "LocationLink" : "Location"));
    const targets = answers.map(d => String((d.uri || d.targetUri || {}).fsPath || ""));
    const lines = answers.map(d => (d.range || d.targetSelectionRange || d.targetRange || {}).start?.line);
    note("us3_definitionTargets", targets);
    note("us3_definitionLines", lines);
    expect("US3 definition resolves back to the Python source", targets.some(t => t.endsWith("demo.py")), targets);
    expect("US3 definition lands on the write_function line", lines.includes(2), lines);
    expect("US3 definition no longer stops at the generated file",
      !targets.some(t => t.endsWith("alpha.mcfunction")), targets);

    // The settings gate.
    const cfg = vscode.workspace.getConfiguration("StewBeet");
    await cfg.update("languageFeatures", false, vscode.ConfigurationTarget.Workspace);
    await sleep(1500);
    const gated = await completionsAt(py.uri, IN_COMMAND, " ");
    const gatedLeak = gated.filter(i => label(i) === "say");
    expect("Setting gate disables forwarding", gatedLeak.length === 0, gated.slice(0, 5).map(label));
    await cfg.update("languageFeatures", undefined, vscode.ConfigurationTarget.Workspace);

    note("VERDICT", failures.length === 0 ? "PASS" : `FAIL: ${failures.join(", ")}`);
  } catch (e) {
    results.error = String(e && e.stack ? e.stack : e);
    results.VERDICT = "ERROR";
  }

  fs.writeFileSync(process.env.SB_OUT, JSON.stringify(results, null, 2));
};
