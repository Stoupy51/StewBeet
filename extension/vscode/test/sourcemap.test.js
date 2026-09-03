// @ts-check
"use strict";

// Conformance of the decoder against someone else's encoder.
//
// The fixtures are Sniffer's own reference implementation, committed at
// specs/001-stewbeet-vscode-dx/contracts/reference/, and the expected line tables are
// Appendix A of contracts/source-map.md. No fixture we write ourselves can replace this:
// a decoder that treats the deltas as per-source rather than file-wide passes everything
// we would think to write and fails `aura`.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const path = require("path");

const { decode, decodeVlq, originOf, clearCache } = require("../src/sourcemap");

const REFERENCE = path.resolve(
  __dirname, "../../../specs/001-stewbeet-vscode-dx/contracts/reference/generated/pack/data/ns/function",
);

/** @param {string} relative */
function readMap(relative) {
  return JSON.parse(fs.readFileSync(path.join(REFERENCE, relative), "utf8"));
}

/** The decoded table as `generated -> "source:line:column"`, which is how Appendix A reads. @param {any} json */
function table(json) {
  const map = decode(json);
  return [...map.lines.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([generated, entry]) =>
      [generated, `${map.sources[entry.sourceIndex]}:${entry.sourceLine}:${entry.sourceColumn}`]);
}

test("VLQ decodes the signed values the format specifies", () => {
  assert.deepStrictEqual(decodeVlq("A"), [0]);
  assert.deepStrictEqual(decodeVlq("C"), [1]);
  assert.deepStrictEqual(decodeVlq("D"), [-1]);
  assert.deepStrictEqual(decodeVlq("K"), [5]);
  assert.deepStrictEqual(decodeVlq("H"), [-3]);
  assert.deepStrictEqual(decodeVlq("gB"), [16]);
  // The segment Appendix A singles out: next source, three lines back, in one step.
  assert.deepStrictEqual(decodeVlq("ACHA"), [0, 1, -3, 0]);
});

test("hit.mcfunction.map decodes to Appendix A", () => {
  assert.deepStrictEqual(table(readMap("hit.mcfunction.map")), [
    [0, "source/combat/hit.ts:5:0"],
    [1, "source/combat/hit.ts:6:0"],
    [2, "source/combat/hit.ts:7:0"],
    [3, "source/combat/hit.ts:7:0"],
    [4, "source/combat/hit.ts:8:0"],
  ]);
});

test("aura.mcfunction.map switches source mid-file, which per-source deltas get wrong", () => {
  assert.deepStrictEqual(table(readMap("nested/aura.mcfunction.map")), [
    [0, "source/combat/hit.ts:8:0"],
    [1, "source/spawn.ts:5:0"],
    [2, "source/spawn.ts:6:0"],
  ]);
});

test("two generated lines may share one source line", () => {
  const rows = table(readMap("hit.mcfunction.map"));
  assert.strictEqual(rows[2][1], rows[3][1], "G7: one statement expanding to two commands");
});

test("the trailing sourceMappingURL comment is unmapped", () => {
  const map = decode(readMap("hit.mcfunction.map"));
  assert.strictEqual(map.lines.has(5), false, "no group means unknown origin, not a mapping");
});

test("an unmapped line in the middle is an empty group, not a missing one", () => {
  const map = decode({ sources: ["a.py"], sourceRoot: "", mappings: "AAAA;;AACA" });
  assert.deepStrictEqual([...map.lines.keys()], [0, 2]);
});

test("a malformed map decodes to nothing rather than throwing", () => {
  assert.deepStrictEqual(decode({}).lines.size, 0);
  assert.deepStrictEqual(decode({ sources: ["a.py"], mappings: "!!!!" }).lines.size, 0);
  assert.deepStrictEqual(decode(null).sources, []);
});

test("originOf resolves through sourceRoot to a file that exists", () => {
  clearCache();
  const origin = originOf(path.join(REFERENCE, "hit.mcfunction"), 0);
  assert.ok(origin, "line 0 of the reference is mapped");
  assert.strictEqual(path.basename(origin.file), "hit.ts");
  assert.ok(fs.existsSync(origin.file), `sourceRoot must resolve on disk, got ${origin.file}`);
  assert.strictEqual(origin.line, 5);
});

test("originOf returns null for an unmapped line rather than the nearest one", () => {
  clearCache();
  assert.strictEqual(originOf(path.join(REFERENCE, "hit.mcfunction"), 5), null, "G3 forbids interpolating");
  assert.strictEqual(originOf(path.join(REFERENCE, "does_not_exist.mcfunction"), 0), null);
});
