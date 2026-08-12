/**
 * The /api/playground handler: rate limits, the result cache and the single build slot.
 *
 * Both server.tsx and the Vite dev middleware import this, so it must use **no `Bun.*` API**.
 * Everything here is `node:crypto`, `fetch`, `Request`, `Response` and `AbortSignal.timeout`, which
 * both runtimes have. That one constraint is what keeps development and production on a single
 * implementation of the limits, rather than on two that drift.
 *
 * It does not sandbox anything. The worker on the other side of `PLAYGROUND_WORKER_URL` runs in its
 * own container on a network with no gateway, because StewBeet executes submitted Python by design
 * and bolt hands it every builtin including `exec` and `open`. What is here only decides who is
 * allowed to ask, how often, and how long they may wait.
 */
import { createHash } from 'node:crypto';
import { MAX_CODE_BYTES } from './playgroundLimits';

const RATE_PER_MINUTE = 10;
const RATE_PER_HOUR = 60;

/**
 * The worker builds one at a time, so a second request waits and a third is turned away. Waiting
 * forever behind a queue is worse than being told to try again: the tab looks broken either way,
 * and only one of the two says so.
 */
const MAX_QUEUED = 2;

/** Longer than the worker's own 20 s wall clock ceiling, so its `timeout` reply wins the race. */
const WORKER_TIMEOUT_MS = 30_000;

const CACHE_ENTRIES = 200;
const CACHE_TTL_MS = 60 * 60 * 1000;

interface CacheEntry {
    at: number;
    body: Record<string, unknown>;
}

/** Per IP request timestamps, pruned on every lookup. */
const hits = new Map<string, number[]>();

/** sha256(code) -> result. Insertion ordered, so the oldest key is the first one out. */
const cache = new Map<string, CacheEntry>();

let building = false;
const waiting: (() => void)[] = [];

function json(status: number, body: Record<string, unknown>, headers: Record<string, string> = {}): Response {
    return new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers },
    });
}

/**
 * Record one request and report whether the caller has gone over either window.
 *
 * Two windows rather than one: ten a minute keeps a held-down key from monopolising the single
 * build slot, and sixty an hour stops someone from doing that all afternoon at nine a minute.
 */
function rateLimited(ip: string): number {
    const now = Date.now();
    const seen = (hits.get(ip) ?? []).filter(at => now - at < 3_600_000);

    const lastMinute = seen.filter(at => now - at < 60_000);
    if (lastMinute.length >= RATE_PER_MINUTE) {
        hits.set(ip, seen);
        return 60_000 - (now - lastMinute[0]);
    }
    if (seen.length >= RATE_PER_HOUR) {
        hits.set(ip, seen);
        return 3_600_000 - (now - seen[0]);
    }

    seen.push(now);
    hits.set(ip, seen);
    // Without this the map grows one entry per address seen, for the lifetime of the process.
    if (hits.size > 10_000) {
        for (const [key, times] of hits) {
            if (times.every(at => now - at > 3_600_000)) hits.delete(key);
        }
    }
    return 0;
}

function cached(key: string): Record<string, unknown> | null {
    const entry = cache.get(key);
    if (!entry) return null;
    if (Date.now() - entry.at > CACHE_TTL_MS) {
        cache.delete(key);
        return null;
    }
    // Re-insert so the most recently used key is last, and eviction takes the coldest.
    cache.delete(key);
    cache.set(key, entry);
    return entry.body;
}

function remember(key: string, body: Record<string, unknown>): void {
    cache.set(key, { at: Date.now(), body });
    while (cache.size > CACHE_ENTRIES) {
        const oldest = cache.keys().next();
        if (oldest.done) break;
        cache.delete(oldest.value);
    }
}

async function acquire(): Promise<void> {
    if (!building) {
        building = true;
        return;
    }
    return new Promise<void>(resolve => waiting.push(resolve));
}

function release(): void {
    const next = waiting.shift();
    if (next) next();
    else building = false;
}

/**
 * Handle one POST /api/playground.
 *
 * @param req      The incoming request. Only POST exists; anything else is 405.
 * @param clientIp Caller address, resolved by the host since only it knows whether there is a
 *                 trusted proxy in front. Used as the rate limit bucket.
 */
export async function handlePlayground(req: Request, clientIp: string): Promise<Response> {
    if (req.method !== 'POST') {
        return json(405, { ok: false, error: 'method_not_allowed' }, { Allow: 'POST' });
    }

    // Absent in development and on any deploy whose compose stack predates the worker. Answering
    // clearly beats a connection error the page cannot explain to the reader.
    const workerUrl = process.env.PLAYGROUND_WORKER_URL;
    if (!workerUrl) {
        return json(503, { ok: false, error: 'playground_disabled' });
    }

    let code: string;
    try {
        const body = await req.json() as { code?: unknown };
        if (typeof body.code !== 'string' || body.code.trim() === '') {
            return json(400, { ok: false, error: 'invalid_body' });
        }
        code = body.code;
    } catch {
        return json(400, { ok: false, error: 'invalid_body' });
    }

    // TextEncoder rather than Buffer: both runtimes have it, and it keeps this module free of
    // anything Node specific beyond the one crypto import.
    if (new TextEncoder().encode(code).length > MAX_CODE_BYTES) {
        return json(400, { ok: false, error: 'code_too_large' });
    }

    const key = createHash('sha256').update(code).digest('hex');

    // Deliberately before the rate limit and the build slot. Re-running a build nobody has changed
    // costs nothing, so it should not consume either budget, and the page stays responsive while a
    // reader clicks between files.
    const hit = cached(key);
    if (hit) {
        return json(200, { ...hit, cached: true });
    }

    const retryAfterMs = rateLimited(clientIp);
    if (retryAfterMs > 0) {
        return json(429, { ok: false, error: 'rate_limited', retryAfterMs }, {
            'Retry-After': String(Math.ceil(retryAfterMs / 1000)),
        });
    }

    if (building && waiting.length >= MAX_QUEUED) {
        return json(503, { ok: false, error: 'busy' });
    }

    await acquire();
    try {
        const response = await fetch(workerUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
            signal: AbortSignal.timeout(WORKER_TIMEOUT_MS),
        });

        const body = await response.json() as Record<string, unknown>;
        if (!response.ok) {
            // The worker's own 400s and 503s are about this request, so they are forwarded rather
            // than flattened into a generic upstream failure.
            return json(response.status, { ...body, ok: false });
        }

        // Only a successful build is worth keeping. Caching a failure would pin someone's typo for
        // an hour and hide the fix.
        if (body.ok === true) {
            remember(key, body);
        }
        return json(200, { ...body, cached: false });
    } catch (error) {
        const timedOut = error instanceof Error && (error.name === 'TimeoutError' || error.name === 'AbortError');
        return json(timedOut ? 504 : 502, {
            ok: false,
            error: timedOut ? 'timeout' : 'worker_unavailable',
        });
    } finally {
        release();
    }
}

/**
 * Caller address for the rate limit bucket.
 *
 * `x-forwarded-for` is only read when TRUST_PROXY is set, because a client can send that header
 * itself: trusting it unconditionally would let anyone pick their own bucket, and rate limiting
 * would become opt-in. Behind Traefik the socket address is the proxy, so it has to be read there.
 *
 * @param req         The incoming request.
 * @param socketIp    Address of the connection, or an empty string when the host cannot say.
 */
export function clientIpFrom(req: Request, socketIp: string): string {
    if (process.env.TRUST_PROXY === '1') {
        const forwarded = req.headers.get('x-forwarded-for');
        if (forwarded) return forwarded.split(',')[0].trim();
    }
    return socketIp || 'unknown';
}
