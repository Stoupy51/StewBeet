/**
 * Limits both sides of every sandbox-backed tool need to agree on.
 *
 * Its own module, with no imports, because the browser bundle reads these to draw the counter under
 * the editor and the size check on the upload. Importing them from the handlers instead would pull
 * `node:crypto` and the whole server side into the landing page's dependency graph.
 *
 * Each number is enforced three times: here for the UI, again by the handler, and again by the
 * worker, which cannot assume its caller.
 */

/** Playground: largest definitions module the editor will submit. */
export const MAX_CODE_BYTES = 16 * 1024;

/** Playground: where the counter turns amber, before the Build button goes away entirely. */
export const WARN_CODE_BYTES = 14 * 1024;

/** auto.headers: largest datapack archive the upload will submit. */
export const MAX_PACK_BYTES = 25 * 1024 * 1024;

/** The playground worker's own ceilings, quoted in the limitations panel so it cannot misstate them. */
export const SANDBOX_LIMITS = {
    cpuSeconds: 10,
    wallSeconds: 20,
    memoryMiB: 512,
    files: 500,
    totalMiB: 4,
} as const;

/**
 * The headers worker's ceilings. Higher than the playground's because the work is proportional to
 * the submitted pack rather than to fifteen lines of definitions: the analysis cross-references
 * every function against every caller, and a real pack has thousands of both.
 */
export const HEADERS_LIMITS = {
    packMiB: MAX_PACK_BYTES / (1024 * 1024),
    cpuSeconds: 60,
    wallSeconds: 90,
    memoryMiB: 768,
    /** Total size once extracted, which is what a zip bomb runs into. */
    extractedMiB: 192,
    entries: 20_000,
} as const;
