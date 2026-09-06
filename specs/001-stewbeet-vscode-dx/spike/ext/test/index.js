const vscode = require("vscode");
const fs = require("fs");
const path = require("path");

const OUT = process.env.Q2_OUT;
const SCHEME = "stewbeet-mcfunction";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// The projection under test: everything outside [start,end) becomes a space, newlines kept.
function project(text, start, end) {
  let out = "";
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    out += (i >= start && i < end) || c === "\n" ? c : " ";
  }
  return out;
}

const PY = [
  'write_function("probe:demo", """',
  "execute as @a run say hi",
  "function probe:alpha",
  '""")',
  "",
].join("\n");

const BLOCK_START = PY.indexOf("\n") + 1;
const BLOCK_END = PY.indexOf('""")');

let virtualContent = "";
const emitter = new vscode.EventEmitter();

async function completionsAt(uri, pos, trigger) {
  const list = await vscode.commands.executeCommand(
    "vscode.executeCompletionItemProvider", uri, pos, trigger, 50,
  );
  return list && list.items ? list.items : [];
}

const label = (it) => (typeof it.label === "string" ? it.label : it.label && it.label.label) || "";

// Poll until Spyglass has finished initializing and answers on a real file.
async function waitForSpyglass(realUri, results) {
  for (let attempt = 1; attempt <= 40; attempt++) {
    const items = await completionsAt(realUri, new vscode.Position(0, 0));
    if (items.length > 0) {
      results.spyglassReadyAfterSeconds = attempt * 2;
      return items;
    }
    await sleep(2000);
  }
  return [];
}

// openTextDocument is Canceled while the extension host is still wiring up.
async function openWithRetry(uri, attempts = 15) {
  let last;
  for (let i = 0; i < attempts; i++) {
    try { return await vscode.workspace.openTextDocument(uri); }
    catch (e) { last = e; await sleep(1000); }
  }
  throw last;
}

exports.run = async () => {
  const results = { steps: [] };
  const note = (k, v) => { results[k] = v; results.steps.push(`${k} = ${JSON.stringify(v)}`); };

  try {
    await sleep(5000); // let the window and extension host settle
    const sg = vscode.extensions.getExtension("SPGoding.datapack-language-server");
    note("spyglassInstalled", !!sg);
    if (sg && !sg.isActive) { try { await sg.activate(); } catch (e) { note("activateError", String(e)); } }
    note("spyglassActive", !!(sg && sg.isActive));
    note("workspaceFolders", (vscode.workspace.workspaceFolders || []).map((f) => f.uri.fsPath));

    // --- Control: a real .mcfunction file in the workspace -------------------
    const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const realUri = vscode.Uri.file(path.join(root, "data", "probe", "function", "beta.mcfunction"));
    const realDoc = await openWithRetry(realUri);
    note("realLanguageId", realDoc.languageId);

    const realItems = await waitForSpyglass(realUri, results);
    note("control_realFileCompletions", realItems.length);
    note("control_sample", realItems.slice(0, 8).map(label));

    if (realItems.length === 0) {
      note("VERDICT", "INCONCLUSIVE: Spyglass never answered on a real .mcfunction file");
      fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
      return;
    }

    // --- The question: a virtual document, opened but never shown ------------
    vscode.workspace.registerTextDocumentContentProvider(SCHEME, {
      onDidChange: emitter.event,
      provideTextDocumentContent: () => virtualContent,
    });

    virtualContent = project(PY, BLOCK_START, BLOCK_END);
    note("projectedContent", virtualContent);

    const vUri = vscode.Uri.parse(`${SCHEME}://probe/0/demo.mcfunction`);
    const vDoc = await openWithRetry(vUri);
    note("virtualLanguageId", vDoc.languageId);
    note("offsetsIdentical", vDoc.getText().length === PY.length);

    await sleep(3000); // let the client sync didOpen and the server parse

    // line 1 is "execute as @a run say hi"; ask right after "run "
    const posAfterRun = new vscode.Position(1, "execute as @a run ".length);
    let vItems = await completionsAt(vUri, posAfterRun, " ");
    note("unshown_virtualCompletions", vItems.length);
    note("unshown_sample", vItems.slice(0, 8).map(label));

    // --- Escalation step 1: show it in a preserved-focus preview editor ------
    if (vItems.length === 0) {
      await vscode.window.showTextDocument(vDoc, { preserveFocus: true, preview: true });
      await sleep(3000);
      vItems = await completionsAt(vUri, posAfterRun, " ");
      note("shown_virtualCompletions", vItems.length);
      note("shown_sample", vItems.slice(0, 8).map(label));
    }

    // --- Does the virtual doc see the project symbol table? ------------------
    // line 2 is "function probe:alpha"; ask after "function probe:"
    const posInPath = new vscode.Position(2, "function probe:".length);
    const pathItems = await completionsAt(vUri, posInPath, ":");
    note("projectSymbolCompletions", pathItems.length);
    note("projectSymbolSample", pathItems.slice(0, 12).map(label));
    note("offersAlpha", pathItems.some((i) => label(i).includes("alpha")));

    // --- Hover and definition, the other forwarded requests -----------------
    const hovers = await vscode.commands.executeCommand("vscode.executeHoverProvider", vUri, posInPath);
    note("hoverResults", (hovers || []).length);
    const defs = await vscode.commands.executeCommand("vscode.executeDefinitionProvider", vUri, posInPath);
    note("definitionResults", (defs || []).length);
    note("definitionTargets", (defs || []).map((d) => (d.uri || d.targetUri || {}).fsPath || String(d.uri || d.targetUri)));

    const worked = results.unshown_virtualCompletions > 0;
    const workedShown = results.shown_virtualCompletions > 0;
    note("VERDICT", worked ? "PASS: virtual documents work unshown"
      : workedShown ? "PASS WITH ESCALATION: must show the document"
      : "FAIL: Spyglass does not answer on virtual documents");
  } catch (e) {
    results.error = String(e && e.stack ? e.stack : e);
    results.VERDICT = "ERROR";
  }

  fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
};
