// @ts-check
"use strict";

const { test } = require("node:test");
const assert = require("node:assert/strict");

const { findBlockOffsets, findInterpolationSpans } = require("../src/blocks");
const {
  project, resolveLine, toVirtual, toPython, describesMask, crossesSubstitution,
  virtualPath, blockIndexFromPath, sanitizeName,
} = require("../src/projection");

/** Project the first block of a Python source, masking its interpolations. */
function projectFirstBlock(text) {
  const [block] = findBlockOffsets(text);
  assert.ok(block, "expected the fixture to contain a block");
  return project(text, block.start, block.end, findInterpolationSpans(text, block)).text;
}

// findInterpolationSpans

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

// Offset identity
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
  const out = project(text, block.start, block.end, []).text;
  assert.equal(out.slice(block.start, block.end), text.slice(block.start, block.end));
});

test("everything outside the block becomes spaces or newlines", () => {
  const text = 'write_function("ns:p", """\nsay hi\n""")\nfoo = 2\n';
  const [block] = findBlockOffsets(text);
  const out = project(text, block.start, block.end, []).text;
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

// Virtual URI paths

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

// resolveLine

/** Line-local spans of every `{...}` in a single line. @param {string} line */
function spansOf(line) {
  const spans = [];
  const re = /\{[^}]*\}/g;
  let m;
  while ((m = re.exec(line)) !== null) spans.push({ start: m.index, end: m.index + m[0].length });
  return spans;
}

/** Mask a single line the way project() does, so resolveLine sees what it expects. @param {string} line */
function mask(line) {
  return spansOf(line).reduce(
    (acc, s) => acc.slice(0, s.start) + "_".repeat(s.end - s.start) + acc.slice(s.end), line);
}

/** @param {string} pythonLine @param {string} generatedLine */
function resolve(pythonLine, generatedLine) {
  return resolveLine(mask(pythonLine), generatedLine, spansOf(pythonLine));
}

test("a single interpolation is read off the generated line", () => {
  assert.deepEqual(
    resolve("function {ns}:utils/foo", "function simplenergy:utils/foo"),
    [{ start: 9, end: 13, value: "simplenergy" }]);
});

test("an interpolation ending the line takes the rest of it", () => {
  assert.deepEqual(
    resolve("function {path}", "function simplenergy:utils/foo"),
    [{ start: 9, end: 15, value: "simplenergy:utils/foo" }]);
});

test("two interpolations are separated by the literal between them", () => {
  assert.deepEqual(
    resolve("scoreboard players set #a {obj} {n}", "scoreboard players set #a energy.storage 42"),
    [{ start: 26, end: 31, value: "energy.storage" }, { start: 32, end: 35, value: "42" }]);
});

test("a line with no interpolation resolves to nothing rather than failing", () => {
  assert.deepEqual(resolve("say hi", "say hi"), []);
});

test("indentation differences on either side do not break the anchors", () => {
  assert.deepEqual(
    resolve("\texecute if score #h {ns}.data matches 1..  ", "  execute if score #h simplenergy.data matches 1.."),
    [{ start: 21, end: 25, value: "simplenergy" }]);
});

test("a stale build is a mismatch, and a mismatch resolves to null", () => {
  assert.equal(resolve("function {ns}:utils/foo", "function simplenergy:utils/renamed"), null);
  assert.equal(resolve("function {ns}:utils/foo", "say something else entirely"), null);
});

test("adjacent interpolations cannot be told apart and resolve to null", () => {
  assert.equal(resolve("say {a}{b}", "say hello"), null);
});

test("a generated value spanning lines is refused", () => {
  assert.equal(resolve("function {ns}:foo", "function a\nb:foo"), null);
});

// Substitution

/** Project the first block of a Python source against a table of generated lines. */
function projectWith(text, generatedLines) {
  const [block] = findBlockOffsets(text);
  return project(text, block.start, block.end, findInterpolationSpans(text, block), new Map(generatedLines));
}

const INTERPOLATED = 'write_function(f"{ns}:p", f"""\nfunction {ns}:utils/foo\nsay done\n""")\nx = 1\n';

test("substituting a longer value keeps the line count", () => {
  const { text } = projectWith(INTERPOLATED, [[1, "function simplenergy:utils/foo"]]);
  assert.equal(text.split("\n").length, INTERPOLATED.split("\n").length);
  assert.match(text, /function simplenergy:utils\/foo/);
});

test("substituting keeps every line's content on its own line", () => {
  const { text } = projectWith(INTERPOLATED, [[1, "function simplenergy:utils/foo"]]);
  const lines = text.split("\n");
  assert.equal(lines[1], "function simplenergy:utils/foo");
  assert.equal(lines[2], "say done");
});

test("a line with no generated counterpart keeps its mask", () => {
  const { text, table } = projectWith(INTERPOLATED, []);
  assert.match(text, /function ____:utils\/foo/);
  assert.equal(table.size, 0);
});

test("a generated line that does not match keeps the mask too", () => {
  const { text, table } = projectWith(INTERPOLATED, [[1, "say nothing to do with it"]]);
  assert.match(text, /function ____:utils\/foo/);
  assert.equal(table.size, 0);
});

test("the table records only the spans whose width changed", () => {
  const { table } = projectWith(INTERPOLATED, [[1, "function simplenergy:utils/foo"]]);
  assert.deepEqual(table.get(1), [{ start: 9, pythonWidth: 4, virtualWidth: 11 }]);
  assert.equal(table.has(2), false, "an untouched line stays out of the table");
});

test("a same-width substitution needs no translation and stays out of the table", () => {
  const { text, table } = projectWith(INTERPOLATED, [[1, "function fooo:utils/foo"]]);
  assert.match(text, /function fooo:utils\/foo/);
  assert.equal(table.size, 0);
});

test("a multi-line interpolation is never substituted", () => {
  const text = 'write_function("ns:p", f"""\nsay {foo(\n  1)}\n""")';
  const out = projectWith(text, [[1, "say resolved"], [2, "say resolved"]]);
  assert.equal(out.text.length, text.length, "the mask keeps the offsets it always had");
  assert.equal(out.table.size, 0);
});

test("CRLF survives a substitution that changes a line's width", () => {
  const source = INTERPOLATED.replace(/\n/g, "\r\n");
  const { text } = projectWith(source, [[1, "function simplenergy:utils/foo"]]);
  assert.equal((text.match(/\r\n/g) || []).length, (source.match(/\r\n/g) || []).length);
  assert.equal(text.split("\r\n")[1], "function simplenergy:utils/foo");
});

// Column translation
// The round trip is the property that protects the user's buffer: a range that comes back
// from Spyglass and is applied as an edit must land where the author was actually typing.

const TABLE = new Map([[1, [{ start: 9, pythonWidth: 4, virtualWidth: 11 }]]]);

/** @param {number} character */
const at = (character) => ({ line: 1, character });

test("a column before the span is unchanged in both directions", () => {
  assert.deepEqual(toVirtual(at(3), TABLE), at(3));
  assert.deepEqual(toPython(at(3), TABLE), at(3));
});

test("a column after the span shifts by the width delta", () => {
  assert.deepEqual(toVirtual(at(13), TABLE), at(20));
  assert.deepEqual(toPython(at(20), TABLE), at(13));
});

test("a column inside the span collapses onto its start", () => {
  assert.deepEqual(toVirtual(at(11), TABLE), at(9));
  assert.deepEqual(toPython(at(14), TABLE), at(9));
});

test("toPython round-trips every column outside a span", () => {
  for (const character of [0, 5, 8, 9, 13, 14, 30]) {
    assert.deepEqual(toPython(toVirtual(at(character), TABLE), TABLE), at(character),
      `column ${character} must survive the round trip`);
  }
});

test("a column inside a span round-trips to the span start and stays there", () => {
  const once = toPython(toVirtual(at(11), TABLE), TABLE);
  assert.deepEqual(once, at(9));
  assert.deepEqual(toPython(toVirtual(once, TABLE), TABLE), at(9));
});

test("a line absent from the table is returned untouched", () => {
  assert.deepEqual(toVirtual({ line: 0, character: 7 }, TABLE), { line: 0, character: 7 });
  assert.deepEqual(toPython({ line: 0, character: 7 }, TABLE), { line: 0, character: 7 });
});

test("two spans on one line accumulate their deltas", () => {
  const table = new Map([[1, [
    { start: 4, pythonWidth: 3, virtualWidth: 5 },
    { start: 10, pythonWidth: 3, virtualWidth: 1 },
  ]]]);
  assert.deepEqual(toVirtual(at(7), table), at(9));
  assert.deepEqual(toVirtual(at(13), table), at(13));
  for (const character of [0, 4, 7, 9, 10, 13, 25]) {
    assert.deepEqual(toPython(toVirtual(at(character), table), table), at(character));
  }
});

test("crossesSubstitution catches a range covering a substituted span", () => {
  assert.equal(crossesSubstitution(at(9), at(20), TABLE), true);
  assert.equal(crossesSubstitution(at(0), at(30), TABLE), true);
  assert.equal(crossesSubstitution(at(14), at(16), TABLE), true);
});

// Diagnostics about the mask
// The rule has to separate two things that both touch a masked run: the parser complaining
// about the placeholder, which is noise, and the parser complaining about a real mistake on a
// line that happens to contain one, which is the whole point of having diagnostics.

// `execute store reslt score #height {ns}.data run data get entity @s Pos[1]`, where the typo
// stops the line matching what was built, so `{ns}` stays masked at columns 33 to 37.
const TYPO_LINE = new Map([[0, [{ start: 33, end: 37 }]]]);

test("a diagnostic pointing at the mask is about the mask", () => {
  assert.equal(describesMask({ line: 0, character: 33 }, TYPO_LINE), true);
  assert.equal(describesMask({ line: 0, character: 35 }, TYPO_LINE), true);
});

test("a typo earlier on the line is reported even though the line carries a mask", () => {
  // `reslt` sits at column 14. Its diagnostic runs to the end of the line and therefore
  // overlaps the mask, which is why an overlap test silently swallowed the error.
  assert.equal(describesMask({ line: 0, character: 14 }, TYPO_LINE), false);
});

test("a diagnostic just past the mask is about the text after it", () => {
  assert.equal(describesMask({ line: 0, character: 37 }, TYPO_LINE), false);
});

test("a line with no mask never suppresses anything", () => {
  assert.equal(describesMask({ line: 1, character: 35 }, TYPO_LINE), false);
  assert.equal(describesMask({ line: 0, character: 35 }, new Map()), false);
});

test("crossesSubstitution leaves a range clear of every span alone", () => {
  assert.equal(crossesSubstitution(at(0), at(9), TABLE), false);
  assert.equal(crossesSubstitution(at(20), at(30), TABLE), false);
  assert.equal(crossesSubstitution({ line: 0, character: 0 }, { line: 0, character: 40 }, TABLE), false);
});
