// @ts-check
"use strict";

// The lenses VS Code shows on real files, with Spyglass running beside this extension.
//
//   SB_TESTS=lenses SB_WORKSPACE=d:/advanced_desktop/projects/Switch \
//   SB_FILES=build/datapack/data/switch/function/modes/tnt_run/dash/use.mcfunction,src/datapack/modes/tnt_run/main.py \
//   node test/integration/run.js
//
// VS Code shows none of a file's lenses until every provider has answered, so one provider still waiting hides them all.
// A generated file's header lens needs no map index and must answer at once, even while a build is reindexed.
// A source file's lenses come once the index is built, and each file listed must show at least one by then.

const vscode = require("vscode");
const path = require("node:path");
const fs = require("node:fs");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** How long a reader waits for a lens before calling it missing, and how long the index gets to build. */
const LIMIT_MS = Number(process.env.SB_LIMIT_MS || 20000);

/** @param {vscode.Uri} uri @returns {Promise<{ ms: number, titles: string[] } | null>}  Null when VS Code got no answer in time. */
async function lensTitles(uri) {
  const startedAt = Date.now();
  /** @type {Thenable<vscode.CodeLens[]>} */
  const asked = vscode.commands.executeCommand("vscode.executeCodeLensProvider", uri, 100);
  const lenses = await Promise.race([asked, sleep(LIMIT_MS).then(() => null)]);
  if (!lenses) return null;
  return { ms: Date.now() - startedAt, titles: lenses.filter(lens => lens.command).map(lens => `${lens.range.start.line + 1}: ${lens.command?.title}`) };
}

exports.run = async () => {
  const results = { checks: [] };
  const failures = [];
  // Written after every step, so a run that hangs still says how far it got.
  const note = (k, v) => {
    results[k] = v;
    results.checks.push(`${k} = ${JSON.stringify(v)}`);
    fs.writeFileSync(String(process.env.SB_OUT), JSON.stringify(results, null, 2));
  };

  try {
    const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const files = String(process.env.SB_FILES || "").split(",").filter(Boolean).map(f => path.join(root, f));
    note("spyglass", Boolean(vscode.extensions.getExtension("SPGoding.datapack-language-server")));
    const stewbeet = vscode.extensions.getExtension("stoupy.stewbeet");
    if (stewbeet && !stewbeet.isActive) await stewbeet.activate();

    for (const file of files) {
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(file));
      await vscode.window.showTextDocument(doc, { preview: false });
      note(`${path.basename(file)} languageId`, doc.languageId);
      const answer = await lensTitles(doc.uri);
      note(path.basename(file), answer ?? `no answer within ${LIMIT_MS} ms`);
    }

    // Spyglass is still indexing the pack right after opening, which is when a reader first looks, and again once it is done.
    await sleep(LIMIT_MS);
    for (const file of files) {
      const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(file));
      note(`${path.basename(file)} languageId later`, doc.languageId);
      const answer = await lensTitles(doc.uri);
      note(`${path.basename(file)} later`, answer ?? `no answer within ${LIMIT_MS} ms`);
      if (!answer || answer.titles.length === 0) failures.push(path.basename(file));
    }

    // What a build does: every map is reindexed, and a generated file's header lens must not wait for that.
    const generated = files.find(file => file.endsWith(".mcfunction"));
    if (generated) {
      await vscode.commands.executeCommand("stewbeet.reloadSourceMaps");
      const answer = await lensTitles(vscode.Uri.file(generated));
      note(`${path.basename(generated)} while reindexing`, answer ?? `no answer within ${LIMIT_MS} ms`);
      if (!answer || answer.titles.length === 0 || answer.ms > 1000) failures.push(`${path.basename(generated)} while reindexing`);
    }
    note("VERDICT", failures.length === 0 ? "PASS" : `FAIL no lens on ${failures.join(", ")}`);
  } catch (e) {
    results.error = String(e && e.stack ? e.stack : e);
    note("VERDICT", "FAIL");
  }
};
