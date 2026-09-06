// @ts-check
"use strict";

// Resource locations inside a generated file's header comments. The vscode-facing half (the
// link and lens providers) needs the extension host; this covers the scanning and resolution,
// which is where a wrong answer would send the reader to the wrong file.

const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const { resolveFunction, linksIn } = require("../src/headers");

/** A throwaway pack holding one function, so existence checks have something to find. */
function pack() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-headers-"));
  const dir = path.join(root, "data", "simplenergy", "function", "v2.0.27", "load");
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "main.mcfunction"), "say main\n");
  fs.writeFileSync(path.join(dir, "secondary.mcfunction"), "say secondary\n");
  return { root, secondary: path.join(dir, "secondary.mcfunction") };
}

const HEADER = [
  "#> simplenergy:v2.0.27/load/secondary",
  "#",
  "# @within\tsimplenergy:v2.0.27/load/main",
  "#",
  "",
  "function simplenergy:v2.0.27/load/main",
].join("\n");

test("a resource location in a header resolves to the file it names", () => {
  const { root, secondary } = pack();
  assert.strictEqual(
    resolveFunction(secondary, "simplenergy", "v2.0.27/load/main"),
    path.normalize(path.join(root, "data/simplenergy/function/v2.0.27/load/main.mcfunction")));
});

test("a resource location naming no real file resolves to null", () => {
  const { secondary } = pack();
  assert.strictEqual(resolveFunction(secondary, "simplenergy", "does/not/exist"), null);
  assert.strictEqual(resolveFunction(secondary, "nosuchnamespace", "v2.0.27/load/main"), null);
});

test("a path outside a datapack resolves to null rather than guessing", () => {
  assert.strictEqual(resolveFunction("/tmp/loose.mcfunction", "ns", "p"), null);
});

test("both @within and the file's own name become links", () => {
  const { secondary } = pack();
  const links = linksIn(HEADER, secondary);
  assert.deepStrictEqual(links.map(l => l.line), [0, 2], "the #> line and the @within line");
});

test("the link covers exactly the resource location, not the whole comment", () => {
  const { secondary } = pack();
  const within = linksIn(HEADER, secondary).find(l => l.line === 2);
  assert.ok(within);
  const line = HEADER.split("\n")[2];
  assert.strictEqual(line.slice(within.start, within.end), "simplenergy:v2.0.27/load/main");
});

test("commands outside comments are left to Spyglass", () => {
  const { secondary } = pack();
  // Line 5 is a real `function` command. Spyglass already makes that one navigable, and two
  // providers claiming the same range is how a link ends up pointing at the wrong place.
  assert.strictEqual(linksIn(HEADER, secondary).some(l => l.line === 5), false);
});

test("prose containing a colon does not become a link", () => {
  const { secondary } = pack();
  assert.deepStrictEqual(linksIn("# note: see the docs\n# TODO: fix this\n", secondary), []);
});

test("CRLF headers scan the same as LF ones", () => {
  const { secondary } = pack();
  assert.deepStrictEqual(
    linksIn(HEADER.replace(/\n/g, "\r\n"), secondary).map(l => l.line),
    linksIn(HEADER, secondary).map(l => l.line));
});
