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

// Line 12 is "function {ns}:alpha", which gamma.mcfunction resolves to "function probe:alpha".
// Both columns are Python columns, four characters short of where they land in the virtual
// document, which is the whole point of the translation these two exercise.
const IN_INTERPOLATED = new vscode.Position(12, "function {ns}:".length);
const ON_INTERPOLATED = new vscode.Position(12, "function {ns}:al".length);

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
    // Shown, not merely opened: VS Code disposes a document no editor is holding, and the
    // author always has their Python file visible. Leaving it unshown made the run drift into
    // a state no user is ever in.
    await vscode.window.showTextDocument(py, { preview: false });
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

    // US4: the same two answers on a path StewBeet actually writes.
    //
    // Nothing here can pass by masking: `function ____:alpha` is not a resource location, so
    // without the substitution Spyglass resolves nothing and both checks come back empty.
    const interpolated = await completionsAt(py.uri, IN_INTERPOLATED, ":");
    note("us4_interpolatedCompletions", interpolated.map(label).slice(0, 10));
    expect("US4 completion works on an interpolated path",
      interpolated.some(i => label(i).includes("alpha")), interpolated.map(label).slice(0, 10));

    const interpolatedDefs = (await vscode.commands.executeCommand(
      "vscode.executeDefinitionProvider", py.uri, ON_INTERPOLATED)) || [];
    const interpolatedTargets = interpolatedDefs.map(d => String((d.uri || d.targetUri || {}).fsPath || ""));
    note("us4_interpolatedDefinitionTargets", interpolatedTargets);
    expect("US4 definition resolves from an interpolated path",
      interpolatedTargets.some(t => t.endsWith("demo.py")), interpolatedTargets);

    // ...and the escape hatch puts the mask back, which is step A's behaviour exactly.
    //
    // Definition is what tells the two apart, not completion: Spyglass answers a resource
    // location request with every path in the pack whatever the prefix, so `____:` lists the
    // same items that `probe:` does. Only resolving one needs the real namespace.
    const settings = vscode.workspace.getConfiguration("StewBeet");
    await settings.update("resolveInterpolations", false, vscode.ConfigurationTarget.Workspace);
    await sleep(3000);
    const maskedDefs = (await vscode.commands.executeCommand(
      "vscode.executeDefinitionProvider", py.uri, ON_INTERPOLATED)) || [];
    const maskedTargets = maskedDefs.map(d => String((d.uri || d.targetUri || {}).fsPath || ""));
    expect("US4 turning substitution off restores masking", maskedTargets.length === 0, maskedTargets);
    await settings.update("resolveInterpolations", undefined, vscode.ConfigurationTarget.Workspace);
    await sleep(3000);

    // Does the server report errors on the virtual documents themselves?
    //
    // This decides the whole diagnostics design. Opening a generated file invisibly is
    // unreliable, because VS Code disposes a document nothing is shown in and the server drops
    // it. The virtual documents are ones we open and reopen ourselves, and their lines are in
    // lockstep with the Python, so if errors arrive on them the relay needs no build at all.
    // demo.py line 16 is `nonexistentcommand foo bar`, which no version of the game accepts.
    const virtualUri = vscode.Uri.from({
      scheme: "stewbeet-mcfunction",
      path: "/2/demo.py.mcfunction",
      query: py.uri.toString(),
    });
    await openWithRetry(virtualUri);
    await completionsAt(py.uri, new vscode.Position(16, 5), " ");
    await sleep(4000);

    const virtualDiagnostics = vscode.languages.getDiagnostics(virtualUri) || [];
    note("virtual_diagnosticCount", virtualDiagnostics.length);
    note("virtual_diagnostics", virtualDiagnostics.slice(0, 4).map(
      d => `${d.range.start.line}:${d.range.start.character} ${d.message}`));
    note("virtual_documentStaysOpen",
      vscode.workspace.textDocuments.some(d => d.uri.toString() === virtualUri.toString()));

    expect("US5 the server reports on virtual documents", virtualDiagnostics.length > 0);

    // The quotes are Python, and projecting them earned a diagnostic saying `"""` is not a
    // command. Line 15 and line 17 are the two quote lines around the broken block.
    const onQuoteLines = virtualDiagnostics.filter(d => d.range.start.line === 15 || d.range.start.line === 17);
    note("virtual_quoteLineNoise", onQuoteLines.map(d => d.range.start.line));
    expect("US5 the string quotes raise nothing", onQuoteLines.length === 0,
      onQuoteLines.map(d => `${d.range.start.line}: ${d.message.slice(0, 40)}`));

    // ...and the whole point: it reaches the Python file without any generated file involved.
    await sleep(2000);
    const beforeCommand = (vscode.languages.getDiagnostics(py.uri) || [])
      .filter(d => String(d.source || "").startsWith("stewbeet")).length;
    note("us5_relayedBeforeCommand", beforeCommand);

    // Forcing the pass separates "the event never reached us" from "the mapping is broken".
    await vscode.commands.executeCommand("stewbeet.refreshDiagnostics");
    await sleep(3000);
    note("us5_relayStatus", await vscode.commands.executeCommand("stewbeet.diagnosticsStatus"));
    const relayed = vscode.languages.getDiagnostics(py.uri) || [];
    const ours = relayed.filter(d => String(d.source || "").startsWith("stewbeet"));
    note("us5_relayedOntoPython", ours.map(d => `${d.range.start.line}: ${d.message.slice(0, 45)}`));
    expect("US5 the error reaches the Python file with no build file opened",
      ours.some(d => d.range.start.line === 16), ours.map(d => d.range.start.line));

    // US6: a real mistake on a line that also carries an unresolvable interpolation.
    //
    // demo.py line 20 is `execute store reslt score #h {ns}.data run data get entity @s Pos[1]`.
    // Nothing in the fixture's build matches it, so `{ns}` keeps its mask, and the diagnostic
    // for the `reslt` typo runs from the typo to the end of the line and therefore crosses that
    // mask. Suppressing everything that merely overlaps a mask threw this error away.
    const virtualTypo = vscode.Uri.from({
      scheme: "stewbeet-mcfunction",
      path: "/3/demo.py.mcfunction",
      query: py.uri.toString(),
    });
    await openWithRetry(virtualTypo);
    await completionsAt(py.uri, new vscode.Position(20, 5), " ");
    await sleep(4000);
    await vscode.commands.executeCommand("stewbeet.refreshDiagnostics");
    await sleep(3000);

    const onTypoLine = (vscode.languages.getDiagnostics(py.uri) || [])
      .filter(d => String(d.source || "").startsWith("stewbeet") && d.range.start.line === 20);
    note("us6_typoDiagnostics", onTypoLine.map(d => `${d.range.start.character}: ${d.message.slice(0, 40)}`));
    expect("US6 a typo is reported on a line whose interpolation stayed masked",
      onTypoLine.length > 0, (vscode.languages.getDiagnostics(py.uri) || []).map(d => d.range.start.line));

    // ...and the mask itself must still raise nothing, which is what US5 established.
    const maskColumn = "execute store reslt score #h ".length;
    expect("US6 the mask on that same line still raises nothing",
      !onTypoLine.some(d => d.range.start.character >= maskColumn
        && d.range.start.character < maskColumn + "{ns}".length),
      onTypoLine.map(d => d.range.start.character));

    // Waking a document makes the server publish, and publishing is what asks for the next
    // pass, so a pass that always wakes never stops. The broken version ran seven a second
    // with nobody typing, which is what "my editor got slow" looks like from the inside.
    const passesBefore = (await vscode.commands.executeCommand("stewbeet.diagnosticsStatus")).livePasses;
    await sleep(10000);
    const passesAfter = (await vscode.commands.executeCommand("stewbeet.diagnosticsStatus")).livePasses;
    note("us6_idlePasses", passesAfter - passesBefore);
    expect("US6 the relay does not spin while nothing changes", passesAfter - passesBefore <= 4,
      passesAfter - passesBefore);

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
