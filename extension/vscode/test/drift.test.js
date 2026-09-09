// @ts-check
"use strict";

// Following a line while the author moves it.
//
// The tracker is fed exactly what VS Code reports, so every case here is written as an edit
// made to a buffer rather than as a change record: `type`, `deleteLines` and `paste` build the
// record the way the editor does, including the one field it cannot state and the tracker has
// to read back off the result, whether anything of the last replaced line survived.
//
// The end-to-end cases at the bottom go through ./sourcemap, which is where the drift is
// applied: no consumer asks the tracker anything, they ask the maps and get lines that moved.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const drift = require("../src/drift");
const sourcemap = require("../src/sourcemap");

const FILE = path.resolve("/pack/src/link.py");

// A buffer, edited the way an editor edits one

/**
 * A document the tracker can be fed edits of, holding the text and reporting each change.
 * @param {string} text
 * @param {string} [file]
 */
function buffer(text, file = FILE) {
  let lines = text.split("\n");

  /** @param {{ start: [number, number], end: [number, number], text: string }[]} edits */
  function apply(edits) {
    // The editor reports the changes of one event from the end of the document backwards, and
    // each one's coordinates are read against the document before it is applied.
    const ordered = [...edits].sort((a, b) => b.start[0] - a.start[0] || b.start[1] - a.start[1]);
    const changes = ordered.map(edit => ({
      range: {
        start: { line: edit.start[0], character: edit.start[1] },
        end: { line: edit.end[0], character: edit.end[1] },
      },
      text: edit.text,
    }));
    for (const edit of ordered) {
      const head = lines.slice(0, edit.start[0]).concat(lines[edit.start[0]].slice(0, edit.start[1]));
      const tail = [lines[edit.end[0]].slice(edit.end[1])].concat(lines.slice(edit.end[0] + 1));
      const written = edit.text.split("\n");
      const middle = written.length === 1
        ? [head.pop() + written[0] + tail.shift()]
        : [head.pop() + written[0], ...written.slice(1, -1), written[written.length - 1] + tail.shift()];
      lines = [...head, ...middle, ...tail];
    }
    drift.noteChanges(file, changes, { lineCount: lines.length, lineAt: line => ({ text: lines[line] }) });
  }

  return {
    apply,
    /** @param {[number, number]} at @param {string} text */
    type(at, text) { apply([{ start: at, end: at, text }]); },
    /** @param {number} from @param {number} count  Whole lines, as ctrl+x takes them. */
    deleteLines(from, count) { apply([{ start: [from, 0], end: [from + count, 0], text: "" }]); },
    get lines() { return lines.slice(); },
  };
}

/** Where each of a file's lines sits now, `null` for the ones that are gone.
 *  @param {number[]} at @param {string} [file] */
function nowAt(at, file = FILE) {
  return at.map(line => drift.currentLineOf(file, line));
}

// The edits

test("typing inside a line moves nothing, and costs no table", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c");
  doc.type([1, 4], "bb");

  assert.deepEqual(nowAt([0, 1, 2]), [0, 1, 2]);
  assert.equal(drift.size(), 0, "a file whose lines have not moved is not followed at all");
});

test("a line typed above pushes the lines below it down", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c");
  doc.type([1, 0], "say new\n");

  assert.deepEqual(doc.lines, ["say a", "say new", "say b", "say c"]);
  assert.deepEqual(nowAt([0, 1, 2]), [0, 2, 3]);
});

test("enter at the end of a line leaves it where it is", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c");
  doc.type([0, 5], "\n");

  assert.deepEqual(nowAt([0, 1, 2]), [0, 2, 3]);
});

test("enter in the middle of a line keeps the line on its head", () => {
  drift.clear();
  const doc = buffer("say a\nsay bbb\nsay c");
  doc.type([1, 4], "\n");

  assert.deepEqual(doc.lines, ["say a", "say ", "bbb", "say c"]);
  assert.deepEqual(nowAt([0, 1, 2]), [0, 1, 3]);
});

test("a deleted line is gone, and the ones below it come up", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c\nsay d");
  doc.deleteLines(1, 1);

  assert.deepEqual(doc.lines, ["say a", "say c", "say d"]);
  assert.deepEqual(nowAt([0, 1, 2, 3]), [0, null, 1, 2]);
});

test("a deleted block takes every line inside it and no other", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c\nsay d\nsay e");
  doc.deleteLines(1, 3);

  assert.deepEqual(doc.lines, ["say a", "say e"]);
  assert.deepEqual(nowAt([0, 1, 2, 3, 4]), [0, null, null, null, 1]);
});

test("joining two lines keeps the first and drops the second", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c");
  doc.apply([{ start: [0, 5], end: [1, 0], text: "" }]); // backspace at the start of line 1

  assert.deepEqual(doc.lines, ["say asay b", "say c"]);
  assert.deepEqual(nowAt([0, 1, 2]), [0, null, 1]);
});

test("emptying a line without deleting it leaves nothing to point at", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c");
  doc.apply([{ start: [1, 0], end: [1, 5], text: "" }]);

  assert.deepEqual(doc.lines, ["say a", "", "say c"]);
  assert.deepEqual(nowAt([0, 1, 2]), [0, null, 2], "the command that was on it is not there any more");
});

test("pasting a block pushes everything below it down", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c");
  doc.type([1, 0], "one\ntwo\nthree\n");

  assert.deepEqual(nowAt([0, 1, 2]), [0, 4, 5]);
  assert.deepEqual([1, 2, 3].map(line => drift.buildLineOf(FILE, line)), [null, null, null],
    "the pasted lines came from no build");
});

test("replacing a selection that spans lines keeps the ends and loses the middle", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c\nsay d");
  doc.apply([{ start: [1, 4], end: [2, 4], text: "X" }]);

  assert.deepEqual(doc.lines, ["say a", "say Xc", "say d"]);
  assert.deepEqual(nowAt([0, 1, 2, 3]), [0, 1, null, 2]);
});

test("two cursors deleting two lines in one event move the rest once", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c\nsay d\nsay e");
  doc.apply([
    { start: [1, 0], end: [2, 0], text: "" },
    { start: [3, 0], end: [4, 0], text: "" },
  ]);

  assert.deepEqual(doc.lines, ["say a", "say c", "say e"]);
  assert.deepEqual(nowAt([0, 1, 2, 3, 4]), [0, null, 1, null, 2]);
});

test("two cursors typing a line each keep both sides in step", () => {
  drift.clear();
  const doc = buffer("say a\nsay b\nsay c");
  doc.apply([
    { start: [0, 0], end: [0, 0], text: "# one\n" },
    { start: [2, 0], end: [2, 0], text: "# two\n" },
  ]);

  assert.deepEqual(doc.lines, ["# one", "say a", "say b", "# two", "say c"]);
  assert.deepEqual(nowAt([0, 1, 2]), [1, 2, 4]);
});

// Lines that move rather than shift, which no arithmetic on line numbers can follow

test("a line moved with alt+down takes its identity with it", () => {
  drift.clear();
  const doc = buffer("l0\nwrite a\nwrite b\nl3");
  doc.type([0, 2], "!");  // the buffer is what the tracker learns from the first edit it sees
  // One edit replacing two lines with the same two, swapped, which is what moving a line is.
  doc.apply([{ start: [1, 0], end: [2, 7], text: "write b\nwrite a" }]);

  assert.deepEqual(doc.lines, ["l0!", "write b", "write a", "l3"]);
  assert.deepEqual(nowAt([0, 1, 2, 3]), [0, 2, 1, 3]);
});

test("a block indented into a branch is followed, since only the text matters", () => {
  drift.clear();
  const doc = buffer("l0\nwrite a\nwrite b\nl3");
  doc.type([0, 2], "!");
  doc.apply([{ start: [1, 0], end: [2, 7], text: "\twrite a\n\twrite b" }]);

  assert.deepEqual(doc.lines, ["l0!", "\twrite a", "\twrite b", "l3"]);
  assert.deepEqual(nowAt([0, 1, 2, 3]), [0, 1, 2, 3]);
});

test("a blank line matches nothing, however many of them a change writes", () => {
  drift.clear();
  const doc = buffer("l0\nwrite a\n\nl3");
  doc.type([0, 2], "!");
  doc.apply([{ start: [1, 0], end: [2, 0], text: "\n\n" }]);

  assert.deepEqual(doc.lines, ["l0!", "", "", "", "l3"]);
  assert.deepEqual(nowAt([1, 2]), [null, null], "the command is gone, and no blank line inherits it");
});

test("the two directions agree on every line that survived", () => {
  drift.clear();
  const doc = buffer("l0\nl1\nl2\nl3\nl4\nl5");
  doc.deleteLines(1, 2);
  doc.type([2, 0], "new\n");

  assert.deepEqual(doc.lines, ["l0", "l3", "new", "l4", "l5"]);
  for (const built of [0, 3, 4, 5]) {
    const now = drift.currentLineOf(FILE, built);
    assert.notEqual(now, null, `line ${built} should still be somewhere`);
    assert.equal(drift.buildLineOf(FILE, /** @type {number} */ (now)), built);
  }
  assert.deepEqual(nowAt([1, 2]), [null, null]);
  assert.equal(drift.buildLineOf(FILE, 2), null, "the line typed since came from no build");
});

// Saves, builds and closes

test("a build rebases on what was saved, not on what is in the buffer", () => {
  drift.clear();
  const doc = buffer("l0\nl1\nl2\nl3");
  doc.deleteLines(0, 1);        // saved, and then built
  drift.noteSave(FILE);
  doc.type([0, 0], "new\n");    // typed after the save, so no build has seen it

  drift.rebase();
  assert.deepEqual(nowAt([0, 1, 2]), [1, 2, 3],
    "the build read the saved file, and only the unsaved line still shifts it");
});

test("a build after a save forgets the file entirely", () => {
  drift.clear();
  const doc = buffer("l0\nl1\nl2");
  doc.deleteLines(0, 1);
  drift.noteSave(FILE);
  drift.rebase();

  assert.equal(drift.size(), 0);
  assert.deepEqual(nowAt([0, 1, 2]), [0, 1, 2], "the maps and the file agree again");
});

test("closing a document without saving gives back the saved lines", () => {
  drift.clear();
  const doc = buffer("l0\nl1\nl2\nl3");
  doc.deleteLines(1, 1);        // saved: the file on disk is now l0, l2, l3
  drift.noteSave(FILE);
  doc.deleteLines(0, 2);        // not saved

  assert.deepEqual(nowAt([0, 1, 2, 3]), [null, null, null, 0]);
  drift.noteClose(FILE);
  assert.deepEqual(nowAt([0, 1, 2, 3]), [0, null, 1, 2], "the unsaved deletion died with the buffer");
});

test("forgetting a file answers as if it had never moved", () => {
  drift.clear();
  const doc = buffer("l0\nl1\nl2");
  doc.deleteLines(0, 1);
  drift.forget(FILE);

  assert.deepEqual(nowAt([0, 1, 2]), [0, 1, 2]);
});

test("one file's edits leave the others alone", () => {
  drift.clear();
  const other = path.resolve("/pack/src/other.py");
  buffer("l0\nl1\nl2", other).deleteLines(0, 1);

  assert.deepEqual(nowAt([0, 1, 2]), [0, 1, 2]);
  assert.deepEqual(nowAt([0, 1, 2], other), [null, 0, 1]);
});

// Through the maps, which is where every consumer meets it

/** A generated function whose map says its three lines came from source lines 3, 4 and 5. */
function writePack() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-drift-"));
  const functions = path.join(root, "build", "data", "ns", "function");
  fs.mkdirSync(functions, { recursive: true });
  fs.mkdirSync(path.join(root, "src"), { recursive: true });

  const source = path.join(root, "src", "link.py");
  fs.writeFileSync(source, [...Array(8).keys()].map(i => `line ${i}`).join("\n"));
  const generated = path.join(functions, "alpha.mcfunction");
  fs.writeFileSync(generated, "say a\nsay b\nsay c\n");
  fs.writeFileSync(`${generated}.map`, JSON.stringify({
    version: 3, file: "alpha.mcfunction", sourceRoot: "../../../..",
    sources: ["src/link.py"], names: [], mappings: "AAGA;AACA;AACA",
  }));
  return { source, generated, mapPath: `${generated}.map` };
}

test("the maps answer where a line is now, not where the build left it", () => {
  drift.clear();
  sourcemap.clearCache();
  const { source, generated, mapPath } = writePack();
  assert.deepEqual(sourcemap.originOf(generated, 0), { file: source, line: 3, column: 0 });

  buffer("", source); // the tracker is fed the real file below
  const doc = buffer(fs.readFileSync(source, "utf8"), source);
  doc.deleteLines(0, 2);

  assert.equal(sourcemap.originOf(generated, 0)?.line, 1, "two lines above it went");
  assert.deepEqual([...sourcemap.originLinesFor([mapPath], source).keys()], [1, 2, 3]);
  assert.deepEqual(sourcemap.generatedFrom([mapPath], source, 1), [{ file: generated, line: 0 }]);
  drift.clear();
  sourcemap.clearCache();
});

test("a line the author deleted stops answering, rather than answering a neighbour", () => {
  drift.clear();
  sourcemap.clearCache();
  const { source, generated, mapPath } = writePack();

  buffer(fs.readFileSync(source, "utf8"), source).deleteLines(3, 1); // the origin of line 0

  assert.equal(sourcemap.originOf(generated, 0), null, "no lens, no jump, no diagnostic on it");
  assert.equal(sourcemap.originsOf(generated).length, 0);
  assert.deepEqual([...sourcemap.originLinesFor([mapPath], source).keys()], [3, 4],
    "the two lines that survived still lead to what they wrote");
  drift.clear();
  sourcemap.clearCache();
});

test("a rebuild of the same file goes back to reading the map as it is", () => {
  drift.clear();
  sourcemap.clearCache();
  const { source, generated } = writePack();

  const doc = buffer(fs.readFileSync(source, "utf8"), source);
  doc.deleteLines(0, 2);
  drift.noteSave(source);
  drift.rebase();

  assert.equal(sourcemap.originOf(generated, 0)?.line, 3,
    "the new map is written against the new file, so nothing is applied on top of it");
  drift.clear();
  sourcemap.clearCache();
});
