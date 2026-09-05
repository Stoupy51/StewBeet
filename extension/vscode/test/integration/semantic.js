// @ts-check
"use strict";

// Does Spyglass answer semantic tokens, and does it answer them for a virtual document?
//
//   SB_TESTS=semantic node test/integration/run.js
//
// This gates a design: colouring commands that reach a project's own `def` cannot be done by a
// TextMate grammar, which sees one place at a time and cannot connect a call to a `def`
// elsewhere. A semantic tokens provider can, but only if Spyglass supplies the tokens, since
// StewBeet may not reimplement mcfunction syntax (NFR-001).

const vscode = require("vscode");
const path = require("node:path");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const results = { checks: [] };
const note = (key, value) => {
  results[key] = value;
  results.checks.push(`${key} = ${JSON.stringify(value)}`);
};

/** Decode the flat uint32 array into readable tokens, resolving the legend. */
function decode(data, legend, limit = 12) {
  if (!data || !data.data) return null;
  const raw = data.data;
  const out = [];
  let line = 0;
  let char = 0;
  for (let i = 0; i + 4 < raw.length && out.length < limit; i += 5) {
    line += raw[i];
    char = raw[i] === 0 ? char + raw[i + 1] : raw[i + 1];
    out.push({
      line,
      char,
      length: raw[i + 2],
      type: legend ? legend.tokenTypes[raw[i + 3]] : raw[i + 3],
    });
  }
  return out;
}

module.exports.run = async () => {
  try {
    const folder = vscode.workspace.workspaceFolders[0].uri;
    const generated = vscode.Uri.joinPath(folder, "data", "probe", "function", "alpha.mcfunction");

    // Control: a real .mcfunction file. Without this the rest proves nothing.
    const real = await vscode.workspace.openTextDocument(generated);
    await vscode.window.showTextDocument(real, { preview: false });
    await sleep(4000);

    const legend = await vscode.commands.executeCommand(
      "vscode.provideDocumentSemanticTokensLegend", real.uri);
    note("legendFound", Boolean(legend));
    note("tokenTypes", legend ? legend.tokenTypes : null);

    const realTokens = await vscode.commands.executeCommand(
      "vscode.provideDocumentSemanticTokens", real.uri);
    note("realFileText", real.getText().split("\n")[0]);
    note("realFileTokenCount", realTokens && realTokens.data ? realTokens.data.length / 5 : 0);
    note("realFileTokens", decode(realTokens, legend));
    note("control: Spyglass answers semantic tokens on a real file",
      realTokens && realTokens.data && realTokens.data.length > 0 ? "PASS" : "INCONCLUSIVE");

    // The question: does it answer for the virtual documents this extension serves?
    const py = await vscode.workspace.openTextDocument(vscode.Uri.joinPath(folder, "demo.py"));
    await vscode.window.showTextDocument(py, { preview: false });
    await sleep(3000);

    const virtual = vscode.Uri.from({
      scheme: "stewbeet-mcfunction",
      path: "/0/demo.py.mcfunction",
      query: py.uri.toString(),
    });
    const doc = await vscode.workspace.openTextDocument(virtual);
    // One hover makes the server actually look at the document, as the relay does.
    await vscode.commands.executeCommand("vscode.executeHoverProvider", virtual, new vscode.Position(3, 3));
    await sleep(3000);

    note("virtualFirstLines", doc.getText().split("\n").slice(0, 5));
    const virtualTokens = await vscode.commands.executeCommand(
      "vscode.provideDocumentSemanticTokens", virtual);
    note("virtualTokenCount", virtualTokens && virtualTokens.data ? virtualTokens.data.length / 5 : 0);
    note("virtualTokens", decode(virtualTokens, legend));
    note("the virtual document answers too",
      virtualTokens && virtualTokens.data && virtualTokens.data.length > 0 ? "PASS" : "FAIL");

    note("VERDICT", results["the virtual document answers too"] === "PASS"
      ? "PASS"
      : (results["control: Spyglass answers semantic tokens on a real file"] === "INCONCLUSIVE"
        ? "INCONCLUSIVE: Spyglass never answered semantic tokens at all"
        : "FAIL: real files answer but virtual ones do not"));
  } catch (e) {
    results.error = String(e && e.stack ? e.stack : e);
    note("VERDICT", "ERROR");
  }

  require("node:fs").writeFileSync(process.env.SB_OUT, JSON.stringify(results, null, 2));
};
