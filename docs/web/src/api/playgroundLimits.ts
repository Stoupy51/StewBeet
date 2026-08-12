/**
 * Limits both sides of the playground need to agree on.
 *
 * Its own module, with no imports, because the browser bundle reads these to draw the counter under
 * the editor. Importing them from playground.ts instead would pull `node:crypto` and the whole
 * server handler into the landing page's dependency graph.
 */

/** Also enforced by the handler and again by the worker, which cannot assume its caller. */
export const MAX_CODE_BYTES = 16 * 1024;

/** Where the counter turns amber, before the Build button goes away entirely. */
export const WARN_CODE_BYTES = 14 * 1024;

/** The worker's own ceilings, quoted in the limitations panel so the page cannot misstate them. */
export const SANDBOX_LIMITS = {
    cpuSeconds: 10,
    wallSeconds: 20,
    memoryMiB: 512,
    files: 500,
    totalMiB: 4,
} as const;
