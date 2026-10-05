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

const os = require("os");

const {
  decode, decodeVlq, originOf, clearCache, isBoltSource, compiledColumns, opaqueStarts, originLinesFor,
} = require("../src/sourcemap");

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

// Columns and the x_ fields, which a build compiling through mecha adds

test("a line with several segments keeps the first as its origin and the rest as its points", () => {
  // `schedule function ~/ 1t replace` on source line 4, compiled to `schedule function t:probe 1 replace`.
  const map = decode({ sources: ["a.mcfunction"], mappings: "AAIA,kBAAkB,OAAE,CAAC,CAAE" });
  const line = map.lines.get(0);
  assert.deepStrictEqual([line?.sourceLine, line?.sourceColumn], [4, 0]);
  assert.deepStrictEqual(line?.points, [
    { generated: 18, line: 4, column: 18 },
    { generated: 25, line: 4, column: 20 },
    { generated: 26, line: 4, column: 21 },
    { generated: 27, line: 4, column: 23 },
  ], "the generated column restarts on each line while the source fields run on");
});

test("the x_ fields are read, and a map without them has none", () => {
  const map = decode({ sources: ["a.mcfunction"], mappings: "AAAA", x_stewbeet_bolt: [0], x_stewbeet_opaque: [[0, 3, 8]] });
  assert.deepStrictEqual([map.bolt, map.opaque], [[0], [[0, 3, 8]]]);
  assert.deepStrictEqual([decode({ mappings: "AAAA" }).bolt, decode({ mappings: "AAAA" }).opaque], [[], []]);
});

test("a source file reads what every map says about it", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-sourcemap-"));
  const source = path.join(root, "src", "tick.mcfunction");
  const generated = path.join(root, "build", "data", "t", "function", "tick.mcfunction");
  fs.mkdirSync(path.dirname(source), { recursive: true });
  fs.mkdirSync(path.dirname(generated), { recursive: true });
  fs.writeFileSync(source, "say a\n\n\n\nschedule function ~/ 1t replace\ncompute bolt float (1+1)\n");
  fs.writeFileSync(generated, "say a\nschedule function t:probe 1 replace\ncompute default float 2\n");
  fs.writeFileSync(`${generated}.map`, JSON.stringify({
    version: 3, sources: ["src/tick.mcfunction"], sourceRoot: "../../../../",
    mappings: "AAAA;AAIA,kBAAkB,OAAE;AACpB", x_stewbeet_bolt: [0], x_stewbeet_opaque: [[0, 5, 8]],
  }));
  clearCache();
  const maps = [`${generated}.map`];

  assert.ok(isBoltSource(maps, source));
  assert.ok(!isBoltSource(maps, path.join(root, "src", "other.mcfunction")));
  assert.deepStrictEqual([...originLinesFor(maps, source).keys()], [0, 4, 5], "every line a command was compiled from");
  assert.deepStrictEqual(compiledColumns(maps, source).get(4),
    { text: "schedule function t:probe 1 replace", points: [{ generated: 18, column: 18 }, { generated: 25, column: 20 }] });
  assert.deepStrictEqual([...opaqueStarts(maps, source)], [[5, 8]]);
  fs.rmSync(root, { recursive: true, force: true });
  clearCache();
});

test("originOf returns null for an unmapped line rather than the nearest one", () => {
  clearCache();
  assert.strictEqual(originOf(path.join(REFERENCE, "hit.mcfunction"), 5), null, "G3 forbids interpolating");
  assert.strictEqual(originOf(path.join(REFERENCE, "does_not_exist.mcfunction"), 0), null);
});
