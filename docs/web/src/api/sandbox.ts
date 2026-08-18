/**
 * What every sandbox-backed tool shares: the worker address, the rate limit buckets and the single
 * build slot.
 *
 * There is one worker container, so there is one build slot, and it lives here rather than in
 * either handler: /api/playground and /api/tools/headers both go through it, and two independent
 * slots would let one of each run at the same time on a container sized for one.
 *
 * Both server.tsx and the Vite dev middleware import this, so it must use **no `Bun.*` API**.
 * Everything is `fetch`, `Request`, `Response` and `AbortSignal.timeout`, which both runtimes have.
 * That one constraint is what keeps development and production on a single implementation of the
 * limits, rather than on two that drift.
 *
 * Nothing here sandboxes anything. The worker on the other side runs in its own container on a
 * network with no gateway. What is here only decides who is allowed to ask, how often, and how long
 * they may wait.
 */

/**
 * The worker builds one at a time, so a second request waits and a third is turned away. Waiting
 * forever behind a queue is worse than being told to try again: the tab looks broken either way,
 * and only one of the two says so.
 */
const MAX_QUEUED = 2;

const HOUR_MS = 3_600_000;
const MINUTE_MS = 60_000;

export function json(status: number, body: Record<string, unknown>, headers: Record<string, string> = {}): Response {
    return new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers },
    });
}

/**
 * Base URL of the worker, or null when this deploy has none.
 *
 * Absent in development and on any deploy whose compose stack predates the worker, which is why
 * every caller answers `sandbox_disabled` rather than letting a connection error reach the page.
 *
 * SANDBOX_WORKER_URL is a base; PLAYGROUND_WORKER_URL was the endpoint itself and is still read so
 * that a host running an older compose file keeps a working playground after this deploy.
 */
export function workerBase(): string | null {
    const configured = process.env.SANDBOX_WORKER_URL ?? process.env.PLAYGROUND_WORKER_URL;
    if (!configured) return null;
    return configured.replace(/\/build\/?$/, '').replace(/\/$/, '');
}

/**
 * Per IP request timestamps for one tool, pruned on every lookup.
 *
 * Two windows rather than one: the per-minute one keeps a held-down key from monopolising the
 * single build slot, and the per-hour one stops someone from doing that all afternoon just under
 * the minute rate. One instance per tool, because a 25 MB pack costs far more than a rebuild of an
 * unchanged snippet and the two should not spend the same budget.
 */
export class RateLimiter {
    readonly hits = new Map<string, number[]>();
    readonly perMinute: number;
    readonly perHour: number;

    constructor(perMinute: number, perHour: number) {
        this.perMinute = perMinute;
        this.perHour = perHour;
    }

    /** Record one request and report how long the caller must wait, or 0 when it is allowed. */
    check(ip: string): number {
        const now = Date.now();
        const seen = (this.hits.get(ip) ?? []).filter(at => now - at < HOUR_MS);

        const lastMinute = seen.filter(at => now - at < MINUTE_MS);
        if (lastMinute.length >= this.perMinute) {
            this.hits.set(ip, seen);
            return MINUTE_MS - (now - lastMinute[0]);
        }
        if (seen.length >= this.perHour) {
            this.hits.set(ip, seen);
            return HOUR_MS - (now - seen[0]);
        }

        seen.push(now);
        this.hits.set(ip, seen);
        // Without this the map grows one entry per address seen, for the lifetime of the process.
        if (this.hits.size > 10_000) {
            for (const [key, times] of this.hits) {
                if (times.every(at => now - at > HOUR_MS)) this.hits.delete(key);
            }
        }
        return 0;
    }
}

let building = false;
const waiting: (() => void)[] = [];

/** Whether the queue in front of the single slot is already as long as it is allowed to get. */
export function queueFull(): boolean {
    return building && waiting.length >= MAX_QUEUED;
}

export async function acquire(): Promise<void> {
    if (!building) {
        building = true;
        return;
    }
    return new Promise<void>(resolve => waiting.push(resolve));
}

export function release(): void {
    const next = waiting.shift();
    if (next) next();
    else building = false;
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
