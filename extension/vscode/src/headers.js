// @ts-check
"use strict";

// Navigation inside a generated .mcfunction file.
//
// StewBeet's headers name the functions that call this one and the ones it calls, but they sit
// in `#` comments, so Spyglass sees prose and offers nothing. Every resource location in a
// comment that matches a real file becomes a link here.
//
// The lens on the header is the other half of the one in Python files: from a block you can
// already reach what it produced, and from what was produced you can now reach the block.

const fs = require("fs");
const path = require("path");
const sourcemap = require("./sourcemap");

// Required lazily by the providers, so the scanning above stays loadable under plain
// `node --test`, where the vscode module does not exist.
/** @returns {typeof import("vscode")} */
function api() {
  return require("vscode");
}

// Constants

const CFG_KEY = "StewBeet";

/** A resource location, as it appears in a header line such as `# @within  ns:path/to/fn`.
 *  Namespace and path use the characters the format allows and nothing else, so ordinary
 *  prose containing a colon does not turn into a link. */
const RESOURCE = /\b([a-z0-9_.-]+):([a-z0-9_./-]+)\b/g;

/** Both spellings, because the folder was renamed between pack formats. */
const FUNCTION_FOLDERS = ["function", "functions"];

// Resolving a resource location

/**
 * The file a resource location names, or null when it is not one of this pack's functions.
 *
 * The pack root is read off the file being viewed rather than configured: a generated function
 * always sits at `<root>/data/<namespace>/function/<path>.mcfunction`, so the root is whatever
 * precedes its own `data` segment.
 *
 * @param {string} fromPath  The generated file the comment appears in.
 * @param {string} namespace
 * @param {string} functionPath
 * @returns {string | null}
 */
function resolveFunction(fromPath, namespace, functionPath) {
  const parts = fromPath.replace(/\\/g, "/").split("/");
  const data = parts.lastIndexOf("data");
  if (data === -1) return null;

  const root = parts.slice(0, data + 1).join("/");
  for (const folder of FUNCTION_FOLDERS) {
    const candidate = `${root}/${namespace}/${folder}/${functionPath}.mcfunction`;
    if (fs.existsSync(candidate)) return path.normalize(candidate);
  }
  return null;
}

/**
 * Every link a generated file's comment lines carry.
 * @param {string} text
 * @param {string} fromPath
 * @returns {{ line: number, start: number, end: number, target: string }[]}
 */
function linksIn(text, fromPath) {
  const found = [];
  text.split("\n").forEach((raw, line) => {
    const content = raw.replace(/\r$/, "");
    if (!content.trimStart().startsWith("#")) return;

    RESOURCE.lastIndex = 0;
    let match;
    while ((match = RESOURCE.exec(content)) !== null) {
      const target = resolveFunction(fromPath, match[1], match[2]);
      if (target) found.push({ line, start: match.index, end: match.index + match[0].length, target });
    }
  });
  return found;
}

// Providers

const documentLinkProvider = {
  /** @param {vscode.TextDocument} doc */
  provideDocumentLinks(doc) {
    const vscode = api();
    if (doc.uri.scheme !== "file") return [];
    if (!vscode.workspace.getConfiguration(CFG_KEY).get("headerLinks", true)) return [];

    // The `#>` line names the file you are already in, so linking it to itself leads nowhere.
    // It points at the Python that wrote it instead, which is the only place left to go.
    const self = path.normalize(doc.uri.fsPath).toLowerCase();
    const origin = sourcemap.originsOf(doc.uri.fsPath)[0];

    const links = [];
    for (const { line, start, end, target } of linksIn(doc.getText(), doc.uri.fsPath)) {
      const range = new vscode.Range(line, start, line, end);
      if (path.normalize(target).toLowerCase() !== self) {
        const link = new vscode.DocumentLink(range, vscode.Uri.file(target));
        link.tooltip = "Go to function";
        links.push(link);
        continue;
      }
      if (!origin) continue;
      const link = new vscode.DocumentLink(
        range, vscode.Uri.file(origin.file).with({ fragment: `L${origin.line + 1}` }));
      link.tooltip = `Go to ${path.basename(origin.file)}:${origin.line + 1}`;
      links.push(link);
    }
    return links;
  },
};

const headerLensProvider = {
  /**
   * One lens at the top of a generated file, leading back to the Python that wrote it.
   * Nothing is shown for a file with no map, which is every file when there is no build.
   * @param {vscode.TextDocument} doc
   */
  provideCodeLenses(doc) {
    const vscode = api();
    if (doc.uri.scheme !== "file") return [];
    if (!vscode.workspace.getConfiguration(CFG_KEY).get("codeLens", true)) return [];

    const origins = sourcemap.originsOf(doc.uri.fsPath);
    if (origins.length === 0) return [];

    const origin = origins[0];
    const extra = origins.length > 1 ? ` (+${origins.length - 1} more)` : "";
    return [new vscode.CodeLens(new vscode.Range(0, 0, 0, 0), {
      title: `$(go-to-file) ${path.basename(origin.file)}:${origin.line + 1}${extra}`,
      tooltip: origin.file,
      command: "stewbeet.goToSource",
      arguments: [origin],
    })];
  },
};

/** @param {vscode.ExtensionContext} context */
function registerHeaderNavigation(context) {
  const vscode = api();
  // Both ids, because a `.mcfunction` holding bolt is switched to `bolt` to keep Spyglass off
  // it, and losing its header links for that would be a poor trade. A `.bolt` source has no map
  // of its own, so the lens finds nothing there and only the comment links appear.
  for (const language of ["mcfunction", "bolt"]) {
    context.subscriptions.push(
      vscode.languages.registerDocumentLinkProvider({ language, scheme: "file" }, documentLinkProvider),
      vscode.languages.registerCodeLensProvider({ language, scheme: "file" }, headerLensProvider),
    );
  }
}

module.exports = {
  resolveFunction,
  linksIn,
  documentLinkProvider,
  headerLensProvider,
  registerHeaderNavigation,
};
