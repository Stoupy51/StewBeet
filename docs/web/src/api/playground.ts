/**
 * The /api/playground handler: the result cache, and the request checks around it.
 *
 * The worker address, the rate limit buckets and the single build slot are shared with the other
 * sandbox-backed tools and live in sandbox.ts. Like it, this module uses **no `Bun.*` API**, since
 * server.tsx and the Vite dev middleware both import it.
 */
import { createHash } from 'node:crypto';
import { acquire, json, outcomeOf, queueFull, RateLimiter, release, workerBase } from './sandbox';
import { MAX_CODE_BYTES } from './sandboxLimits';
import { recordEvent } from './telemetry';

/** Longer than the worker's own 20 s wall clock ceiling, so its `timeout` reply wins the race. */
const WORKER_TIMEOUT_MS = 30_000;

const CACHE_ENTRIES = 200;
const CACHE_TTL_MS = 60 * 60 * 1000;

interface CacheEntry {
    at: number;
    body: Record<string, unknown>;
}

const limiter = new RateLimiter(10, 60);

/** sha256(code) -> result. Insertion ordered, so the oldest key is the first one out. */
const cache = new Map<string, CacheEntry>();

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

    const base = workerBase();
    if (!base) {
        return json(503, { ok: false, error: 'sandbox_disabled' });
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
    const startedAt = Date.now();

    // Counted here rather than at each return: what /telemetry shows is runs the worker was asked
    // for, so a malformed body, a rate limited caller and the cache hit below are all absent, and
    // every way a real run can end is present with the reason it ended that way. The cache hit in
    // particular has to stay out: it is answered before the rate limiter, so counting it would be
    // a number anyone could run up by pressing the same button.
    const count = (outcome: string): void => {
        recordEvent('playground', { durationSeconds: (Date.now() - startedAt) / 1000, labels: { outcomes: outcome } });
    };

    // Deliberately before the rate limit and the build slot. Re-running a build nobody has changed
    // costs nothing, so it should not consume either budget, and the page stays responsive while a
    // reader clicks between files.
    const hit = cached(key);
    if (hit) {
        return json(200, { ...hit, cached: true });
    }

    const retryAfterMs = limiter.check(clientIp);
    if (retryAfterMs > 0) {
        return json(429, { ok: false, error: 'rate_limited', retryAfterMs }, {
            'Retry-After': String(Math.ceil(retryAfterMs / 1000)),
        });
    }

    if (queueFull()) {
        count('busy');
        return json(503, { ok: false, error: 'busy' });
    }

    await acquire();
    try {
        const response = await fetch(`${base}/build`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
            signal: AbortSignal.timeout(WORKER_TIMEOUT_MS),
        });

        const body = await response.json() as Record<string, unknown>;
        if (!response.ok) {
            // The worker's own 400s and 503s are about this request, so they are forwarded rather
            // than flattened into a generic upstream failure.
            count(outcomeOf(body));
            return json(response.status, { ...body, ok: false });
        }

        // Only a successful build is worth keeping. Caching a failure would pin someone's typo for
        // an hour and hide the fix.
        if (body.ok === true) {
            remember(key, body);
        }
        count(outcomeOf(body));
        return json(200, { ...body, cached: false });
    } catch (error) {
        const timedOut = error instanceof Error && (error.name === 'TimeoutError' || error.name === 'AbortError');
        count(timedOut ? 'timeout' : 'worker_unavailable');
        return json(timedOut ? 504 : 502, {
            ok: false,
            error: timedOut ? 'timeout' : 'worker_unavailable',
        });
    } finally {
        release();
    }
}
