// @ts-check
"use strict";

// The pure half of the lens providers: where a lens goes and what it is called.
//
// `functionIdOf` and `targetOfBlock` predate this file and were never tested, which is what
// pulling them out of codelens.js into a module with no vscode import made possible.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");

const { functionIdOf, targetOfBlock, lensAnchors } = require("../src/lenses");

// Naming the target

test("a generated path is named as the resource location it spells", () => {
  assert.equal(functionIdOf("/p/build/pack/data/ns/function/foo/bar.mcfunction"), "ns:foo/bar");
  assert.equal(functionIdOf("/p/build/pack/data/ns/function/top.mcfunction"), "ns:top");
});

test("the pre-1.21 folder name is read too", () => {
  assert.equal(functionIdOf("/p/build/pack/data/ns/functions/foo.mcfunction"), "ns:foo",
    "a pack built for an older format spells it in the plural");
});

test("backslashes are read the same as forward slashes", () => {
  assert.equal(functionIdOf("D:\\p\\build\\pack\\data\\ns\\function\\foo\\bar.mcfunction"), "ns:foo/bar");
});

test("the last data segment wins, so a project called data does not confuse it", () => {
  assert.equal(functionIdOf("/data/build/pack/data/ns/function/x.mcfunction"), "ns:x");
});

test("a layout the convention does not cover falls back to the file name", () => {
  for (const odd of ["/p/somewhere/else.mcfunction", "/p/data/function/x.mcfunction", "/p/data/ns/x.mcfunction"]) {
    assert.equal(functionIdOf(odd), path.basename(odd), `should fall back: ${odd}`);
  }
});

// Choosing the line a block's lens sits on

/** A stand-in for a TextDocument, which is all targetOfBlock touches. */
function docOf(text) {
  return { positionAt: (/** @type {number} */ offset) => ({ line: text.slice(0, offset).split("\n").length - 1 }) };
}

test("a block whose call line was recorded uses that line", () => {
  const origins = new Map([[7, { file: "/gen/a.mcfunction", line: 0 }]]);
  const found = targetOfBlock(origins, docOf("x\n".repeat(20)), { start: 0, end: 4 }, 7);
  assert.equal(found?.file, "/gen/a.mcfunction", "the call line is where the map records a variable write");
});

test("a block written inline is found through its own lines", () => {
  // Nothing on the call line 0, but line 2 is inside the block and was recorded.
  const origins = new Map([[2, { file: "/gen/b.mcfunction", line: 5 }]]);
  const text = "call(\nsay a\nsay b\n)\n";
  const found = targetOfBlock(origins, docOf(text), { start: 0, end: text.length - 1 }, 0);
  assert.equal(found?.file, "/gen/b.mcfunction");
});

test("the call line wins over a line inside the block", () => {
  const origins = new Map([
    [0, { file: "/gen/call.mcfunction", line: 0 }],
    [2, { file: "/gen/inside.mcfunction", line: 0 }],
  ]);
  const text = "call(\nsay a\nsay b\n)\n";
  const found = targetOfBlock(origins, docOf(text), { start: 0, end: text.length - 1 }, 0);
  assert.equal(found?.file, "/gen/call.mcfunction");
});

test("a block that produced nothing gets no target", () => {
  const text = "call(\nsay a\n)\n";
  assert.equal(targetOfBlock(new Map(), docOf(text), { start: 0, end: text.length - 1 }, 0), null,
    "no build means no lens, rather than a lens that leads nowhere");
});

// Grouping, which is what keeps a bolt file readable

test("anchors are sorted by line whatever order the map is read in", () => {
  const origins = new Map([
    [9, { file: "/gen/c.mcfunction", line: 0 }],
    [1, { file: "/gen/a.mcfunction", line: 0 }],
    [5, { file: "/gen/b.mcfunction", line: 0 }],
  ]);
  assert.deepEqual(lensAnchors(origins).map(a => a.line), [1, 5, 9]);
});

test("the earliest line wins for a target, whatever order it is seen in", () => {
  const origins = new Map([
    [9, { file: "/gen/a.mcfunction", line: 3 }],
    [2, { file: "/gen/a.mcfunction", line: 0 }],
    [5, { file: "/gen/a.mcfunction", line: 1 }],
  ]);
  const anchors = lensAnchors(origins);
  assert.equal(anchors.length, 1);
  assert.equal(anchors[0].line, 2, "the lens belongs at the top of what the file wrote, not in the middle");
});

test("no origins means no anchors", () => {
  assert.deepEqual(lensAnchors(new Map()), []);
});
