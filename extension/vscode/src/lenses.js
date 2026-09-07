// @ts-check
"use strict";

// Where a lens goes and what it is called, with no editor involved.
//
// Split out of codelens.js, which builds `vscode.CodeLens` objects and so cannot be loaded
// under plain `node --test`. Deciding the anchor and the title is the part worth testing:
// it is the difference between one lens on a function and twenty on its lines.

const path = require("path");

/**
 * The resource location a generated path spells, for the lens to name the target.
 * Falls back to the file name for a layout the convention does not cover.
 * @param {string} generatedPath
 * @returns {string}
 */
function functionIdOf(generatedPath) {
  const parts = generatedPath.replace(/\\/g, "/").split("/");
  const data = parts.lastIndexOf("data");
  const folder = parts.findIndex((part, i) => i > data && (part === "function" || part === "functions"));
  if (data === -1 || folder === -1 || folder <= data + 1) return path.basename(generatedPath);
  return `${parts[data + 1]}:${parts.slice(folder + 1).join("/").replace(/\.mcfunction$/, "")}`;
}

/**
 * What a block produced, or null when the current build knows nothing about it.
 *
 * Two shapes of origin exist. Commands written inline map line by line, so the answer sits on
 * one of the block's own lines. Commands arriving in a variable are all attributed to the call
 * itself, so the answer sits on the call line. Both are tried.
 *
 * @param {Map<number, { file: string, line: number }[]>} origins
 * @param {{ positionAt: (offset: number) => { line: number } }} doc
 * @param {{ start:number, end:number }} block
 * @param {number} callLine
 * @returns {{ file: string, line: number }[] | null}  Every function that line produced.
 */
function targetOfBlock(origins, doc, block, callLine) {
  const found = origins.get(callLine);
  if (found && found.length > 0) return found;

  const last = doc.positionAt(block.end).line;
  for (let line = doc.positionAt(block.start).line; line <= last; line++) {
    const inside = origins.get(line);
    if (inside && inside.length > 0) return inside;
  }
  return null;
}

/**
 * One anchor per function a source file produced, at the first line that produced it.
 *
 * Bolt has no blocks to hang a lens on: the whole file is source, and one module routinely
 * writes dozens of functions. Grouping by target is what keeps the density useful, and the
 * first mapped line of a target is the first command inside it, so the lens sits directly
 * under the `function ...:` that opened it.
 *
 * @param {Map<number, { file: string, line: number }>} origins
 * @returns {{ line: number, target: { file: string, line: number } }[]}
 */
function lensAnchors(origins) {
  /** Earliest line each generated function was written from. @type {Map<string, number>} */
  const firsts = new Map();
  /** @type {Map<string, { file: string, line: number }>} */
  const byFile = new Map();
  for (const [line, targets] of origins) {
    for (const target of targets) {
      const seen = firsts.get(target.file);
      if (seen === undefined || line < seen) firsts.set(target.file, line);
      if (!byFile.has(target.file)) byFile.set(target.file, target);
    }
  }

  // One lens per line, not per function: a `write_function` in a loop writes several functions
  // from the same line, and stacking a lens for each would bury the line it sits on.
  /** @type {Map<number, { file: string, line: number }[]>} */
  const byLine = new Map();
  for (const [file, line] of firsts) {
    const bucket = byLine.get(line);
    const target = /** @type {{ file: string, line: number }} */ (byFile.get(file));
    if (bucket) bucket.push(target);
    else byLine.set(line, [target]);
  }

  return [...byLine.entries()]
    .map(([line, targets]) => ({ line, target: targets[0], targets: targets.sort((a, b) => a.file.localeCompare(b.file)) }))
    .sort((a, b) => a.line - b.line);
}

module.exports = {
  functionIdOf,
  targetOfBlock,
  lensAnchors,
};
