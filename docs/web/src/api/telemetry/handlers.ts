/**
 * The four `/api/telemetry` endpoints, and the rate limiting that keeps a script from inventing
 * numbers with them.
 *
 * Addresses are seen, because HTTP works that way, and are used for one thing: an in-memory bucket
 * that decides whether to accept the event. That map lives in the process and is never part of what
 * gets written to disk.
 *
 * The two endpoints that write are deliberately different. `/build` is the published contract with
 * python_package/stewbeet/telemetry.py and only ever touches the `cli` stream. `/event` is for the
 * website's own tools and only accepts streams the registry marks as client reported, so a browser
 * can never add to a counter that is supposed to mean "somebody ran a real build".
 */
import { DEFAULT_STREAM_ID, DURATION_DIMENSION, findStream } from './streams';
import { allStreams, isLabel, recordEvent, RETENTION_DAYS, streamSeries, resetDataset } from './storage';

/** Ceiling on `?days=`, so one request cannot ask for more history than is kept. */
const MAX_QUERY_DAYS = RETENTION_DAYS;

const DEFAULT_QUERY_DAYS = 30;

/** Per-address ceiling per endpoint. A developer saving in a `stewbeet watch` loop stays well under. */
const RATE_PER_HOUR = 120;

/** Longest a version string may be before it is refused, so nothing unbounded is ever parsed. */
const MAX_VERSION_CHARS = 32;

/** Anything longer than this was not a build, it was a hang, and it would only skew the average. */
const MAX_DURATION_SECONDS = 24 * 3600;

/** Labels one event may carry, which is more dimensions than any stream declares. */
const MAX_LABELS_PER_EVENT = 8;

/**
 * Per-address arrival times for one endpoint, pruned on every lookup and never written to disk.
 *
 * One instance per endpoint rather than one shared: a browser clicking through a tool and a build
 * machine reporting builds have nothing to do with each other, and one should not be able to spend
 * the other's budget just by sharing an office NAT.
 */
class HourlyLimiter {
    readonly hits = new Map<string, number[]>();

    /** Record one arrival and report whether this address has gone over its hourly budget. */
    limited(ip: string): boolean {
        const now = Date.now();
        const seen = (this.hits.get(ip) ?? []).filter(at => now - at < 3_600_000);
        if (seen.length >= RATE_PER_HOUR) {
            this.hits.set(ip, seen);
            return true;
        }

        seen.push(now);
        this.hits.set(ip, seen);
        // Without this the map grows one entry per address seen, for the lifetime of the process.
        if (this.hits.size > 10_000) {
            for (const [key, times] of this.hits) {
                if (times.every(at => now - at > 3_600_000)) this.hits.delete(key);
            }
        }
        return false;
    }
}

const buildLimiter = new HourlyLimiter();
const eventLimiter = new HourlyLimiter();

function json(status: number, body: Record<string, unknown>, headers: Record<string, string> = {}): Response {
    return new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers },
    });
}

function queryDays(url: URL): number {
    const requested = Number(url.searchParams.get('days') ?? DEFAULT_QUERY_DAYS);
    if (!Number.isFinite(requested)) return DEFAULT_QUERY_DAYS;
    return Math.min(Math.max(Math.trunc(requested), 1), MAX_QUERY_DAYS);
}

/** A version string is only accepted when it is short and made of the characters a version has. */
function isVersion(value: unknown): value is string {
    return typeof value === 'string' && value.length > 0 && value.length <= MAX_VERSION_CHARS && /^[A-Za-z0-9._+-]+$/.test(value);
}

/**
 * Add one build to the `cli` stream.
 *
 * Exported for the tests, and the reason the two version fields are named here rather than passed
 * as labels by every caller: this is the only shape `/build` has ever accepted.
 *
 * @param durationSeconds How long the build took, already validated.
 * @param stewbeetVersion The reported StewBeet version, or `unknown`.
 * @param pythonVersion   The reported Python version, or `unknown`.
 * @param at              When it arrived, which is kept only as the day it falls in.
 */
export function countBuild(
    durationSeconds: number,
    stewbeetVersion: string = 'unknown',
    pythonVersion: string = 'unknown',
    at: Date = new Date(),
): void {
    recordEvent(DEFAULT_STREAM_ID, {
        durationSeconds,
        labels: { versions: stewbeetVersion, pythonVersions: pythonVersion },
    }, at);
}

/**
 * Handle one `POST /api/telemetry/build`.
 *
 * The three documented fields are validated and then thrown away: what survives the call is `+1` on
 * one day's counter and its duration added to that day's sum. Anything else in the body is ignored
 * rather than refused, so an older client that predates `duration_seconds` still counts.
 *
 * @param req      The incoming request. Only POST exists; anything else is 405.
 * @param clientIp Caller address, resolved by the host. The rate limit bucket, and nothing else.
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

    if (buildLimiter.limited(clientIp)) {
        return json(429, { ok: false, error: 'rate_limited' });
    }

    countBuild(typeof duration === 'number' ? duration : 0, String(body.stewbeet_version), String(body.python_version));
    // 204 rather than a body: the client closes the connection without reading, by design.
    return new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store' } });
}

/**
 * Handle one `POST /api/telemetry/event`, the beacon a tool that runs entirely in the browser sends.
 *
 * A tool the server does its work for is counted by the handler that did the work, which is both
 * accurate and impossible to inflate. This exists for the ones there is no server-side moment for,
 * and it accepts nothing else: an unknown stream, or one the registry counts server side, is
 * refused rather than quietly dropped, because a silent 204 would hide a typo at a call site.
 *
 * No duration is accepted. A number the browser made up is not worth averaging.
 *
 * @param req      The incoming request. Only POST exists; anything else is 405.
 * @param clientIp Caller address, used as the rate limit bucket and nothing else.
 */
export async function handleTelemetryEvent(req: Request, clientIp: string): Promise<Response> {
    if (req.method !== 'POST') {
        return json(405, { ok: false, error: 'method_not_allowed' }, { Allow: 'POST' });
    }

    let body: Record<string, unknown>;
    try {
        body = await req.json() as Record<string, unknown>;
    } catch {
        return json(400, { ok: false, error: 'invalid_body' });
    }

    const stream = typeof body.stream === 'string' ? findStream(body.stream) : undefined;
    if (!stream || stream.source !== 'client') {
        return json(400, { ok: false, error: 'unknown_stream' });
    }

    const labels: Record<string, string> = {};
    if (body.labels !== undefined) {
        if (typeof body.labels !== 'object' || body.labels === null || Array.isArray(body.labels)) {
            return json(400, { ok: false, error: 'invalid_body' });
        }
        const entries = Object.entries(body.labels as Record<string, unknown>);
        if (entries.length > MAX_LABELS_PER_EVENT) {
            return json(400, { ok: false, error: 'invalid_body' });
        }
        for (const [dimension, label] of entries) {
            // Unknown dimensions are dropped rather than refused: a page still counting a dimension
            // the registry no longer declares should keep counting, just without that breakdown.
            // Widened because the registry is `as const`, so `includes` would only take a literal.
            if (!(stream.dimensions as readonly string[]).includes(dimension) || dimension === DURATION_DIMENSION) continue;
            if (!isLabel(label)) return json(400, { ok: false, error: 'invalid_body' });
            labels[dimension] = label;
        }
    }

    if (eventLimiter.limited(clientIp)) {
        return json(429, { ok: false, error: 'rate_limited' });
    }

    recordEvent(stream.id, { labels });
    return new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store' } });
}

/**
 * The `cli` series in the shape `/api/telemetry/builds` has always returned.
 *
 * Exported because the tests read it directly. New readers want `streamSeries`, whose days are
 * `events` and whose breakdowns are a map rather than three named fields.
 *
 * @param days  Length of the window, already clamped.
 * @param today The day the window ends on.
 */
export function publicSeries(days: number, today: Date = new Date()): {
    days: { date: string; builds: number; avgDurationSeconds: number }[];
    total: number;
    avgDurationSeconds: number;
    breakdowns: Record<string, { label: string; count: number; percentage: number }[]>;
} {
    const series = streamSeries(DEFAULT_STREAM_ID, days, today);
    return {
        days: series.days.map(day => ({ date: day.date, builds: day.events, avgDurationSeconds: day.avgDurationSeconds })),
        total: series.total,
        avgDurationSeconds: series.avgDurationSeconds,
        breakdowns: {
            versions: series.breakdowns.versions ?? [],
            pythonVersions: series.breakdowns.pythonVersions ?? [],
            durationBuckets: series.breakdowns[DURATION_DIMENSION] ?? [],
        },
    };
}

/**
 * Handle one `GET /api/telemetry/builds?days=30`, which is the `cli` stream and nothing else.
 *
 * Kept at its original shape and meaning because it is documented on the telemetry page and anyone
 * may already be reading it. Everything added since is on `/streams`.
 */
export function handleTelemetryBuilds(url: URL): Response {
    return json(200, { ...publicSeries(queryDays(url)) }, {
        // Aggregates move once per build, and the page is not a live dashboard.
        'Cache-Control': 'public, max-age=300',
    });
}

/**
 * Handle one `GET /api/telemetry/streams?days=30`: every counter over one window, in one answer.
 *
 * One request rather than one per stream, because the page slides between them and a panel that
 * spins on arrival would make a swipe feel like a page load. The order and the labels come from the
 * registry, which the page imports directly, so they are not repeated in the payload.
 */
export function handleTelemetryStreams(url: URL): Response {
    const days = queryDays(url);
    return json(200, { days, streams: allStreams(days) }, {
        'Cache-Control': 'public, max-age=300',
    });
}

/** Test seam: drop the in-memory dataset and every rate limit bucket, so a case starts from the file. */
export function resetTelemetryState(): void {
    resetDataset();
    buildLimiter.hits.clear();
    eventLimiter.hits.clear();
}
