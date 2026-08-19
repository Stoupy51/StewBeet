/**
 * The usage beacon for a tool that runs entirely in the browser.
 *
 * Most tools are counted by the server handler that did their work, which is both accurate and
 * impossible to inflate. This is for the ones the server never hears about, and it is deliberately
 * the weaker half: it sends the name of the tool and a couple of coarse labels, it sends them after
 * the work the reader asked for is already done, and it can fail without anyone noticing.
 *
 * Nothing identifying is sent, and nothing is read back. See src/api/telemetry/ for what is kept.
 */
import { type StreamId } from '../api/telemetry/streams';

const ENDPOINT = '/api/telemetry/event';

/**
 * Count one use of a browser-only tool, without ever getting in its way.
 *
 * `sendBeacon` first, because it survives the tab closing a moment later, with `fetch` behind it
 * for the browsers that refuse the beacon or have already filled their queue. Both are fire and
 * forget: a counter that could throw would be a counter that breaks the tool it counts.
 *
 * @param stream One of the registry ids, checked at compile time.
 * @param labels Dimension name to label, ex: `{ actions: 'copy' }`. Unknown ones are dropped server side.
 */
export function reportToolUse(stream: StreamId, labels: Record<string, string> = {}): void {
    if (typeof navigator === 'undefined') return;

    const body = JSON.stringify({ stream, labels });
    try {
        if (navigator.sendBeacon(ENDPOINT, new Blob([body], { type: 'application/json' }))) return;
        void fetch(ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body,
            keepalive: true,
        }).catch(() => undefined);
    } catch {
        // A blocked request, an extension, a browser without either: none of it is worth a broken tool.
    }
}
