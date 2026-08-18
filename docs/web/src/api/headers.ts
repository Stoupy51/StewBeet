/**
 * The /api/tools/headers handler: forwards a datapack archive to the worker and streams the
 * rewritten one straight back.
 *
 * Nothing is cached and nothing is stored. A successful reply is the output archive itself, with
 * `Content-Type: application/zip`, so the browser holds the only copy and the download button is a
 * blob URL rather than a second round trip. A failure is JSON, which is how the page tells the two
 * apart. Caching would mean keeping tens of megabytes per caller in the web process for an hour, to
 * serve a second upload of the same pack that nobody makes.
 *
 * Uses **no `Bun.*` API**, like every module in this folder: server.tsx and the Vite dev middleware
 * both import it.
 */
import { acquire, json, queueFull, RateLimiter, release, workerBase } from './sandbox';
import { MAX_PACK_BYTES } from './sandboxLimits';

/** Longer than the worker's own 90 s wall clock ceiling, so its `timeout` reply wins the race. */
const WORKER_TIMEOUT_MS = 120_000;

/**
 * Small metadata the zip response cannot carry in its body: how long the run took, how many
 * functions were rewritten and what the analysis warned about. The worker caps it, and it is read
 * back verbatim, so nothing here has to trust its size.
 */
const META_HEADER = 'X-Sandbox-Meta';

/**
 * Stricter than the playground's ten a minute. One run reads a whole pack off the wire and spends
 * up to a minute of the worker's only CPU on it, so the budget is spent in far fewer requests.
 */
const limiter = new RateLimiter(4, 20);

/**
 * Handle one POST /api/tools/headers.
 *
 * @param req      The incoming request, whose body is the datapack archive. Only POST exists.
 * @param clientIp Caller address, resolved by the host since only it knows whether there is a
 *                 trusted proxy in front. Used as the rate limit bucket.
 */
export async function handleHeaders(req: Request, clientIp: string): Promise<Response> {
    if (req.method !== 'POST') {
        return json(405, { ok: false, error: 'method_not_allowed' }, { Allow: 'POST' });
    }

    const base = workerBase();
    if (!base) {
        return json(503, { ok: false, error: 'sandbox_disabled' });
    }

    // Read before the body, so an oversized upload is refused on its header rather than after
    // twenty-five megabytes have already been buffered.
    const declared = Number(req.headers.get('content-length') ?? '0');
    if (declared > MAX_PACK_BYTES) {
        return json(413, { ok: false, error: 'pack_too_large' });
    }

    const retryAfterMs = limiter.check(clientIp);
    if (retryAfterMs > 0) {
        return json(429, { ok: false, error: 'rate_limited', retryAfterMs }, {
            'Retry-After': String(Math.ceil(retryAfterMs / 1000)),
        });
    }

    let pack: ArrayBuffer;
    try {
        pack = await req.arrayBuffer();
    } catch {
        return json(400, { ok: false, error: 'invalid_body' });
    }
    // A chunked upload declares no length, so this is the check that actually holds.
    if (pack.byteLength > MAX_PACK_BYTES) {
        return json(413, { ok: false, error: 'pack_too_large' });
    }
    if (pack.byteLength === 0) {
        return json(400, { ok: false, error: 'invalid_body' });
    }

    if (queueFull()) {
        return json(503, { ok: false, error: 'busy' });
    }

    await acquire();
    try {
        const response = await fetch(`${base}/headers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/zip' },
            body: pack,
            signal: AbortSignal.timeout(WORKER_TIMEOUT_MS),
        });

        if (response.headers.get('content-type')?.startsWith('application/zip')) {
            return new Response(await response.arrayBuffer(), {
                status: 200,
                headers: {
                    'Content-Type': 'application/zip',
                    'Cache-Control': 'no-store',
                    [META_HEADER]: response.headers.get(META_HEADER) ?? '',
                },
            });
        }

        // Everything else is the worker's own JSON, forwarded rather than flattened into a generic
        // upstream failure: its 400s and 503s are about this request and the page can act on them.
        const body = await response.json() as Record<string, unknown>;
        return json(response.ok ? 500 : response.status, { ...body, ok: false });
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
