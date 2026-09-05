// @ts-check
"use strict";

// Pure projection of a Python buffer into a virtual mcfunction document, plus
// the virtual URI path helpers. Kept free of any "vscode" dependency so it can
// be unit-tested with plain Node (see test/projection.test.js).
//
// The coordinate rule: lines stay in lockstep, columns do not.
// One Python line is always one virtual line, so a line number means the same thing on both
// sides and the line-granular source maps keep working. Columns may differ, because an
// interpolation is replaced by what it resolved to and `{ns}` is not as wide as `simplenergy`.
// Every column crossing the boundary goes through toVirtual or toPython with the table
// project() returns; a line absent from that table has identical columns on both sides.

// Constants

const SCHEME = "stewbeet-mcfunction";

/** What an interpolation becomes when its value is unknown.
 *  Legal in resource locations, selector values, objectives and tags, so the masked token
 *  still parses as a plausible word in most argument positions. */
const MASK = "_";

// Projection

/**
 * Project a Python document into the mcfunction document Spyglass should see.
 *
 * Everything outside the block becomes a space, newlines are preserved everywhere, and each
 * interpolation becomes either what it resolved to in the build or a run of `MASK`.
 *
 * @param {string} text  The whole Python document.
 * @param {number} start  Offset of the block's opening quote (prefix included).
 * @param {number} end  Offset just past the block's closing quote.
 * @param {{ start:number, end:number }[]} [interpolationSpans]  Sorted, from findInterpolationSpans.
 * @param {Map<number, string> | null} [generatedLines]  Generated text per 0-based document line.
 * @returns {{ text: string, table: Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>, masked: Map<number, { start:number, end:number }[]> }}
 *   `masked` holds, per line, the virtual columns still covered by a `MASK` run. Nothing a
 *   parser says about those columns is about the author's text, so a consumer reporting
 *   diagnostics must ignore them.
 */
function project(text, start, end, interpolationSpans = [], generatedLines = null) {
  /** @type {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} */
  const table = new Map();
  /** @type {Map<number, { start:number, end:number }[]>} */
  const masked = new Map();
  const pieces = text.split("\n");
  const projected = [];
  let lineStart = 0;
  let spanIdx = 0;

  for (let line = 0; line < pieces.length; line++) {
    const piece = pieces[line];
    const carriage = piece.endsWith("\r");
    const body = carriage ? piece.slice(0, -1) : piece;
    const lineEnd = lineStart + body.length;

    while (spanIdx < interpolationSpans.length && interpolationSpans[spanIdx].end <= lineStart) spanIdx++;
    const touching = [];
    for (let k = spanIdx; k < interpolationSpans.length && interpolationSpans[k].start < lineEnd; k++) {
      touching.push(interpolationSpans[k]);
    }

    const maskedLine = maskLine(body, lineStart, start, end, touching);
    const present = clipToLine(touching, lineStart, lineEnd, start, end);
    const substituted = present.length === 0 ? maskedLine : substitute(
      maskedLine, generatedLines ? generatedLines.get(line) : undefined,
      containedSpans(touching, lineStart, lineEnd, start, end), present, line, table, masked);

    projected.push(substituted + (carriage ? "\r" : ""));
    lineStart += piece.length + 1;
  }

  return { text: projected.join("\n"), table, masked };
}

/**
 * One line with everything outside the block blanked and every interpolation masked.
 * @param {string} body  The line, without its newline or carriage return.
 * @param {number} lineStart  Document offset of the line's first character.
 * @param {number} start
 * @param {number} end
 * @param {{ start:number, end:number }[]} spans  Only those touching this line.
 */
function maskLine(body, lineStart, start, end, spans) {
  let out = "";
  for (let i = 0; i < body.length; i++) {
    const offset = lineStart + i;
    if (offset < start || offset >= end) { out += " "; continue; }
    out += spans.some(s => offset >= s.start && offset < s.end) ? MASK : body[i];
  }
  return out;
}

/**
 * The spans a line may substitute: entirely on this line and entirely inside the block.
 * A span crossing a line boundary keeps its mask, since replacing it would either move a
 * newline or collapse two Python lines into one, and no resource location is ever multi-line.
 * @param {{ start:number, end:number }[]} spans
 * @param {number} lineStart
 * @param {number} lineEnd
 * @param {number} start
 * @param {number} end
 * @returns {{ start:number, end:number }[]}  Line-local columns.
 */
function containedSpans(spans, lineStart, lineEnd, start, end) {
  return spans
    .filter(s => s.start >= lineStart && s.end <= lineEnd && s.start >= start && s.end <= end)
    .map(s => ({ start: s.start - lineStart, end: s.end - lineStart }));
}

/**
 * The part of every span that falls on this line, as line-local columns.
 * A span crossing a line boundary appears clipped on each line it touches, since its mask does.
 * @param {{ start:number, end:number }[]} spans
 * @param {number} lineStart
 * @param {number} lineEnd
 * @param {number} start
 * @param {number} end
 * @returns {{ start:number, end:number }[]}
 */
function clipToLine(spans, lineStart, lineEnd, start, end) {
  const clipped = [];
  for (const span of spans) {
    const from = Math.max(span.start, lineStart, start);
    const to = Math.min(span.end, lineEnd, end);
    if (from < to) clipped.push({ start: from - lineStart, end: to - lineStart });
  }
  return clipped;
}

/**
 * Splice the resolved values into a masked line, recording the widths that changed and the
 * runs that stayed masked.
 * @param {string} masked
 * @param {string | undefined} generated  Absent when the build says nothing about this line.
 * @param {{ start:number, end:number }[]} spans  The substitutable ones, line-local and sorted.
 * @param {{ start:number, end:number }[]} present  Every span on the line, `spans` included.
 * @param {number} line
 * @param {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} table  Written into.
 * @param {Map<number, { start:number, end:number }[]>} maskedRuns  Written into.
 */
function substitute(masked, generated, spans, present, line, table, maskedRuns) {
  const resolved = (generated === undefined ? null : resolveLine(masked, generated, spans)) ?? [];
  const byStart = new Map(resolved.map(entry => [entry.start, entry]));

  const changed = [];
  const stillMasked = [];
  let out = "";
  let cursor = 0;
  let delta = 0;

  for (const span of present) {
    out += masked.slice(cursor, span.start);
    cursor = span.end;

    const value = byStart.get(span.start);
    if (!value) {
      // Still a run of MASK. Its virtual columns are recorded so a consumer can tell that
      // anything the parser says about them is about our placeholder, not the author's text.
      out += masked.slice(span.start, span.end);
      stillMasked.push({ start: span.start + delta, end: span.end + delta });
      continue;
    }

    out += value.value;
    const width = span.end - span.start;
    if (value.value.length !== width) {
      changed.push({ start: span.start, pythonWidth: width, virtualWidth: value.value.length });
    }
    delta += value.value.length - width;
  }

  if (changed.length > 0) table.set(line, changed);
  if (stillMasked.length > 0) maskedRuns.set(line, stillMasked);
  return out + masked.slice(cursor);
}

/**
 * What each interpolation on a line resolved to, read off the line the build produced.
 *
 * Anchoring only: the literal text before a span and the literal text after it must both be
 * found where they belong, and whatever sits between them is the value. Nothing evaluates
 * Python. Leading and trailing whitespace is ignored on both sides, because a build is free
 * to strip a line's indentation.
 *
 * @param {string} pythonLine  The masked line, so its spans hold `MASK` runs.
 * @param {string} generatedLine  The line the build wrote for it.
 * @param {{ start:number, end:number }[]} spans  Line-local, sorted, non-overlapping.
 * @returns {{ start:number, end:number, value:string }[] | null}  null when the anchors disagree.
 */
function resolveLine(pythonLine, generatedLine, spans) {
  if (spans.length === 0) return [];
  if (generatedLine.includes("\n")) return null;

  const generated = generatedLine.trim();
  const lead = pythonLine.slice(0, spans[0].start).replace(/^[ \t]+/, "");
  if (!generated.startsWith(lead)) return null;

  const resolved = [];
  let cursor = lead.length;

  for (let i = 0; i < spans.length; i++) {
    const span = spans[i];
    if (i + 1 < spans.length) {
      const between = pythonLine.slice(span.end, spans[i + 1].start);
      if (between === "") return null; // two adjacent interpolations cannot be told apart
      const stop = generated.indexOf(between, cursor);
      if (stop === -1) return null;
      resolved.push({ start: span.start, end: span.end, value: generated.slice(cursor, stop) });
      cursor = stop + between.length;
      continue;
    }

    const tail = pythonLine.slice(span.end).replace(/[ \t]+$/, "");
    if (!generated.endsWith(tail)) return null;
    const stop = generated.length - tail.length;
    if (stop < cursor) return null;
    resolved.push({ start: span.start, end: span.end, value: generated.slice(cursor, stop) });
  }

  return resolved;
}

// Column translation

/**
 * The same position in the virtual document.
 * A position inside a substituted span lands on the span's start: there is no character-level
 * correspondence within one, since `{ns}` and `simplenergy` share no characters.
 * @param {{ line:number, character:number }} position
 * @param {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} table
 * @returns {{ line:number, character:number }}
 */
function toVirtual(position, table) {
  const spans = table.get(position.line);
  if (!spans) return position;

  let delta = 0;
  for (const span of spans) {
    if (position.character >= span.start + span.pythonWidth) {
      delta += span.virtualWidth - span.pythonWidth;
      continue;
    }
    if (position.character > span.start) return { line: position.line, character: span.start + delta };
    break;
  }
  return { line: position.line, character: position.character + delta };
}

/**
 * The same position back in the Python document.
 * @param {{ line:number, character:number }} position
 * @param {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} table
 * @returns {{ line:number, character:number }}
 */
function toPython(position, table) {
  const spans = table.get(position.line);
  if (!spans) return position;

  let delta = 0;
  for (const span of spans) {
    const virtualStart = span.start + delta;
    if (position.character >= virtualStart + span.virtualWidth) {
      delta += span.virtualWidth - span.pythonWidth;
      continue;
    }
    if (position.character > virtualStart) return { line: position.line, character: span.start };
    break;
  }
  return { line: position.line, character: position.character - delta };
}

/**
 * Whether a diagnostic at this position is about a `MASK` run rather than the author's text.
 *
 * The test is where the range **starts**, not whether it overlaps. A parser complaining at the
 * placeholder points at it, so its range starts inside the run. A parser complaining about a
 * real mistake earlier in the line points there, and its range may well run past a mask on its
 * way to the end of the line: `execute store reslt score #height {ns}.data` is a typo the
 * author wants flagged, and an overlap test throws it away along with the placeholder noise.
 *
 * @param {{ line:number, character:number }} start  Where the diagnostic points.
 * @param {Map<number, { start:number, end:number }[]>} masked  Virtual columns, per line.
 */
function describesMask(start, masked) {
  const runs = masked.get(start.line);
  return runs ? runs.some(run => start.character >= run.start && start.character < run.end) : false;
}

/**
 * Whether a virtual range overlaps a substituted span, so no honest Python range exists for it.
 * An edit carrying such a range is dropped rather than translated: it would overwrite
 * characters the author never asked to replace.
 * @param {{ line:number, character:number }} start
 * @param {{ line:number, character:number }} end
 * @param {Map<number, { start:number, pythonWidth:number, virtualWidth:number }[]>} table
 */
function crossesSubstitution(start, end, table) {
  for (let line = start.line; line <= end.line; line++) {
    const spans = table.get(line);
    if (!spans) continue;
    const from = line === start.line ? start.character : 0;
    const to = line === end.line ? end.character : Number.MAX_SAFE_INTEGER;

    let delta = 0;
    for (const span of spans) {
      const virtualStart = span.start + delta;
      if (from < virtualStart + span.virtualWidth && to > virtualStart) return true;
      delta += span.virtualWidth - span.pythonWidth;
    }
  }
  return false;
}

// Virtual URIs

/**
 * Strip anything that has no business in a URI path segment.
 * @param {string} name
 */
function sanitizeName(name) {
  const cleaned = name.replace(/[^A-Za-z0-9._-]/g, "_");
  return cleaned || "embedded";
}

/**
 * Build the path of a virtual document's URI.
 * The trailing ".mcfunction" is load-bearing: VS Code derives a document's
 * language id from its path extension, and that language id is what makes
 * Spyglass's document selector match.
 * @param {number} blockIndex
 * @param {string} baseName  Base name of the originating Python file.
 * @returns {string}
 */
function virtualPath(blockIndex, baseName) {
  return `/${blockIndex}/${sanitizeName(baseName)}.mcfunction`;
}

/**
 * Recover the block index from a virtual document's URI path.
 * @param {string} path
 * @returns {number | undefined}
 */
function blockIndexFromPath(path) {
  const m = /^\/(\d+)\//.exec(path);
  return m ? Number(m[1]) : undefined;
}

module.exports = {
  SCHEME,
  MASK,
  project,
  clipToLine,
  resolveLine,
  toVirtual,
  toPython,
  describesMask,
  crossesSubstitution,
  sanitizeName,
  virtualPath,
  blockIndexFromPath,
};
