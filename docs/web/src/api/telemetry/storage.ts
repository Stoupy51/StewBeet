/**
 * The counters themselves: one small JSON file of daily aggregates, and the only code that writes it.
 *
 * An event is counted into the day it arrived on and then forgotten, so there is no row to leak, no
 * row to subpoena and no row to correlate: not the address it came from, not the minute it came in,
 * not two events from the same machine. Reading can only ever give back what writing accumulated.
 *
 * The shape is generic on purpose. A stream is a name, a daily count, a duration sum and whatever
 * breakdowns its registry entry declares, so a new counter needs no migration and no new field.
 *
 * Uses **no `Bun.*` API**: server.tsx and the Vite dev middleware both import it, so it stays on
 * `node:fs`, which both runtimes have.
 */
import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { DEFAULT_STREAM_ID, DURATION_DIMENSION, durationBucket, findStream, TELEMETRY_STREAMS, type StreamId } from './streams';

/** Where the aggregates live. Compose mounts a named volume here so a redeploy keeps the history. */
const DATA_DIR = process.env.TELEMETRY_DATA_DIR ?? '.telemetry';

/** Still builds.json, and it has to stay builds.json: the deployed volume holds the only copy of the history. */
const DATA_FILE = join(DATA_DIR, 'builds.json');

/**
 * Days kept on disk. The public page asks for 30, and nothing else reads this file, so the rest is
 * a short buffer for looking further back rather than an archive worth keeping.
 */
export const RETENTION_DAYS = 365;

/**
 * Distinct labels one dimension keeps in a day before the rest are folded into `other`.
 *
 * The ceiling is what makes a client-reported dimension safe to write down at all: without it, a
 * browser sending a fresh label every time would grow the file without bound and turn a set of
 * counters into a log of arrivals.
 */
const MAX_LABELS_PER_DIMENSION = 60;

/** Longest a label may be, and the characters it may use, which every bucket helper satisfies. */
const MAX_LABEL_CHARS = 32;
const LABEL_PATTERN = /^[A-Za-z0-9 ._+<>-]+$/;

/** Where a label goes once a dimension is full, so the breakdown still adds up to the event count. */
const OVERFLOW_LABEL = 'other';

/** One day of one stream. `seconds` is a sum, so the average is derivable without keeping any event. */
interface DayTotals {
    events: number;
    seconds: number;
    dimensions: Record<string, Record<string, number>>;
}

/** The file on disk: a version tag, then one map of `YYYY-MM-DD` per stream. */
interface Dataset {
    version: number;
    streams: Record<string, Record<string, DayTotals>>;
}

/** One day of a public series. Days with no events are present with a zero, never omitted. */
export interface PublicDay {
    date: string;
    events: number;
    avgDurationSeconds: number;
}

export interface PublicBreakdown {
    label: string;
    count: number;
    percentage: number;
}

/** What the public endpoints return per stream, and what one panel of the slider draws. */
export interface PublicStream {
    stream: string;
    days: PublicDay[];
    total: number;
    avgDurationSeconds: number;
    breakdowns: Record<string, PublicBreakdown[]>;
}

/** What one event carries beyond the fact that it happened. */
export interface EventDetails {
    /** How long the work took. Fills the `durationBuckets` dimension for streams that declare it. */
    durationSeconds?: number;
    /** Dimension name to label. Anything the stream does not declare is dropped rather than stored. */
    labels?: Record<string, string>;
}

/** Read once, mutated in place, flushed on every accepted event. */
let dataset: Dataset | null = null;

function emptyDayTotals(): DayTotals {
    return { events: 0, seconds: 0, dimensions: {} };
}

/** Keep the pairs that are a label and a count, and drop whatever else a hand-edited file holds. */
function normalizeCounts(value: unknown): Record<string, number> {
    if (typeof value !== 'object' || value === null) return {};
    return Object.fromEntries(
        Object.entries(value as Record<string, unknown>)
            .filter(([label, count]) => typeof label === 'string' && typeof count === 'number' && Number.isFinite(count)),
    ) as Record<string, number>;
}

function normalizeDayTotals(value: unknown): DayTotals {
    const totals = (typeof value === 'object' && value !== null ? value : {}) as Record<string, unknown>;
    const dimensions: Record<string, Record<string, number>> = {};
    if (typeof totals.dimensions === 'object' && totals.dimensions !== null) {
        for (const [name, counts] of Object.entries(totals.dimensions as Record<string, unknown>)) {
            dimensions[name] = normalizeCounts(counts);
        }
    }
    return {
        events: typeof totals.events === 'number' ? totals.events : 0,
        seconds: typeof totals.seconds === 'number' ? totals.seconds : 0,
        dimensions,
    };
}

/**
 * The version 2 file, which was builds only, read as the `cli` stream of a version 3 one.
 *
 * Kept because the deployed volume holds real history in that shape, and a fresh start would throw
 * it away. It can go once no running deploy still has a version 2 file, which is one deploy after
 * the first write this code makes.
 */
function migrateFromV2(days: Record<string, unknown>): Record<string, DayTotals> {
    const migrated: Record<string, DayTotals> = {};
    for (const [date, value] of Object.entries(days)) {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || typeof value !== 'object' || value === null) continue;
        const totals = value as Record<string, unknown>;
        migrated[date] = {
            events: typeof totals.builds === 'number' ? totals.builds : 0,
            seconds: typeof totals.seconds === 'number' ? totals.seconds : 0,
            dimensions: {
                versions: normalizeCounts(totals.versions),
                pythonVersions: normalizeCounts(totals.pythonVersions),
                [DURATION_DIMENSION]: normalizeCounts(totals.durationBuckets),
            },
        };
    }
    return migrated;
}

/**
 * The stored dataset, or an empty one when the file is missing or unreadable.
 *
 * An unreadable file is treated as empty rather than fatal: losing the counter is a worse outcome
 * for nobody, whereas a crash loop on a corrupted byte takes the whole documentation site down.
 */
function load(): Dataset {
    if (dataset) return dataset;
    try {
        const parsed = JSON.parse(readFileSync(DATA_FILE, 'utf-8')) as Record<string, unknown>;
        const streams: Record<string, Record<string, DayTotals>> = {};

        if (typeof parsed.streams === 'object' && parsed.streams !== null) {
            for (const [id, days] of Object.entries(parsed.streams as Record<string, unknown>)) {
                if (typeof days !== 'object' || days === null) continue;
                const kept: Record<string, DayTotals> = {};
                for (const [date, totals] of Object.entries(days as Record<string, unknown>)) {
                    if (/^\d{4}-\d{2}-\d{2}$/.test(date)) kept[date] = normalizeDayTotals(totals);
                }
                streams[id] = kept;
            }
        } else if (typeof parsed.days === 'object' && parsed.days !== null) {
            streams[DEFAULT_STREAM_ID] = migrateFromV2(parsed.days as Record<string, unknown>);
        }

        dataset = { version: 3, streams };
    } catch {
        dataset = { version: 3, streams: {} };
    }
    return dataset;
}

/**
 * Write through a temporary file, so a process killed mid-write leaves the previous one intact.
 *
 * @param data The dataset to write, pruned in place first.
 * @param at   The day the retention window ends on: the event being written, not the wall clock,
 *             so backfilling a day never races the clock into deleting it.
 */
function save(data: Dataset, at: Date): void {
    const cutoff = dayKey(new Date(at.getTime() - RETENTION_DAYS * 86_400_000));
    for (const days of Object.values(data.streams)) {
        for (const date of Object.keys(days)) {
            if (date < cutoff) delete days[date];
        }
    }
    try {
        mkdirSync(DATA_DIR, { recursive: true });
        const temporary = `${DATA_FILE}.tmp`;
        writeFileSync(temporary, JSON.stringify(data));
        renameSync(temporary, DATA_FILE);
    } catch (error) {
        // A read-only or unmounted volume is not worth a 500 to a client that ignores the answer.
        console.error('telemetry: could not persist the daily counters', error);
    }
}

/** `YYYY-MM-DD` in UTC, so the day an event lands on does not depend on where the server is. */
export function dayKey(at: Date): string {
    return at.toISOString().slice(0, 10);
}

/** The day keys of a rolling window ending on `today`, oldest first. */
export function windowDays(days: number, today: Date): string[] {
    const keys: string[] = [];
    for (let offset = days - 1; offset >= 0; offset--) {
        keys.push(dayKey(new Date(today.getTime() - offset * 86_400_000)));
    }
    return keys;
}

/** A label is only written down when it is short and made of the characters a label may use. */
export function isLabel(value: unknown): value is string {
    return typeof value === 'string' && value.length > 0 && value.length <= MAX_LABEL_CHARS && LABEL_PATTERN.test(value);
}

/** Add one to a label's count, folding into `other` once the dimension has seen enough distinct ones. */
function countLabel(counts: Record<string, number>, label: string): void {
    const known = counts[label] !== undefined;
    const key = known || Object.keys(counts).length < MAX_LABELS_PER_DIMENSION ? label : OVERFLOW_LABEL;
    counts[key] = (counts[key] ?? 0) + 1;
}

/**
 * Add one event to a stream's totals for the day it arrived on.
 *
 * The only function in this package that writes anything. An unregistered stream is ignored rather
 * than created, so a typo at a call site cannot invent a counter nothing will ever display.
 *
 * @param streamId One of the registry ids.
 * @param details  Duration and labels. Labels the stream does not declare are dropped.
 * @param at       When it arrived, kept only as the day it falls in.
 */
export function recordEvent(streamId: StreamId, details: EventDetails = {}, at: Date = new Date()): void {
    const stream = findStream(streamId);
    if (!stream) return;

    const data = load();
    const days = data.streams[stream.id] ?? {};
    const key = dayKey(at);
    const totals = days[key] ?? emptyDayTotals();
    const duration = typeof details.durationSeconds === 'number' && Number.isFinite(details.durationSeconds)
        ? Math.max(0, details.durationSeconds)
        : 0;

    totals.events += 1;
    totals.seconds += duration;

    for (const dimension of stream.dimensions) {
        const label = dimension === DURATION_DIMENSION ? durationBucket(duration) : details.labels?.[dimension];
        if (!isLabel(label)) continue;
        const counts = totals.dimensions[dimension] ?? {};
        countLabel(counts, label);
        totals.dimensions[dimension] = counts;
    }

    days[key] = totals;
    data.streams[stream.id] = days;
    save(data, at);
}

function summarizeBreakdown(values: Record<string, number>, total: number): PublicBreakdown[] {
    return Object.entries(values)
        .map(([label, count]) => ({ label, count, percentage: total > 0 ? Number(((count / total) * 100).toFixed(1)) : 0 }))
        .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
}

/**
 * One stream's public series: one entry per day of the rolling window, quiet days included.
 *
 * An unregistered id gives an empty series rather than nothing, so a stale `?stream=` in someone's
 * bookmark draws an empty panel instead of breaking the page.
 *
 * @param streamId One of the registry ids.
 * @param days     Length of the window, already clamped.
 * @param today    The day the window ends on.
 */
export function streamSeries(streamId: string, days: number, today: Date = new Date()): PublicStream {
    const stream = findStream(streamId);
    const stored = load().streams[streamId] ?? {};
    const window = windowDays(days, today);

    const series: PublicDay[] = window.map(date => {
        const totals = stored[date] ?? emptyDayTotals();
        return {
            date,
            events: totals.events,
            avgDurationSeconds: totals.events > 0 ? Number((totals.seconds / totals.events).toFixed(3)) : 0,
        };
    });

    const total = series.reduce((sum, day) => sum + day.events, 0);
    const seconds = window.reduce((sum, date) => sum + (stored[date]?.seconds ?? 0), 0);

    const totalled: Record<string, Record<string, number>> = {};
    for (const dimension of stream?.dimensions ?? []) totalled[dimension] = {};
    for (const date of window) {
        for (const [dimension, counts] of Object.entries(stored[date]?.dimensions ?? {})) {
            const running = totalled[dimension];
            if (!running) continue;
            for (const [label, count] of Object.entries(counts)) {
                running[label] = (running[label] ?? 0) + count;
            }
        }
    }

    return {
        stream: streamId,
        days: series,
        total,
        avgDurationSeconds: total > 0 ? Number((seconds / total).toFixed(3)) : 0,
        breakdowns: Object.fromEntries(
            Object.entries(totalled).map(([dimension, counts]) => [dimension, summarizeBreakdown(counts, total)]),
        ),
    };
}

/** Every registered stream over the same window, which is one request for the whole slider. */
export function allStreams(days: number, today: Date = new Date()): Record<string, PublicStream> {
    return Object.fromEntries(TELEMETRY_STREAMS.map(stream => [stream.id, streamSeries(stream.id, days, today)]));
}

/** Test seam: drop the in-memory dataset so a case starts from the file. */
export function resetDataset(): void {
    dataset = null;
}
