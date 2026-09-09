// @ts-check
"use strict";

// Where a source line the build recorded sits now, after the edits made since.
//
// A `.mcfunction.map` names the line a command was written on when the build ran, and the
// author keeps typing afterwards. Three lines deleted above a `write_function` and every lens,
// every relayed diagnostic and every resolved interpolation on it points three lines too low
// until the next build. This keeps one small table per source file, moved by the edits VS Code
// reports, so a line is followed while it travels and answers null once it is gone: a consumer
// that gets null shows nothing, which is the only honest answer for a line that was deleted.
//
// Two tables, not one, and the useful one is the composition. `saved` holds where the lines of
// the file on disk are in the buffer now, and `atSave` where the lines of that file were when
// the build ran. A save makes the buffer the file, a build makes the file the map, and a close
// throws the buffer away, so each of the three moves one of the two and never both: an unsaved
// edit is not forgotten by someone else's rebuild, and a discarded buffer takes its own drift
// with it.
//
// Alongside them, the lines of each open file, because a moved line is a line no arithmetic can
// follow: alt+down reports one edit replacing two lines with the same two, swapped, and only
// their text says which is which.
//
// Deliberately free of any "vscode" dependency, like ./sourcemap.js: the tracking is a pure
// function of the changes, and that is the half worth testing.

const path = require("path");

// Constants

/** A current line no earlier line corresponds to, because it was typed since. */
const NEW = -1;

// State

/** @typedef {{ startLine:number, startChar:number, endLine:number, addedLines:number, writtenLength:number, movedBy:number }} Change */
/** @typedef {{ saved:number[], atSave:number[], build:number[] | null, byBuild:Map<number, number> | null }} Table */

/** Tables per source file, created on its first moving edit and dropped once it drifts no more.
 *  A file absent from here has not moved, and every lookup on it is the identity.
 *  @type {Map<string, Table>} */
const tables = new Map();

/** The lines of each open source file, so a change can be asked what it replaced.
 *  VS Code holds the strings already and this holds the same ones, so it costs one array per
 *  open file and is what lets a moved line be recognised by its own text.
 *  @type {Map<string, string[]>} */
const buffers = new Map();

// Lookup

/**
 * The line a build line sits on now, or null when the edits since deleted it.
 * @param {string} file  Absolute path of the source file.
 * @param {number} buildLine  0-based, as the map records it.
 * @returns {number | null}
 */
function currentLineOf(file, buildLine) {
  const table = tables.get(fileKey(file));
  if (!table) return buildLine;
  if (!table.byBuild) table.byBuild = inverseOf(buildOf(table));
  return table.byBuild.get(buildLine) ?? null;
}

/**
 * The build line a current line came from, or null when it was typed since the build.
 * @param {string} file
 * @param {number} currentLine
 * @returns {number | null}
 */
function buildLineOf(file, currentLine) {
  const table = tables.get(fileKey(file));
  if (!table) return currentLine;
  const line = buildOf(table)[currentLine];
  return line === undefined || line === NEW ? null : line;
}

/** The build line of each current line, which is the one table nothing writes directly: a line
 *  is followed from the buffer to the file on disk, and from there to what the build read.
 *  @param {Table} table */
function buildOf(table) {
  if (!table.build) {
    table.build = table.saved.map(saved => (saved === NEW ? NEW : table.atSave[saved] ?? NEW));
  }
  return table.build;
}

/** Build line to current line, for the direction the array cannot answer by index.
 *  @param {number[]} lines */
function inverseOf(lines) {
  const byBuild = new Map();
  for (let current = 0; current < lines.length; current++) {
    if (lines[current] !== NEW) byBuild.set(lines[current], current);
  }
  return byBuild;
}

// Following the edits

/**
 * Take note of what one document's edits did to its lines.
 *
 * The changes of one event are reported against the document as it was before them, and are
 * applied from the end of the document backwards so that each one's coordinates still hold when
 * its turn comes. `doc` already holds the result of all of them, which is why each change also
 * carries how far the ones applied before it have since moved it.
 *
 * @param {string} file
 * @param {readonly { range: { start:{line:number,character:number}, end:{line:number,character:number} }, text:string }[]} changes
 * @param {{ lineCount:number, lineAt:(line:number) => { text:string } }} doc  After the changes.
 */
function noteChanges(file, changes, doc) {
  if (changes.length === 0) return;
  const shapes = shapesOf(changes);
  const key = fileKey(file);
  let table = tables.get(key);
  let text = buffers.get(key);

  // Typing inside a line moves nothing, which is most of what an author does, so a file that
  // has only been typed in is followed by its lines alone and answers every lookup untouched.
  if (!table && !shapes.every(isStill)) {
    const before = doc.lineCount - shapes.reduce((sum, shape) => sum + deltaOf(shape), 0);
    tables.set(key, table = {
      saved: identity(before), atSave: identity(before), build: null, byBuild: null,
    });
  }

  for (const shape of shapes) {
    const written = linesWritten(doc, shape);
    if (table && !isStill(shape)) {
      table.saved = applied(table.saved, shape, replacedIn(text, shape), written);
    }
    if (text) text = spliced(text, shape, written);
  }
  if (table) {
    table.build = null;
    table.byBuild = null;
  }
  // The remembered lines are only ever read against the buffer they came from, so a disagreement
  // about how many there are means it is no longer that buffer and they are read again.
  buffers.set(key, text && text.length === doc.lineCount ? text : allLines(doc));
}

/**
 * The lines the buffer held where a change landed, or none when the buffer is not remembered.
 * @param {string[] | undefined} text @param {Change} change
 */
function replacedIn(text, change) {
  return text ? text.slice(change.startLine, change.endLine + 1) : [];
}

/**
 * Remember a document's lines as it is opened, so its very first edit can already be followed.
 * @param {string} file
 * @param {{ lineCount:number, lineAt:(line:number) => { text:string } }} doc
 */
function noteOpen(file, doc) {
  buffers.set(fileKey(file), allLines(doc));
}

/**
 * The line-level shape of each change, in the order they are applied.
 * @param {readonly { range: { start:{line:number,character:number}, end:{line:number,character:number} }, text:string }[]} changes
 * @returns {Change[]}
 */
function shapesOf(changes) {
  const ordered = [...changes].sort((a, b) =>
    b.range.start.line - a.range.start.line || b.range.start.character - a.range.start.character);

  /** @type {Change[]} */
  const shapes = new Array(ordered.length);
  let movedBy = 0;
  for (let i = ordered.length - 1; i >= 0; i--) {
    const { range, text } = ordered[i];
    shapes[i] = {
      startLine: range.start.line,
      startChar: range.start.character,
      endLine: range.end.line,
      addedLines: countNewlines(text),
      writtenLength: text.length - (text.lastIndexOf("\n") + 1),
      movedBy,
    };
    movedBy += deltaOf(shapes[i]);
  }
  return shapes;
}

/** The lines a change left behind, read off the document it has already been applied to.
 *  @param {{ lineCount:number, lineAt:(line:number) => { text:string } }} doc @param {Change} change */
function linesWritten(doc, change) {
  const from = change.startLine + change.movedBy;
  const written = [];
  for (let line = from; line <= from + change.addedLines && line < doc.lineCount; line++) {
    written.push(doc.lineAt(line).text);
  }
  return written;
}

/**
 * The table one change leaves behind.
 *
 * The replaced lines become `addedLines + 1` new ones, of which at most two carry an identity
 * over by position: the first, when text of the first replaced line survives in front of the
 * change, and the last, when text of the last replaced line survives behind it. A line rewritten
 * from its first column keeps the identity of what followed the edit, which is what makes a line
 * pushed down by a newline typed in front of it stay the same line rather than become a new one.
 *
 * What position cannot answer, the text does, in `carriedByText`.
 *
 * @param {number[]} lines
 * @param {Change} change
 * @param {string[]} replaced  What the change took out, empty when the buffer is not remembered.
 * @param {string[]} written  What it left in place of them.
 * @returns {number[]}
 */
function applied(lines, change, replaced, written) {
  const { startLine, endLine, addedLines } = change;
  const head = change.startChar > 0;
  // Both ends only speak for different lines when the change spans several and leaves several
  // behind. Otherwise one line is being split, joined or rewritten in its middle, and it cannot
  // be in two places at once: the head keeps it, so a word typed inside a command moves nothing.
  const tail = tailSurvives(change, written) && (!head || (addedLines > 0 && startLine < endLine));

  /** @type {number[]} */
  const middle = new Array(addedLines + 1).fill(NEW);
  if (head) middle[0] = lines[startLine] ?? NEW;
  if (tail) middle[addedLines] = lines[endLine] ?? NEW;
  carriedByText(middle, lines, change, replaced, written);

  return [...lines.slice(0, startLine), ...middle, ...lines.slice(endLine + 1)];
}

/**
 * Whether anything of the last replaced line outlived the change.
 * What is left of it sits at the end of the line the change now ends on, so the answer is
 * whether that line is longer than what the change itself put there.
 * @param {Change} change @param {string[]} written
 */
function tailSurvives(change, written) {
  const last = written[change.addedLines];
  if (last === undefined) return false;
  return last.length > (change.addedLines === 0 ? change.startChar : 0) + change.writtenLength;
}

/**
 * Give every still-new line the identity of a replaced line holding the same text.
 *
 * Moving a line is a replacement of the block it moved inside, and no arithmetic on line numbers
 * can tell which of the new lines is which: alt+down on a `write_function` call reports one edit
 * replacing two lines with the same two, swapped. Their text says it, and indentation is ignored
 * so a block dragged into an `if` is still followed. A blank line matches nothing, since it
 * carries no command and there are too many of them, and an identity one end of the change has
 * already carried is never given a second home.
 *
 * @param {number[]} middle  Written into.
 * @param {number[]} lines
 * @param {Change} change
 * @param {string[]} replaced
 * @param {string[]} written
 */
function carriedByText(middle, lines, change, replaced, written) {
  if (replaced.length === 0) return;

  /** New lines still looking for an identity, by their text. @type {Map<string, number[]>} */
  const free = new Map();
  for (let index = 0; index < middle.length; index++) {
    if (middle[index] !== NEW) continue;
    const text = (written[index] ?? "").trim();
    if (!text) continue;
    const waiting = free.get(text);
    if (waiting) waiting.push(index);
    else free.set(text, [index]);
  }
  if (free.size === 0) return;

  const taken = new Set(middle.filter(line => line !== NEW));
  for (let index = 0; index < replaced.length; index++) {
    const line = lines[change.startLine + index];
    if (line === undefined || line === NEW || taken.has(line)) continue;
    const waiting = free.get(replaced[index].trim());
    if (!waiting || waiting.length === 0) continue;
    middle[/** @type {number} */ (waiting.shift())] = line;
    taken.add(line);
  }
}

/** One change applied to the remembered lines, so the next one can read what it replaced.
 *  A change writing as many lines as it took needs no new array, which is every keystroke and
 *  every line moved.
 *  @param {string[]} text @param {Change} change @param {string[]} written */
function spliced(text, change, written) {
  if (written.length !== change.endLine - change.startLine + 1) {
    return [...text.slice(0, change.startLine), ...written, ...text.slice(change.endLine + 1)];
  }
  for (let index = 0; index < written.length; index++) text[change.startLine + index] = written[index];
  return text;
}

/** @param {{ lineCount:number, lineAt:(line:number) => { text:string } }} doc */
function allLines(doc) {
  const lines = new Array(doc.lineCount);
  for (let line = 0; line < doc.lineCount; line++) lines[line] = doc.lineAt(line).text;
  return lines;
}

/** @param {Change} change */
function deltaOf(change) {
  return change.addedLines - (change.endLine - change.startLine);
}

/** Whether a change leaves every line where it was, which is what typing inside one does.
 *  @param {Change} change */
function isStill(change) {
  return change.addedLines === 0 && change.startLine === change.endLine && change.startChar > 0;
}

/** @param {string} text */
function countNewlines(text) {
  let count = 0;
  for (let i = text.indexOf("\n"); i !== -1; i = text.indexOf("\n", i + 1)) count++;
  return count;
}

// Milestones

/**
 * The buffer reached disk, so the next build reads exactly these lines.
 * @param {string} file
 */
function noteSave(file) {
  const table = tables.get(fileKey(file));
  if (!table) return;
  table.atSave = buildOf(table).slice();
  table.saved = identity(table.atSave.length);
  table.build = null;
  table.byBuild = null;
}

/**
 * The buffer is gone, so what disk holds is what the reader will see next.
 *
 * Called only for a document closed clean: an unsaved edit dies with the buffer, and the lines
 * that come back are the saved ones, which `atSave` already places against the build.
 *
 * @param {string} file
 */
function noteClose(file) {
  const key = fileKey(file);
  buffers.delete(key);
  const table = tables.get(key);
  if (!table) return;

  table.saved = identity(table.atSave.length);
  table.build = null;
  table.byBuild = null;
  if (isIdentity(table.atSave)) tables.delete(key);
}

/**
 * A build ran, so the maps now describe the files as they were last saved.
 * A file with no unsaved edit drifts no more and its table goes, which is what keeps this free
 * in the ordinary case: build, edit, save, build again, and nothing is kept between them.
 */
function rebase() {
  for (const [key, table] of tables) {
    if (isIdentity(table.saved)) { tables.delete(key); continue; }
    table.atSave = identity(table.atSave.length);
    table.build = null;
    table.byBuild = null;
  }
}

/** @param {string} file */
function forget(file) {
  tables.delete(fileKey(file));
  buffers.delete(fileKey(file));
}

/** Forget every file, for a reload and for the tests. */
function clear() {
  tables.clear();
  buffers.clear();
}

/** How many files are being followed, for the status command. */
function size() {
  return tables.size;
}

// Helpers

/** @param {number} count */
function identity(count) {
  const lines = new Array(Math.max(count, 0));
  for (let line = 0; line < lines.length; line++) lines[line] = line;
  return lines;
}

/** @param {number[]} lines */
function isIdentity(lines) {
  return lines.every((line, index) => line === index);
}

/** @param {string} file */
function fileKey(file) {
  return path.normalize(file).toLowerCase();
}

module.exports = {
  currentLineOf,
  buildLineOf,
  noteOpen,
  noteChanges,
  noteSave,
  noteClose,
  rebase,
  forget,
  clear,
  size,
};
