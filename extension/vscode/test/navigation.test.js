// @ts-check
"use strict";

// The rewriting half of navigation, tested against a fake map so it runs under plain
// `node --test`. The vscode-facing half (toLocation, findMaps) needs the extension host and is
// covered by test/integration/.

const test = require("node:test");
const assert = require("node:assert");
const path = require("path");

const { targetOf, isGenerated, rewrite } = require("../src/navigation");

const GENERATED = path.resolve("/pack/build/datapack/data/ns/function/main.mcfunction");
const OTHER = path.resolve("/pack/build/datapack/data/ns/function/other.mcfunction");
const LINK = path.resolve("/pack/src/link.py");
const BLOCKS = path.resolve("/pack/src/blocks.py");

/** A Location as vscode hands it to us: only the fields the rewriting reads. @param {string} file @param {number} line */
function location(file, line) {
  return { uri: { scheme: "file", fsPath: file }, range: { start: { line } } };
}

/** A LocationLink, the other shape executeDefinitionProvider may resolve to. @param {string} file @param {number} line */
function link(file, line) {
  return { targetUri: { scheme: "file", fsPath: file }, targetSelectionRange: { start: { line } } };
}

/** A stand-in for ./sourcemap with a fixed table. @param {Record<string, Record<number, {file:string,line:number,column:number}>>} table */
function fakeMaps(table) {
  return {
    originOf: (/** @type {string} */ file, /** @type {number} */ line) => table[file]?.[line] ?? null,
    originsOf: (/** @type {string} */ file) => {
      const byLine = table[file];
      if (!byLine) return [];
      const seen = new Set();
      return Object.keys(byLine).map(Number).sort((a, b) => a - b)
        .map(l => byLine[l])
        .filter(o => !seen.has(o.file) && seen.add(o.file));
    },
  };
}

test("targetOf reads both shapes vscode may return", () => {
  assert.strictEqual(targetOf(location(GENERATED, 3))?.uri.fsPath, GENERATED);
  assert.strictEqual(targetOf(link(GENERATED, 3))?.uri.fsPath, GENERATED);
  assert.strictEqual(targetOf(null), null);
  assert.strictEqual(targetOf({}), null);
});

test("isGenerated only claims real .mcfunction files on disk", () => {
  assert.strictEqual(isGenerated({ scheme: "file", fsPath: GENERATED }), true);
  assert.strictEqual(isGenerated({ scheme: "file", fsPath: LINK }), false);
  assert.strictEqual(isGenerated({ scheme: "stewbeet-mcfunction", fsPath: GENERATED }), false);
});

test("a mapped line is rewritten to its Python origin", () => {
  const maps = fakeMaps({ [GENERATED]: { 3: { file: LINK, line: 14, column: 4 } } });
  assert.deepStrictEqual(rewrite([location(GENERATED, 3)], maps), [{ file: LINK, line: 14, column: 4 }]);
});

test("the LocationLink shape is rewritten the same way", () => {
  const maps = fakeMaps({ [GENERATED]: { 3: { file: LINK, line: 14, column: 4 } } });
  assert.deepStrictEqual(rewrite([link(GENERATED, 3)], maps), [{ file: LINK, line: 14, column: 4 }]);
});

test("a function with several origins offers all of them, in generated order", () => {
  const maps = fakeMaps({
    [GENERATED]: {
      0: { file: BLOCKS, line: 11, column: 4 },
      7: { file: LINK, line: 20, column: 8 },
    },
  });
  // Line 4 is unmapped, so the whole file's origins are offered rather than nothing (G6).
  assert.deepStrictEqual(rewrite([location(GENERATED, 4)], maps), [
    { file: BLOCKS, line: 11, column: 4 },
    { file: LINK, line: 20, column: 8 },
  ]);
});

test("several generated hits collapsing onto one Python line are de-duplicated", () => {
  const maps = fakeMaps({
    [GENERATED]: { 2: { file: LINK, line: 14, column: 4 }, 3: { file: LINK, line: 14, column: 4 } },
  });
  // G7: one Python line writing two commands must not show up twice in the peek list.
  assert.deepStrictEqual(rewrite([location(GENERATED, 2), location(GENERATED, 3)], maps),
    [{ file: LINK, line: 14, column: 4 }]);
});

test("hits across two generated files each keep their own origin", () => {
  const maps = fakeMaps({
    [GENERATED]: { 1: { file: LINK, line: 14, column: 4 } },
    [OTHER]: { 1: { file: BLOCKS, line: 30, column: 0 } },
  });
  assert.deepStrictEqual(rewrite([location(GENERATED, 1), location(OTHER, 1)], maps), [
    { file: LINK, line: 14, column: 4 },
    { file: BLOCKS, line: 30, column: 0 },
  ]);
});

test("a target with no map at all is left to the caller, not dropped", () => {
  assert.strictEqual(rewrite([location(GENERATED, 3)], fakeMaps({})), null);
});

test("a target that is not generated content is never touched", () => {
  const maps = fakeMaps({ [GENERATED]: { 3: { file: LINK, line: 14, column: 4 } } });
  assert.strictEqual(rewrite([location(LINK, 3)], maps), null);
});

test("nothing to rewrite is null rather than an empty list", () => {
  assert.strictEqual(rewrite([], fakeMaps({})), null);
  assert.strictEqual(rewrite(undefined, fakeMaps({})), null);
  assert.strictEqual(rewrite(null, fakeMaps({})), null);
});
