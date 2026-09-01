// @ts-check
"use strict";

// Pure projection of a Python buffer into a virtual mcfunction document, plus
// the virtual URI path helpers. Kept free of any "vscode" dependency so it can
// be unit-tested with plain Node (see test/projection.test.js).

// ─── Constants──────────────

const SCHEME = "stewbeet-mcfunction";

// ─── Projection─────────────

/**
 * Project a Python document into the mcfunction document Spyglass should see.
 *
 * Everything outside the block becomes a space and every interpolation becomes
 * a run of "_", while newlines are preserved everywhere. The result therefore
 * has the same length and the same line breaks as the input, so a position in
 * one document is the same position in the other and no range ever needs
 * translating on the way back.
 *
 * "_" rather than a space for interpolations because it is legal in resource
 * locations, selector values, objectives and tags, so the masked token still
 * parses as a plausible word in most argument positions. It will not parse
 * where a number is required; that costs one completion list and nothing more,
 * because diagnostics are never taken from the virtual document.
 *
 * @param {string} text  The whole Python document.
 * @param {number} start  Offset of the block's opening quote (prefix included).
 * @param {number} end  Offset just past the block's closing quote.
 * @param {{ start:number, end:number }[]} [interpolationSpans]  Sorted, from findInterpolationSpans.
 * @returns {string}  Same length as `text`.
 */
function project(text, start, end, interpolationSpans = []) {
  let out = "";
  let spanIdx = 0;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === "\n" || c === "\r") { out += c; continue; }
    if (i < start || i >= end) { out += " "; continue; }

    while (spanIdx < interpolationSpans.length && interpolationSpans[spanIdx].end <= i) spanIdx++;
    const span = interpolationSpans[spanIdx];
    out += (span && i >= span.start && i < span.end) ? "_" : c;
  }

  return out;
}

// ─── Virtual URIs───────────

/**
 * Strip anything that has no business in a URI path segment.
 * @param {string} name
 */
function sanitizeName(name) {
  const cleaned = name.replace(/[^A-Za-z0-9._-]/g, "_");
  return cleaned || "embedded";
}

/**
 * Build the path of a virtual document's URI.
 * The trailing ".mcfunction" is load-bearing: VS Code derives a document's
 * language id from its path extension, and that language id is what makes
 * Spyglass's document selector match.
 * @param {number} blockIndex
 * @param {string} baseName  Base name of the originating Python file.
 * @returns {string}
 */
function virtualPath(blockIndex, baseName) {
  return `/${blockIndex}/${sanitizeName(baseName)}.mcfunction`;
}

/**
 * Recover the block index from a virtual document's URI path.
 * @param {string} path
 * @returns {number | undefined}
 */
function blockIndexFromPath(path) {
  const m = /^\/(\d+)\//.exec(path);
  return m ? Number(m[1]) : undefined;
}

module.exports = {
  SCHEME,
  project,
  sanitizeName,
  virtualPath,
  blockIndexFromPath,
};
