// @ts-check
"use strict";

// The caches under the map layer, which exist for speed and are only correct if they let go.
//
// A stale map is worse than a slow one: it sends the reader to a line the build no longer has.
// These tests are about letting go, not about being fast.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const sourcemap = require("../src/sourcemap");

/** A generated function with a sibling map, written fresh each time. */
function writePack(mappings, source = "src/one.bolt", body = "say generated\n") {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-cache-"));
  const functions = path.join(root, "build", "datapack", "data", "ns", "function");
  fs.mkdirSync(functions, { recursive: true });
  fs.mkdirSync(path.join(root, "src"), { recursive: true });
  fs.writeFileSync(path.join(root, "src", "one.bolt"), "say a\nsay b\nsay c\n");
  fs.writeFileSync(path.join(root, "src", "two.bolt"), "say d\n");

  const generated = path.join(functions, "alpha.mcfunction");
  fs.writeFileSync(generated, body);
  fs.writeFileSync(`${generated}.map`, JSON.stringify({
    version: 3, file: "alpha.mcfunction", sourceRoot: "../../../../..",
    sources: [source], names: [], mappings,
  }));
  return { root, generated, mapPath: `${generated}.map` };
}

test("a rebuilt map is read again after the cache is dropped", () => {
  sourcemap.clearCache();
  const { generated, mapPath } = writePack("AAAA"); // line 0 -> one.bolt line 0

  const before = sourcemap.originOf(generated, 0);
  assert.ok(before?.file.endsWith("one.bolt"), before?.file);
  assert.equal(before?.line, 0);

  // A rebuild moves the origin to line 2 and changes the source file.
  fs.writeFileSync(mapPath, JSON.stringify({
    version: 3, file: "alpha.mcfunction", sourceRoot: "../../../../..",
    sources: ["src/two.bolt"], names: [], mappings: "AAEA",
  }));
  sourcemap.clearCache();

  const after = sourcemap.originOf(generated, 0);
  assert.ok(after?.file.endsWith("two.bolt"), `still the old source: ${after?.file}`);
  assert.equal(after?.line, 2, "still the old line");
  sourcemap.clearCache();
});

test("the derived origins are dropped with the map they came from", () => {
  sourcemap.clearCache();
  const { generated, mapPath } = writePack("AAAA");
  assert.equal(sourcemap.originsOf(generated).length, 1);

  fs.writeFileSync(mapPath, JSON.stringify({
    version: 3, file: "alpha.mcfunction", sourceRoot: "../../../../..",
    sources: ["src/one.bolt", "src/two.bolt"], names: [], mappings: "AAAA;ACAA",
  }));
  sourcemap.clearCache();

  const origins = sourcemap.originsOf(generated);
  assert.equal(origins.length, 2, "a second source appeared and the memoised answer must not hide it");
  sourcemap.clearCache();
});

test("the reverse index is dropped with the maps", () => {
  sourcemap.clearCache();
  const { root, mapPath } = writePack("AAAA");
  const one = path.join(root, "src", "one.bolt");
  const two = path.join(root, "src", "two.bolt");
  assert.equal(sourcemap.originLinesFor([mapPath], one).size, 1);
  assert.equal(sourcemap.originLinesFor([mapPath], two).size, 0);

  fs.writeFileSync(mapPath, JSON.stringify({
    version: 3, file: "alpha.mcfunction", sourceRoot: "../../../../..",
    sources: ["src/two.bolt"], names: [], mappings: "AAAA",
  }));
  sourcemap.clearCache();

  assert.equal(sourcemap.originLinesFor([mapPath], one).size, 0, "the old source still claims the line");
  assert.equal(sourcemap.originLinesFor([mapPath], two).size, 1, "the new one does not");
  sourcemap.clearCache();
});

test("a deleted map stops answering", () => {
  sourcemap.clearCache();
  const { generated, mapPath } = writePack("AAAA");
  assert.ok(sourcemap.originOf(generated, 0));

  fs.unlinkSync(mapPath);
  fs.unlinkSync(generated); // the declared name is read off the function, so it goes too
  sourcemap.clearCache();

  assert.equal(sourcemap.originOf(generated, 0), null);
  assert.deepEqual(sourcemap.originsOf(generated), []);
  sourcemap.clearCache();
});

test("an unmapped line is never answered with a neighbour", () => {
  sourcemap.clearCache();
  // Lines 0 and 2 are mapped; line 1 is an empty group and must stay unknown (G3).
  const { generated } = writePack("AAAA;;AACA", "src/one.bolt", "say a\nsay b\nsay c\n");
  assert.ok(sourcemap.originOf(generated, 0));
  assert.equal(sourcemap.originOf(generated, 1), null, "G3: absent means unknown, never the line before");
  assert.ok(sourcemap.originOf(generated, 2));
  sourcemap.clearCache();
});

test("a map that is not valid JSON is ignored rather than thrown", () => {
  sourcemap.clearCache();
  const { generated, mapPath } = writePack("AAAA");
  fs.writeFileSync(mapPath, "{ this is not json");
  sourcemap.clearCache();

  assert.doesNotThrow(() => sourcemap.originOf(generated, 0));
  assert.equal(sourcemap.originOf(generated, 0), null);
  sourcemap.clearCache();
});

test("a map for a function that no longer exists resolves to nothing", () => {
  sourcemap.clearCache();
  const { root, generated } = writePack("AAAA");
  fs.rmSync(path.join(root, "src"), { recursive: true, force: true });
  sourcemap.clearCache();

  // The map still decodes, and the origin it names simply is not on disk any more. Reporting it
  // is correct: whether the file exists is the navigation layer's question, not the decoder's.
  const origin = sourcemap.originOf(generated, 0);
  assert.ok(origin, "the map is still readable");
  assert.equal(fs.existsSync(origin.file), false);
  sourcemap.clearCache();
});
