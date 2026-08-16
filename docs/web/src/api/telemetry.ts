/**
 * The /api/telemetry endpoints: the daily build counter and the public 30-day series.
 *
 * The whole dataset is one small JSON file of daily aggregates, and that is deliberate. A build
 * event is counted into the day it arrived on and then forgotten, so there is no row to leak, no
 * row to subpoena and no row to correlate: not the address it came from, not the minute it came
 * in, not two builds from the same machine. `GET` can only ever read back what `POST` accumulated.
 *
 * Addresses are seen, because HTTP works that way, and are used for one thing: an in-memory rate
 * limit bucket that keeps a script from inventing build numbers. That map lives in the process
 * and is never part of what gets written to disk.
 *
 * Like src/api/playground.ts, this uses **no `Bun.*` API**: server.tsx and the Vite dev middleware
 * both import it, so it stays on `node:fs`, `Request` and `Response`, which both runtimes have.
 *
 * The client half is python_package/stewbeet/telemetry.py.
 */
import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

/** Where the aggregates live. Compose mounts a named volume here so a redeploy keeps the history. */
const DATA_DIR = process.env.TELEMETRY_DATA_DIR ?? '.telemetry';
const DATA_FILE = join(DATA_DIR, 'builds.json');

/**
 * Days kept on disk. The public page asks for 30, and nothing else reads this file, so the rest is
 * a short buffer for looking further back rather than an archive worth keeping.
 */
const RETENTION_DAYS = 365;

/** Ceiling on `?days=`, so one request cannot ask for more history than is kept. */
const MAX_QUERY_DAYS = RETENTION_DAYS;

const DEFAULT_QUERY_DAYS = 30;

/** Per-address ceiling on accepted events. A developer saving in a `stewbeet watch` loop stays well under. */
const RATE_PER_HOUR = 120;

/** Longest a version string may be before it is refused, so nothing unbounded is ever parsed. */
const MAX_VERSION_CHARS = 32;

/** Anything longer than this was not a build, it was a hang, and it would only skew the average. */
const MAX_DURATION_SECONDS = 24 * 3600;

/** One day's totals. `seconds` is a sum, so the average is derivable without keeping any build. */
interface DayTotals {
    builds: number;
    seconds: number;
    versions: Record<string, number>;
    pythonVersions: Record<string, number>;
    durationBuckets: Record<string, number>;
}

interface DatasetBreakdownMap {
    versions: Record<string, number>;
    pythonVersions: Record<string, number>;
    durationBuckets: Record<string, number>;
}

/** The file on disk: a version tag and one entry per `YYYY-MM-DD`. */
interface Dataset {
    version: number;
    days: Record<string, DayTotals>;
}

/** One day of the public series. Zero-build days are present with a zero, never omitted. */
export interface PublicDay {
    date: string;
    builds: number;
    avgDurationSeconds: number;
}

export interface PublicBreakdown {
    label: string;
    count: number;
    percentage: number;
}

export interface PublicBreakdowns {
    versions: PublicBreakdown[];
    pythonVersions: PublicBreakdown[];
    durationBuckets: PublicBreakdown[];
}

/** Per address arrival times, pruned on every lookup. Never written to disk. */
const hits = new Map<string, number[]>();

/** Read once, mutated in place, flushed on every accepted event. */
let dataset: Dataset | null = null;

function json(status: number, body: Record<string, unknown>, headers: Record<string, string> = {}): Response {
    return new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers },
    });
}

function emptyDayTotals(): DayTotals {
    return { builds: 0, seconds: 0, versions: {}, pythonVersions: {}, durationBuckets: {} };
}

function normalizeDayTotals(totals: Partial<DayTotals> | undefined): DayTotals {
    const value = totals ?? emptyDayTotals();
    return {
        builds: typeof value.builds === 'number' ? value.builds : 0,
        seconds: typeof value.seconds === 'number' ? value.seconds : 0,
        versions: typeof value.versions === 'object' && value.versions ? Object.fromEntries(
            Object.entries(value.versions).filter(([key, count]) => typeof key === 'string' && typeof count === 'number'),
        ) : {},
        pythonVersions: typeof value.pythonVersions === 'object' && value.pythonVersions ? Object.fromEntries(
            Object.entries(value.pythonVersions).filter(([key, count]) => typeof key === 'string' && typeof count === 'number'),
        ) : {},
        durationBuckets: typeof value.durationBuckets === 'object' && value.durationBuckets ? Object.fromEntries(
            Object.entries(value.durationBuckets).filter(([key, count]) => typeof key === 'string' && typeof count === 'number'),
        ) : {},
    };
}

function durationBucketLabel(durationSeconds: number): string {
    const seconds = Math.max(0, Number.isFinite(durationSeconds) ? durationSeconds : 0);
    const lowerBound = Math.floor(seconds / 5) * 5;
    const upperBound = lowerBound + 5;
    return `${lowerBound}s-${upperBound}s`;
}

function summarizeBreakdown(values: Record<string, number>, total: number): PublicBreakdown[] {
    return Object.entries(values)
        .map(([label, count]) => ({ label, count, percentage: total > 0 ? Number(((count / total) * 100).toFixed(1)) : 0 }))
        .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
}

/** `YYYY-MM-DD` in UTC, so the day a build lands on does not depend on where the server is. */
export function dayKey(at: Date): string {
    return at.toISOString().slice(0, 10);
}

/** The `days` keys of a rolling window ending today, oldest first. */
export function windowDays(days: number, today: Date): string[] {
    const keys: string[] = [];
    for (let offset = days - 1; offset >= 0; offset--) {
        keys.push(dayKey(new Date(today.getTime() - offset * 86_400_000)));
    }
    return keys;
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
        const parsed = JSON.parse(readFileSync(DATA_FILE, 'utf-8')) as Partial<Dataset>;
        const days: Record<string, DayTotals> = {};
        for (const [date, totals] of Object.entries(parsed.days ?? {})) {
            if (/^\d{4}-\d{2}-\d{2}$/.test(date) && (typeof totals?.builds === 'number' || typeof totals?.seconds === 'number')) {
                days[date] = normalizeDayTotals(totals as Partial<DayTotals> | undefined);
            }
        }
        dataset = { version: 2, days };
    } catch {
        dataset = { version: 2, days: {} };
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
    for (const date of Object.keys(data.days)) {
        if (date < cutoff) delete data.days[date];
    }
    try {
        mkdirSync(DATA_DIR, { recursive: true });
        const temporary = `${DATA_FILE}.tmp`;
        writeFileSync(temporary, JSON.stringify(data));
        renameSync(temporary, DATA_FILE);
    } catch (error) {
        // A read-only or unmounted volume is not worth a 500 to a client that ignores the answer.
        console.error('telemetry: could not persist the daily counter', error);
    }
}

/** Record one arrival and report whether the caller has gone over its hourly budget. */
function rateLimited(ip: string): boolean {
    const now = Date.now();
    const seen = (hits.get(ip) ?? []).filter(at => now - at < 3_600_000);
    if (seen.length >= RATE_PER_HOUR) {
        hits.set(ip, seen);
        return true;
    }

    seen.push(now);
    hits.set(ip, seen);
    // Without this the map grows one entry per address seen, for the lifetime of the process.
    if (hits.size > 10_000) {
        for (const [key, times] of hits) {
            if (times.every(at => now - at > 3_600_000)) hits.delete(key);
        }
    }
    return false;
}

/**
 * Add one build to today's totals.
 *
 * Exported for the tests, and the only function in this module that writes anything.
 *
 * @param durationSeconds How long the build took, already validated.
 * @param at              When it arrived, which is the only timestamp involved and is kept only as
 *                        the day it falls in.
 */
export function countBuild(
    durationSeconds: number,
    stewbeetVersionOrAt: string | Date = 'unknown',
    pythonVersionOrAt: string | Date = 'unknown',
    maybeAt: Date = new Date(),
): void {
    const data = load();
    const at = stewbeetVersionOrAt instanceof Date ? stewbeetVersionOrAt : maybeAt;
    const version = typeof stewbeetVersionOrAt === 'string' ? stewbeetVersionOrAt : 'unknown';
    const pythonVersion = typeof pythonVersionOrAt === 'string' ? pythonVersionOrAt : 'unknown';
    const key = dayKey(at);
    const totals = data.days[key] ?? emptyDayTotals();
    totals.builds += 1;
    totals.seconds += durationSeconds;
    totals.versions[version] = (totals.versions[version] ?? 0) + 1;
    totals.pythonVersions[pythonVersion] = (totals.pythonVersions[pythonVersion] ?? 0) + 1;
    totals.durationBuckets[durationBucketLabel(durationSeconds)] = (totals.durationBuckets[durationBucketLabel(durationSeconds)] ?? 0) + 1;
    data.days[key] = totals;
    save(data, at);
}

/**
 * The public series: one entry per day of the rolling window, zero-build days included.
 *
 * @param days  Length of the window, already clamped.
 * @param today The day the window ends on.
 */
export function publicSeries(days: number, today: Date = new Date()): {
    days: PublicDay[];
    total: number;
    avgDurationSeconds: number;
    breakdowns: PublicBreakdowns;
} {
    const data = load();
    const window = windowDays(days, today);
    const series: PublicDay[] = window.map(date => {
        const totals = data.days[date] ?? emptyDayTotals();
        return {
            date,
            builds: totals.builds,
            avgDurationSeconds: totals.builds > 0 ? Number((totals.seconds / totals.builds).toFixed(3)) : 0,
        };
    });

    const total = series.reduce((sum, day) => sum + day.builds, 0);
    const seconds = window.reduce((sum, date) => sum + (data.days[date]?.seconds ?? 0), 0);

    const breakdowns: DatasetBreakdownMap = { versions: {}, pythonVersions: {}, durationBuckets: {} };
    for (const date of window) {
        const day = data.days[date] ?? emptyDayTotals();
        for (const [label, count] of Object.entries(day.versions)) breakdowns.versions[label] = (breakdowns.versions[label] ?? 0) + count;
        for (const [label, count] of Object.entries(day.pythonVersions)) breakdowns.pythonVersions[label] = (breakdowns.pythonVersions[label] ?? 0) + count;
        for (const [label, count] of Object.entries(day.durationBuckets)) breakdowns.durationBuckets[label] = (breakdowns.durationBuckets[label] ?? 0) + count;
    }

    return {
        days: series,
        total,
        avgDurationSeconds: total > 0 ? Number((seconds / total).toFixed(3)) : 0,
        breakdowns: {
            versions: summarizeBreakdown(breakdowns.versions, total),
            pythonVersions: summarizeBreakdown(breakdowns.pythonVersions, total),
            durationBuckets: summarizeBreakdown(breakdowns.durationBuckets, total),
        },
    };
}

/** A version string is only accepted when it is short and made of the characters a version has. */
function isVersion(value: unknown): value is string {
    return typeof value === 'string' && value.length > 0 && value.length <= MAX_VERSION_CHARS && /^[A-Za-z0-9._+-]+$/.test(value);
}

/**
 * Handle one `POST /api/telemetry/build`.
 *
 * The three documented fields are validated and then thrown away: what survives the call is `+1`
 * on one day's counter and its duration added to that day's sum. Anything else in the body is
 * ignored rather than refused, so an older client that predates `duration_seconds` still counts.
 *
 * @param req      The incoming request. Only POST exists; anything else is 405.
 * @param clientIp Caller address, resolved by the host. Used as the rate limit bucket and nothing else.
 */
export async function handleTelemetryBuild(req: Request, clientIp: string): Promise<Response> {
    if (req.method !== 'POST') {
        return json(405, { ok: false, error: 'method_not_allowed' }, { Allow: 'POST' });
    }

    let body: Record<string, unknown>;
    try {
        body = await req.json() as Record<string, unknown>;
    } catch {
        return json(400, { ok: false, error: 'invalid_body' });
    }

    if (!isVersion(body.stewbeet_version) || !isVersion(body.python_version)) {
        return json(400, { ok: false, error: 'invalid_body' });
    }

    const duration = body.duration_seconds;
    if (duration !== undefined && (typeof duration !== 'number' || !Number.isFinite(duration) || duration < 0 || duration > MAX_DURATION_SECONDS)) {
        return json(400, { ok: false, error: 'invalid_body' });
    }

    if (rateLimited(clientIp)) {
        return json(429, { ok: false, error: 'rate_limited' });
    }

    countBuild(
        typeof duration === 'number' ? duration : 0,
        String(body.stewbeet_version),
        String(body.python_version),
    );
    // 204 rather than a body: the client closes the connection without reading, by design.
    return new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store' } });
}

/**
 * Handle one `GET /api/telemetry/builds?days=30`.
 *
 * @param url The request URL, whose `days` parameter is clamped to what is actually retained.
 */
export function handleTelemetryBuilds(url: URL): Response {
    const requested = Number(url.searchParams.get('days') ?? DEFAULT_QUERY_DAYS);
    const days = Number.isFinite(requested) ? Math.min(Math.max(Math.trunc(requested), 1), MAX_QUERY_DAYS) : DEFAULT_QUERY_DAYS;

    return json(200, { ...publicSeries(days) }, {
        // Aggregates move once per build, and the page is not a live dashboard.
        'Cache-Control': 'public, max-age=300',
    });
}

/** Test seam: drop the in-memory dataset and rate limit buckets so a case starts from the file. */
export function resetTelemetryState(): void {
    dataset = null;
    hits.clear();
}
