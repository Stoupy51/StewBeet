// @ts-check
"use strict";

const { test } = require("node:test");
const assert = require("node:assert/strict");

const { findBlockOffsets, findInterpolationSpans } = require("../src/blocks");
const { project, virtualPath, blockIndexFromPath, sanitizeName } = require("../src/projection");

/** Project the first block of a Python source, masking its interpolations. */
function projectFirstBlock(text) {
  const [block] = findBlockOffsets(text);
  assert.ok(block, "expected the fixture to contain a block");
  return project(text, block.start, block.end, findInterpolationSpans(text, block));
}

// ─── findInterpolationSpans──

test("plain string has no interpolation spans", () => {
  const text = 'write_function("ns:p", """\nsay hi\n""")';
  const [block] = findBlockOffsets(text);
  assert.deepEqual(findInterpolationSpans(text, block), []);
});

test("single interpolation span covers its braces", () => {
  const text = 'write_tick_file(f"say {name}")';
  const [block] = findBlockOffsets(text);
  const [span] = findInterpolationSpans(text, block);
  assert.equal(text.slice(span.start, span.end), "{name}");
});

test("nested braces stay inside one span", () => {
  const text = 'write_tick_file(f"say {d[\'k\'] + f(1)}")';
  const [block] = findBlockOffsets(text);
  const spans = findInterpolationSpans(text, block);
  assert.equal(spans.length, 1);
  assert.equal(text.slice(spans[0].start, spans[0].end), "{d['k'] + f(1)}");
});

test("literal double brace is not an interpolation", () => {
  const text = 'write_tick_file(f"summon pig ~ ~ ~ {{Tags:[a]}}")';
  const [block] = findBlockOffsets(text);
  assert.deepEqual(findInterpolationSpans(text, block), []);
});

test("interpolation containing a quoted string is one span", () => {
  const text = 'write_function("ns:p", f"""\nsay {obj.get(\'key\')}\n""")';
  const [block] = findBlockOffsets(text);
  const spans = findInterpolationSpans(text, block);
  assert.equal(spans.length, 1);
  assert.equal(text.slice(spans[0].start, spans[0].end), "{obj.get('key')}");
});

test("several interpolations produce sorted non-overlapping spans", () => {
  const text = 'write_tick_file(f"scoreboard players set {a} {b} 1")';
  const [block] = findBlockOffsets(text);
  const spans = findInterpolationSpans(text, block);
  assert.equal(spans.length, 2);
  assert.ok(spans[0].end <= spans[1].start);
});

// ─── Offset identity─────────
// The property the whole forwarding design rests on: a position in the Python
// document is the same position in the virtual one.

test("projection preserves total length", () => {
  const text = 'write_function("ns:p", """\nexecute as @a run say hi\n""")\nx = 1\n';
  assert.equal(projectFirstBlock(text).length, text.length);
});

test("projection preserves every newline position", () => {
  const text = 'write_function("ns:p", """\nsay a\nsay b\n""")\nother()\n';
  const out = projectFirstBlock(text);
  const positions = (/** @type {string} */ s) =>
    [...s].reduce((acc, c, i) => (c === "\n" ? [...acc, i] : acc), /** @type {number[]} */([]));
  assert.deepEqual(positions(out), positions(text));
});

test("block content is byte-identical inside the block", () => {
  const text = 'write_function("ns:p", """\nexecute as @a run say hi\n""")';
  const [block] = findBlockOffsets(text);
  const out = project(text, block.start, block.end, []);
  assert.equal(out.slice(block.start, block.end), text.slice(block.start, block.end));
});

test("everything outside the block becomes spaces or newlines", () => {
  const text = 'write_function("ns:p", """\nsay hi\n""")\nfoo = 2\n';
  const [block] = findBlockOffsets(text);
  const out = project(text, block.start, block.end, []);
  const outside = out.slice(0, block.start) + out.slice(block.end);
  assert.match(outside, /^[ \r\n]*$/);
});

test("interpolations are masked to underscores of the same width", () => {
  const text = 'write_tick_file(f"say {name}")';
  const out = projectFirstBlock(text);
  assert.equal(out.length, text.length);
  assert.ok(out.includes("say ______"), `expected masked interpolation, got: ${out}`);
  assert.ok(!out.includes("name"), "interpolation must not leak Python into the virtual document");
});

test("a multi-line interpolation keeps its newlines so line counts match", () => {
  const text = 'write_function("ns:p", f"""\nsay {foo(\n  1)}\n""")';
  const out = projectFirstBlock(text);
  assert.equal(out.length, text.length);
  assert.equal((out.match(/\n/g) || []).length, (text.match(/\n/g) || []).length);
});

// ─── Virtual URI paths───────

test("virtual path round-trips its block index", () => {
  for (const i of [0, 1, 7, 42]) {
    assert.equal(blockIndexFromPath(virtualPath(i, "demo.py")), i);
  }
});

test("virtual path ends in .mcfunction so VS Code assigns the language id", () => {
  assert.ok(virtualPath(0, "demo.py").endsWith(".mcfunction"));
});

test("unsafe base names are sanitised", () => {
  assert.equal(sanitizeName("a b/c"), "a_b_c");
  assert.equal(sanitizeName(""), "embedded");
});

test("blockIndexFromPath rejects a foreign path", () => {
  assert.equal(blockIndexFromPath("/nope/demo.mcfunction"), undefined);
});
