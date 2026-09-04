// @ts-check
"use strict";

// Navigation across the Python/mcfunction boundary.
//
// Spyglass answers definition and references against the generated .mcfunction files, which is
// the right answer for a datapack and the wrong one for someone editing Python: those files are
// build output. This rewrites every answer that lands in generated content to the Python that
// wrote it, using the source maps a build emits.
//
// The rewriting itself is a pure function over plain {file, line} records, kept apart from the
// vscode plumbing so it can be unit-tested under `node --test`.

const path = require("path");
const sourcemap = require("./sourcemap");

// Required lazily by the two functions that need it, so the rewriting above stays loadable
// under plain `node --test`, where the vscode module does not exist.
/** @returns {typeof import("vscode")} */
function api() {
  return require("vscode");
}

// ─── Constants──────────────

const CFG_KEY = "StewBeet";

const GENERATED_SUFFIX = ".mcfunction";

// ─── Shape normalisation────

/**
 * The target of one definition answer, whichever of the two shapes VS Code returned.
 *
 * `vscode.executeDefinitionProvider` resolves to `Location[] | LocationLink[]` and which one
 * arrives depends on the answering provider, not on us, so both are handled rather than
 * assuming Spyglass's current choice will hold.
 *
 * @param {any} entry
 * @returns {{ uri: vscode.Uri, range: vscode.Range } | null}
 */
function targetOf(entry) {
  if (!entry) return null;
  if (entry.targetUri) return { uri: entry.targetUri, range: entry.targetSelectionRange ?? entry.targetRange };
  if (entry.uri) return { uri: entry.uri, range: entry.range };
  return null;
}

/** @param {vscode.Uri} uri */
function isGenerated(uri) {
  return uri.scheme === "file" && uri.fsPath.endsWith(GENERATED_SUFFIX);
}

// ─── Rewriting (pure)───────

/**
 * Rewrite one generated location to the Python that wrote it.
 *
 * Returns every distinct origin of the file when the clicked line itself is unmapped, so a
 * click on a generated header still leads somewhere useful, and an empty list when the file
 * has no map at all, which the caller turns back into the generated location.
 *
 * @param {{ file: string, line: number }} location
 * @param {typeof sourcemap} [maps]  Injected in tests.
 * @returns {{ file: string, line: number, column: number }[]}
 */
function originsFor(location, maps = sourcemap) {
  const exact = maps.originOf(location.file, location.line);
  if (exact) return [exact];
  return maps.originsOf(location.file);
}

/**
 * Rewrite a whole definition or reference answer.
 *
 * A target that is not generated content, or that has no map, is passed through untouched:
 * losing navigation is worse than landing in the generated file, which is what step A did.
 * Distinct origins are kept in the order they were produced and de-duplicated by file and
 * line, since several generated lines routinely share one source line (guarantee G7) and a
 * peek list showing the same line five times is noise.
 *
 * @param {any[]} answers  Location[] or LocationLink[] as returned by vscode.execute*.
 * @param {typeof sourcemap} [maps]
 * @returns {{ file: string, line: number, column: number }[] | null}  null when nothing was rewritten.
 */
function rewrite(answers, maps = sourcemap) {
  if (!Array.isArray(answers) || answers.length === 0) return null;

  /** @type {{ file: string, line: number, column: number }[]} */
  const rewritten = [];
  const seen = new Set();
  let touched = false;

  for (const entry of answers) {
    const target = targetOf(entry);
    if (!target || !isGenerated(target.uri)) continue;

    const origins = originsFor({ file: target.uri.fsPath, line: target.range?.start?.line ?? 0 }, maps);
    if (origins.length === 0) continue;
    touched = true;

    for (const origin of origins) {
      const key = `${path.normalize(origin.file).toLowerCase()}:${origin.line}`;
      if (seen.has(key)) continue;
      seen.add(key);
      rewritten.push(origin);
    }
  }

  return touched ? rewritten : null;
}

// ─── vscode adapters────────

/** @param {{ file: string, line: number, column: number }} origin */
function toLocation(origin) {
  const vscode = api();
  return new vscode.Location(vscode.Uri.file(origin.file), new vscode.Position(origin.line, origin.column));
}

/**
 * Turn Spyglass's answer into Python locations, or leave it alone.
 * @param {any} answers
 * @returns {any}
 */
function resolve(answers) {
  const origins = rewrite(answers);
  return origins ? origins.map(toLocation) : answers;
}

// ─── Build output───────────

/** The last discovery, reused until a map is written or deleted. @type {string[] | null} */
let discovered = null;

/**
 * Every `.mcfunction.map` in the workspace's build output.
 *
 * The whole workspace is searched, since a pack's output does not have to sit under `build/`,
 * and `StewBeet.buildOutput` narrows it for a workspace where that costs too much. A
 * workspace with no build yields an empty list and nothing else happens: navigation quietly
 * stops working and every step A feature keeps going.
 *
 * The result is cached because the projection now asks for it on every keystroke, and a
 * workspace-wide `findFiles` per character typed is not something an editor survives.
 *
 * @returns {Promise<string[]>}
 */
async function findMaps() {
  if (discovered) return discovered;

  const vscode = api();
  const configured = vscode.workspace.getConfiguration(CFG_KEY).get("buildOutput", "");
  const pattern = configured
    ? new vscode.RelativePattern(configured, `**/*${sourcemap.MAP_SUFFIX}`)
    : `**/*${sourcemap.MAP_SUFFIX}`;
  try {
    const found = await vscode.workspace.findFiles(pattern, "**/node_modules/**");
    discovered = found.map(uri => uri.fsPath);
    return discovered;
  } catch (e) {
    console.debug("[StewBeet] source map discovery failed", e);
    return [];
  }
}

/** Forget which maps exist, so the next lookup searches the workspace again. */
function forgetMaps() {
  discovered = null;
}

module.exports = {
  targetOf,
  isGenerated,
  originsFor,
  rewrite,
  resolve,
  findMaps,
  forgetMaps,
};
