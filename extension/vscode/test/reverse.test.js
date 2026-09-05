// @ts-check
"use strict";

// The source-to-generated direction, which is what the lenses on a source file read.
//
// Built against maps written to a temporary directory rather than fixtures on disk, because
// what is under test is the index over several maps and the paths they resolve through, not
// the decoding of one file. sourcemap.test.js covers the decoding against Sniffer's reference.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const os = require("os");
const path = require("path");

const { originLinesFor, generatedFrom, clearCache } = require("../src/sourcemap");
const { lensAnchors } = require("../src/lenses");

/** A pack laid out the way a build writes one, with maps beside their functions. */
function makePack() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-reverse-"));
  const functions = path.join(root, "build", "datapack", "data", "ns", "function");
  fs.mkdirSync(functions, { recursive: true });
  fs.mkdirSync(path.join(root, "src"), { recursive: true });
  fs.writeFileSync(path.join(root, "src", "one.bolt"), "say a\nsay b\n");
  fs.writeFileSync(path.join(root, "src", "two.bolt"), "say c\n");
  return { root, functions };
}

/**
 * @param {string} functions
 * @param {string} name
 * @param {string[]} sources  Relative to the project root.
 * @param {string} mappings
 */
function writeMap(functions, name, sources, mappings) {
  fs.writeFileSync(path.join(functions, `${name}.mcfunction`), "say generated\n");
  fs.writeFileSync(path.join(functions, `${name}.mcfunction.map`), JSON.stringify({
    version: 3, file: `${name}.mcfunction`, sourceRoot: "../../../../..", sources, names: [], mappings,
  }));
}

test("a source line finds what it generated, across several maps", () => {
  clearCache();
  const { root, functions } = makePack();
  // alpha line 0 comes from one.bolt line 0; beta line 0 comes from two.bolt line 0.
  writeMap(functions, "alpha", ["src/one.bolt"], "AAAA");
  writeMap(functions, "beta", ["src/two.bolt"], "AAAA");
  const maps = ["alpha", "beta"].map(n => path.join(functions, `${n}.mcfunction.map`));

  const fromOne = generatedFrom(maps, path.join(root, "src", "one.bolt"), 0);
  assert.strictEqual(fromOne.length, 1);
  assert.ok(fromOne[0].file.endsWith("alpha.mcfunction"), fromOne[0].file);

  const fromTwo = generatedFrom(maps, path.join(root, "src", "two.bolt"), 0);
  assert.ok(fromTwo[0].file.endsWith("beta.mcfunction"), fromTwo[0].file);

  assert.deepStrictEqual(generatedFrom(maps, path.join(root, "src", "one.bolt"), 9), [],
    "a line that generated nothing has no answer, and never the nearest one");
  clearCache();
});

test("one source file feeding several functions lists each of them once", () => {
  clearCache();
  const { root, functions } = makePack();
  // Both functions come from one.bolt: alpha from line 0, beta from line 1.
  writeMap(functions, "alpha", ["src/one.bolt"], "AAAA");
  writeMap(functions, "beta", ["src/one.bolt"], "AACA");
  const maps = ["alpha", "beta"].map(n => path.join(functions, `${n}.mcfunction.map`));

  const origins = originLinesFor(maps, path.join(root, "src", "one.bolt"));
  assert.deepStrictEqual([...origins.keys()].sort((a, b) => a - b), [0, 1]);

  const anchors = lensAnchors(origins);
  assert.strictEqual(anchors.length, 2, "one lens per generated function");
  assert.deepStrictEqual(anchors.map(a => a.line), [0, 1], "in source order");
  clearCache();
});

test("many lines feeding one function get a single lens, at the first of them", () => {
  clearCache();
  const { root, functions } = makePack();
  // Three generated lines, from source lines 0, 1 and 1 again: one loop, one function.
  writeMap(functions, "alpha", ["src/one.bolt"], "AAAA;AACA;AAAA");
  const maps = [path.join(functions, "alpha.mcfunction.map")];

  const anchors = lensAnchors(originLinesFor(maps, path.join(root, "src", "one.bolt")));
  assert.strictEqual(anchors.length, 1, "a lens per line would be twenty lenses on one function");
  assert.strictEqual(anchors[0].line, 0, "the first contributing line is where the lens belongs");
  clearCache();
});

test("a generated file is not a source, so it gets no lens of this kind", () => {
  clearCache();
  const { functions } = makePack();
  writeMap(functions, "alpha", ["src/one.bolt"], "AAAA");
  const maps = [path.join(functions, "alpha.mcfunction.map")];

  const origins = originLinesFor(maps, path.join(functions, "alpha.mcfunction"));
  assert.strictEqual(origins.size, 0);
  clearCache();
});

test("the index is keyed by file, so one file's lookup ignores every other map", () => {
  clearCache();
  const { root, functions } = makePack();
  for (let i = 0; i < 50; i++) writeMap(functions, `f${i}`, ["src/two.bolt"], "AAAA");
  writeMap(functions, "mine", ["src/one.bolt"], "AAAA");
  const maps = fs.readdirSync(functions).filter(f => f.endsWith(".map")).map(f => path.join(functions, f));

  const origins = originLinesFor(maps, path.join(root, "src", "one.bolt"));
  assert.strictEqual(origins.size, 1, "only this file's lines come back");
  assert.ok(origins.get(0)?.file.endsWith("mine.mcfunction"));
  clearCache();
});
