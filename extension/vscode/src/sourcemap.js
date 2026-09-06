// @ts-check
"use strict";

// Source Map v3 decoding and lookup, for the `.mcfunction.map` sidecars a build emits.
//
// Deliberately free of any "vscode" dependency, like ./projection.js: this file decodes a
// published format and knows nothing about StewBeet, so it stays testable under plain
// `node --test` and is reusable the day bolt or mecha emit maps of their own.
//
// The format and its guarantees are specified in
// specs/001-stewbeet-vscode-dx/contracts/source-map.md.

const fs = require("fs");
const path = require("path");

// Constants

const MAP_SUFFIX = ".mcfunction.map";

const SOURCE_MAPPING_URL = "## sourceMappingURL=";

/** The Source Map v3 alphabet, indexed by 6-bit group. */
const BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/** @type {Map<string, number>} */
const BASE64_INDEX = new Map([...BASE64].map((c, i) => [c, i]));

// Decoding

/**
 * Decode one base64 VLQ segment into its signed fields.
 * The sign travels in the least significant bit and each group carries a continuation bit.
 * @param {string} segment
 * @returns {number[]}
 */
function decodeVlq(segment) {
  const values = [];
  let accumulator = 0;
  let shift = 0;
  for (const char of segment) {
    const digit = BASE64_INDEX.get(char);
    if (digit === undefined) return [];
    accumulator += (digit & 31) << shift;
    if (digit & 32) {
      shift += 5;
    } else {
      values.push(accumulator & 1 ? -(accumulator >> 1) : accumulator >> 1);
      accumulator = 0;
      shift = 0;
    }
  }
  return values;
}

/**
 * Decode a source map's JSON into its line table.
 *
 * Every field is delta-encoded against the previous segment **in the file**, not within the
 * line, which is the detail a hand-rolled decoder gets wrong: it passes any fixture where each
 * line advances by one and fails the moment a segment moves to another source.
 *
 * A generated line with no origin emits an empty group and is absent from `lines` rather than
 * present with a null value, so a caller that finds nothing knows the line is unmapped (G3).
 *
 * @param {any} json  The parsed contents of a .mcfunction.map.
 * @returns {{ sources: string[], sourceRoot: string, lines: Map<number, { sourceIndex: number, sourceLine: number, sourceColumn: number }> }}
 */
function decode(json) {
  const sources = Array.isArray(json?.sources) ? json.sources : [];
  const sourceRoot = typeof json?.sourceRoot === "string" ? json.sourceRoot : "";
  const lines = new Map();
  if (typeof json?.mappings !== "string") return { sources, sourceRoot, lines };

  let sourceIndex = 0;
  let sourceLine = 0;
  let sourceColumn = 0;

  json.mappings.split(";").forEach((/** @type {string} */ group, /** @type {number} */ generatedLine) => {
    if (!group) return;
    const fields = decodeVlq(group);
    if (fields.length < 4) return;
    sourceIndex += fields[1];
    sourceLine += fields[2];
    sourceColumn += fields[3];
    lines.set(generatedLine, { sourceIndex, sourceLine, sourceColumn });
  });

  return { sources, sourceRoot, lines };
}

// Discovery

/**
 * Path of the map belonging to a generated function, or null when it has none.
 *
 * The `## sourceMappingURL=` comment on the function's last line is what the format specifies,
 * so it wins when present and lets a generator point the map somewhere other than the sibling.
 * The sibling name is the fallback, which is what a build without the comment looks like.
 *
 * @param {string} generatedPath  Absolute path of a .mcfunction file.
 * @returns {string | null}
 */
function mapPathFor(generatedPath) {
  const cached = resolvedMaps.get(generatedPath);
  if (cached !== undefined) return cached;

  const found = searchMapFor(generatedPath);
  resolvedMaps.set(generatedPath, found);
  return found;
}

/** Answers of mapPathFor, since the diagnostic relay asks it once per diagnostic per refresh.
 *  A remembered `null` is corrected when the map appears, because writing one drops the cache.
 *  @type {Map<string, string | null>} */
const resolvedMaps = new Map();

/** @param {string} generatedPath @returns {string | null} */
function searchMapFor(generatedPath) {
  const declared = declaredMapName(generatedPath);
  if (declared) {
    const resolved = path.resolve(path.dirname(generatedPath), declared);
    if (fs.existsSync(resolved)) return resolved;
  }
  const sibling = `${generatedPath}.map`;
  return fs.existsSync(sibling) ? sibling : null;
}

/**
 * The map named by the function's own `## sourceMappingURL=` last line, if it has one.
 * @param {string} generatedPath
 * @returns {string | null}
 */
function declaredMapName(generatedPath) {
  const lines = linesOf(generatedPath);
  if (!lines) return null;

  let index = lines.length - 1;
  while (index >= 0 && lines[index] === "") index--;
  const last = lines[index] ?? "";
  return last.startsWith(SOURCE_MAPPING_URL) ? last.slice(SOURCE_MAPPING_URL.length).trim() : null;
}

// Cache

/** How long a path's mtime is trusted without asking the filesystem again.
 *
 * A `statSync` costs around 65 microseconds, and every lookup here paid one: a lens pass over an
 * open file, or a diagnostic relay pass, makes hundreds in a burst and spent all of its time in
 * the kernel. The map watcher in extension.js already drops these caches when a build writes, so
 * the stat is only the backstop for a build the watcher cannot see, such as an output directory
 * outside the workspace. One second of staleness is what that backstop costs. */
const STAT_TTL_MS = 1000;

/** When each path was last stat'd, and what it said. @type {Map<string, { at: number, mtimeMs: number | null }>} */
const stats = new Map();

/**
 * The mtime of a path, asked of the filesystem at most once per `STAT_TTL_MS`.
 * @param {string} file
 * @returns {number | null} null when the file does not exist.
 */
function mtimeOf(file) {
  const now = Date.now();
  const cached = stats.get(file);
  if (cached && now - cached.at < STAT_TTL_MS) return cached.mtimeMs;

  let mtimeMs = null;
  try {
    mtimeMs = fs.statSync(file).mtimeMs;
  } catch {
    mtimeMs = null;
  }
  stats.set(file, { at: now, mtimeMs });
  return mtimeMs;
}

/** Decoded maps, keyed by map path, with the mtime they were decoded at. @type {Map<string, { mtimeMs: number, map: ReturnType<typeof decode> }>} */
const cache = new Map();

/**
 * The decoded map at `mapPath`, decoded once and reused until the file changes.
 * @param {string} mapPath
 * @returns {ReturnType<typeof decode> | null}
 */
function load(mapPath) {
  const mtimeMs = mtimeOf(mapPath);
  if (mtimeMs === null) {
    cache.delete(mapPath);
    return null;
  }
  const cached = cache.get(mapPath);
  if (cached && cached.mtimeMs === mtimeMs) return cached.map;

  try {
    const map = decode(JSON.parse(fs.readFileSync(mapPath, "utf8")));
    cache.set(mapPath, { mtimeMs, map });
    return map;
  } catch (e) {
    console.debug(`[StewBeet] could not read source map ${mapPath}`, e);
    return null;
  }
}

/** Decoded generated files, keyed by path, with the mtime they were read at.
 *  @type {Map<string, { mtimeMs: number, lines: string[] }>} */
const contents = new Map();

/**
 * The lines of a generated file, read once and reused until it changes.
 * @param {string} generatedPath
 * @returns {string[] | null}
 */
function linesOf(generatedPath) {
  const mtimeMs = mtimeOf(generatedPath);
  if (mtimeMs === null) {
    contents.delete(generatedPath);
    return null;
  }
  const cached = contents.get(generatedPath);
  if (cached && cached.mtimeMs === mtimeMs) return cached.lines;

  try {
    const lines = fs.readFileSync(generatedPath, "utf8").split("\n").map(line => line.replace(/\r$/, ""));
    contents.set(generatedPath, { mtimeMs, lines });
    return lines;
  } catch (e) {
    console.debug(`[StewBeet] could not read ${generatedPath}`, e);
    return null;
  }
}

/** Drop every decoded map, the reverse index built from them, and the generated text. */
function clearCache() {
  cache.clear();
  contents.clear();
  resolvedMaps.clear();
  origins.clear();
  stats.clear();
  reverseIndex = null;
}

// Lookup: generated to source

/**
 * Where a generated line came from, or null when that line has no origin.
 *
 * Never falls back to the nearest mapped line: guarantee G3 says a missing mapping means
 * "unknown origin", never "same as the previous one", and a confident wrong jump costs the
 * reader more than no jump at all.
 *
 * @param {string} generatedPath  Absolute path of the .mcfunction.
 * @param {number} line  0-based generated line.
 * @returns {{ file: string, line: number, column: number } | null}
 */
function originOf(generatedPath, line) {
  const mapPath = mapPathFor(generatedPath);
  if (!mapPath) return null;
  const map = load(mapPath);
  const entry = map?.lines.get(line);
  if (!map || !entry) return null;

  const source = map.sources[entry.sourceIndex];
  if (!source) return null;
  return {
    file: path.resolve(path.dirname(mapPath), map.sourceRoot, source),
    line: entry.sourceLine,
    column: entry.sourceColumn,
  };
}

/**
 * Every distinct origin contributing to a generated file, in generated order.
 *
 * One map carries several sources whenever a declaration and a developer's own append both
 * feed one function (G6), and a consumer offering navigation is expected to present all of
 * them rather than only the first.
 *
 * @param {string} generatedPath
 * @returns {{ file: string, line: number, column: number }[]}
 */
function originsOf(generatedPath) {
  const mapPath = mapPathFor(generatedPath);
  if (!mapPath) return [];
  const map = load(mapPath);
  if (!map) return [];

  const cached = origins.get(mapPath);
  if (cached && cached.map === map) return cached.origins;

  const seen = new Set();
  const found = [];
  // `map.lines` is filled in ascending generated order by `decode`, so it needs no sorting.
  for (const [, entry] of map.lines) {
    const source = map.sources[entry.sourceIndex];
    if (!source || seen.has(entry.sourceIndex)) continue;
    seen.add(entry.sourceIndex);
    found.push({
      file: path.resolve(path.dirname(mapPath), map.sourceRoot, source),
      line: entry.sourceLine,
      column: entry.sourceColumn,
    });
  }
  origins.set(mapPath, { map, origins: found });
  return found;
}

/** Origins per map, keyed by map path and held against the decoded map they were read from,
 *  so a rebuild that replaces the map replaces these too. The header lens and the document link
 *  provider both ask on every request VS Code makes.
 *  @type {Map<string, { map: ReturnType<typeof decode>, origins: { file: string, line: number, column: number }[] }>} */
const origins = new Map();

// Lookup: source to generated

/** Python file to generated locations, built by scanning every known map. @type {Map<string, { file: string, line: number }[]> | null} */
let reverseIndex = null;

/**
 * Every Python line of one file that produced something, with the first thing it produced.
 *
 * The lens belongs on the line the map recorded, which is the `write_function` call, not on
 * the string it was handed: those are the same line when the commands are written inline and
 * twenty lines apart when they arrive in a variable.
 *
 * @param {string[]} mapPaths
 * @param {string} pythonPath
 * @returns {Map<number, { file: string, line: number }>}
 */
function originLinesFor(mapPaths, pythonPath) {
  if (!reverseIndex) reverseIndex = buildReverseIndex(mapPaths);

  const lines = new Map();
  for (const [line, locations] of reverseIndex.get(fileKey(pythonPath)) ?? []) {
    if (locations.length > 0) lines.set(line, locations[0]);
  }
  return lines;
}

/**
 * Every generated location produced by a Python line.
 *
 * The maps only run one way, so this needs an index built by reading all of them. Several
 * generated lines routinely share one source line (G7), which is why the result is a list.
 *
 * @param {string[]} mapPaths  Every .mcfunction.map to index, from the build output.
 * @param {string} pythonPath  Absolute path of the Python file.
 * @param {number} line  0-based Python line.
 * @returns {{ file: string, line: number }[]}
 */
function generatedFrom(mapPaths, pythonPath, line) {
  if (!reverseIndex) reverseIndex = buildReverseIndex(mapPaths);
  return (reverseIndex.get(fileKey(pythonPath))?.get(line) ?? []).slice();
}

/**
 * Source file to source line to what that line generated.
 *
 * Nested by file rather than keyed by a `file:line` string so that asking about one file is a
 * lookup instead of a walk over every mapped line in the project. A pack of two thousand
 * functions has tens of thousands of entries, and the lens provider asks on every keystroke.
 *
 * @param {string[]} mapPaths
 * @returns {Map<string, Map<number, { file: string, line: number }[]>>}
 */
function buildReverseIndex(mapPaths) {
  /** @type {Map<string, Map<number, { file: string, line: number }[]>>} */
  const index = new Map();

  for (const mapPath of mapPaths) {
    const map = load(mapPath);
    if (!map) continue;
    const generatedPath = mapPath.slice(0, -".map".length);
    const directory = path.dirname(mapPath);
    // One resolve per source, not per mapped line: the same source repeats on every line.
    const files = map.sources.map(source => fileKey(path.resolve(directory, map.sourceRoot, source)));

    for (const [generatedLine, entry] of map.lines) {
      const file = files[entry.sourceIndex];
      if (file === undefined) continue;

      let byLine = index.get(file);
      if (!byLine) index.set(file, byLine = new Map());
      const bucket = byLine.get(entry.sourceLine);
      const location = { file: generatedPath, line: generatedLine };
      if (bucket) bucket.push(location);
      else byLine.set(entry.sourceLine, [location]);
    }
  }
  return index;
}

/**
 * What the build wrote for each Python line of a range, keyed by that Python line.
 *
 * A line that produced nothing, or whose generated file has since been deleted, is simply
 * absent, which is what a project without a build looks like for every line at once.
 * Only the first generated location is read: a line that expanded into several commands has
 * no single answer, and the first one is the one whose text still anchors the line's literals.
 *
 * @param {string[]} mapPaths
 * @param {string} pythonPath
 * @param {number} from  First 0-based Python line, inclusive.
 * @param {number} to  Last 0-based Python line, inclusive.
 * @returns {Map<number, string>}
 */
function generatedText(mapPaths, pythonPath, from, to) {
  /** @type {Map<number, string>} */
  const found = new Map();
  for (let line = from; line <= to; line++) {
    const [target] = generatedFrom(mapPaths, pythonPath, line);
    if (!target) continue;
    const text = linesOf(target.file)?.[target.line];
    if (typeof text === "string") found.set(line, text);
  }
  return found;
}

/** @param {string} file */
function fileKey(file) {
  return path.normalize(file).toLowerCase();
}

module.exports = {
  MAP_SUFFIX,
  SOURCE_MAPPING_URL,
  decodeVlq,
  decode,
  mapPathFor,
  load,
  linesOf,
  clearCache,
  originOf,
  originsOf,
  generatedFrom,
  originLinesFor,
  generatedText,
};
