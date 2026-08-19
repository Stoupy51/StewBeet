/**
 * The registry of counted things, and the label helpers that go with it.
 *
 * Adding a counter is one entry in this list, one `recordEvent` call where the event happens, and
 * the labels under `telemetry.streams.<id>` in translations.ts. Storage, both public endpoints and
 * the slider on /telemetry are driven by this list, so none of them has to be edited to add one.
 *
 * Imported by the API modules and by the page, so it stays free of React and of any `Bun.*` API.
 */

/** Where a stream's events come from, which is also how far its numbers can be trusted. */
export type StreamSource = 'server' | 'client';

/** The dimension whose labels are filled from the event's own duration rather than by the caller. */
export const DURATION_DIMENSION = 'durationBuckets';

export interface TelemetryStream {
    /** Storage key, and the value of `?stream=`. Stable forever: renaming one orphans its history. */
    id: string;
    /**
     * `server` streams are counted by the handler that did the work, so they are as accurate as the
     * work is. `client` streams are reported by a browser and are only as honest as that browser,
     * which is why the event endpoint refuses to write to a stream that is not one of them.
     */
    source: StreamSource;
    /** Breakdowns to keep, in the order the page draws them. Labelled by `telemetry.dimensions.<name>`. */
    dimensions: readonly string[];
    /** The page this stream counts, linked from its panel. Empty for the CLI, which is not a page. */
    href: string;
}

/**
 * Every stream the server will write to, in the order the slider walks through them.
 *
 * The first is the default panel. `cli` and `playground` are deliberately separate rather than one
 * number: the sandbox runs with STEWBEET_TELEMETRY=0, so a playground build has never counted as a
 * real one, and folding curiosity into the figure for installed use would flatter it.
 */
export const TELEMETRY_STREAMS = [
    { id: 'cli',                source: 'server', dimensions: ['versions', 'pythonVersions', DURATION_DIMENSION], href: '' },
    { id: 'playground',         source: 'server', dimensions: ['outcomes', DURATION_DIMENSION],                   href: '/playground' },
    { id: 'auto_headers',       source: 'server', dimensions: ['outcomes', 'packSizes', DURATION_DIMENSION],      href: '/auto_headers' },
    { id: 'markdown_to_bbcode', source: 'client', dimensions: ['actions', 'inputSizes'],                          href: '/markdown_to_pmc_bbcode' },
] as const satisfies readonly TelemetryStream[];

/**
 * The ids that exist, as a type.
 *
 * `recordEvent` takes this rather than a string, so a mistyped stream at a call site is a build
 * error instead of an event counted into a stream nothing will ever draw.
 */
export type StreamId = RegisteredStream['id'];

/** One entry of the registry, with its id narrowed to the literal it was written as. */
export type RegisteredStream = typeof TELEMETRY_STREAMS[number];

/** The stream the page opens on, and the one `/api/telemetry/builds` has always meant. */
export const DEFAULT_STREAM_ID: StreamId = 'cli';

export function findStream(id: string): RegisteredStream | undefined {
    return TELEMETRY_STREAMS.find(stream => stream.id === id);
}

/**
 * The bucket a measurement falls in, as the label that will be shown.
 *
 * The unit is written once, at the end, because these end up as pie slices and `1 MB-5 MB` is
 * twice the width of `1-5 MB` to say the same thing.
 *
 * @param value The measurement. Anything not finite is treated as zero.
 * @param edges Ascending bucket boundaries.
 * @param unit  Suffix for the label, ex: ' MB'.
 * @returns The label, ex: '<1 MB' or '1-5 MB' or '20 MB+'.
 *
 * Examples:
 *     >>> bucketOf(3, [1, 5, 10], ' MB')
 *     '1-5 MB'
 *     >>> bucketOf(0.2, [1, 5, 10], ' MB')
 *     '<1 MB'
 *     >>> bucketOf(40, [1, 5, 10], ' MB')
 *     '10 MB+'
 */
export function bucketOf(value: number, edges: readonly number[], unit: string): string {
    const measurement = Number.isFinite(value) ? Math.max(0, value) : 0;
    if (measurement < edges[0]) return `<${edges[0]}${unit}`;
    for (let index = 1; index < edges.length; index++) {
        if (measurement < edges[index]) return `${edges[index - 1]}-${edges[index]}${unit}`;
    }
    return `${edges[edges.length - 1]}${unit}+`;
}

/**
 * Five second bands, which is the resolution the build chart has always used.
 *
 * Examples:
 *     >>> durationBucket(12.5)
 *     '10s-15s'
 */
export function durationBucket(durationSeconds: number): string {
    const seconds = Math.max(0, Number.isFinite(durationSeconds) ? durationSeconds : 0);
    const lowerBound = Math.floor(seconds / 5) * 5;
    return `${lowerBound}s-${lowerBound + 5}s`;
}

/** Upload size bands, spread over the 25 MB the tool accepts rather than evenly. */
export function packSizeBucket(bytes: number): string {
    return bucketOf(bytes / 1_000_000, [1, 5, 10, 20], ' MB');
}

/** Pasted-document size bands, in thousands of characters: a paragraph, a page, a README, a book. */
export function inputSizeBucket(characters: number): string {
    return bucketOf(characters / 1_000, [1, 5, 20], 'k');
}
