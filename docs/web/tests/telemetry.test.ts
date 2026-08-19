/**
 * Tests for src/api/telemetry.ts, run with `bun test`.
 *
 * They live outside src/ on purpose: `bun:test` has no types in this project's tsconfigs, and
 * adding them to typecheck a test file would put a test-only dependency in the way of `bun run build`.
 *
 * TELEMETRY_DATA_DIR is set before the import because the module reads it once, at module scope.
 */
import { afterAll, beforeEach, describe, expect, test } from 'bun:test';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const dataDir = mkdtempSync(join(tmpdir(), 'stewbeet-telemetry-'));
process.env.TELEMETRY_DATA_DIR = dataDir;

const {
    allStreams, countBuild, dayKey, handleTelemetryBuild, handleTelemetryBuilds, handleTelemetryEvent,
    handleTelemetryStreams, publicSeries, recordEvent, resetTelemetryState, streamSeries, windowDays,
} = await import('../src/api/telemetry/index.ts');

const { bucketOf, durationBucket, inputSizeBucket, packSizeBucket } = await import('../src/api/telemetry/streams.ts');

afterAll(() => rmSync(dataDir, { recursive: true, force: true }));

/** Fresh process state and a fresh file for every case, so nothing leaks between them. */
beforeEach(() => {
    rmSync(join(dataDir, 'builds.json'), { force: true });
    resetTelemetryState();
});

function post(body: unknown, ip = '10.0.0.1'): Promise<Response> {
    return handleTelemetryBuild(
        new Request('http://localhost/api/telemetry/build', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }),
        ip,
    );
}

function postEvent(body: unknown, ip = '10.0.0.1'): Promise<Response> {
    return handleTelemetryEvent(
        new Request('http://localhost/api/telemetry/event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }),
        ip,
    );
}

const validBody = { stewbeet_version: '3.6.3', python_version: '3.14.7', duration_seconds: 12.5 };

describe('the build endpoint', () => {
    test('accepts a documented payload and counts it', async () => {
        expect((await post(validBody)).status).toBe(204);
        expect(publicSeries(30).total).toBe(1);
        expect(publicSeries(30).breakdowns.versions).toEqual([
            { label: '3.6.3', count: 1, percentage: 100 },
        ]);
    });

    test('accepts a client that predates duration_seconds', async () => {
        expect((await post({ stewbeet_version: '3.6.3', python_version: '3.14.7' })).status).toBe(204);
        expect(publicSeries(30).total).toBe(1);
    });

    test('ignores undocumented fields instead of storing them', async () => {
        await post({ ...validBody, project_name: 'SimplEnergy', hostname: 'stoupy-pc' });
        const stored = JSON.stringify(await Bun.file(join(dataDir, 'builds.json')).json());
        expect(stored).not.toContain('SimplEnergy');
        expect(stored).not.toContain('stoupy-pc');
        expect(stored).not.toContain('10.0.0.1');
    });

    test('refuses a body without the documented fields', async () => {
        for (const body of [{}, { stewbeet_version: '3.6.3' }, { stewbeet_version: 1, python_version: '3.14.7' }]) {
            expect((await post(body)).status).toBe(400);
        }
        expect(publicSeries(30).total).toBe(0);
    });

    test('refuses a duration that could not have been a build', async () => {
        for (const duration_seconds of [-1, Number.NaN, 1e9, '3.5']) {
            expect((await post({ ...validBody, duration_seconds })).status).toBe(400);
        }
        expect(publicSeries(30).total).toBe(0);
    });

    test('answers 405 to anything but POST', async () => {
        const response = await handleTelemetryBuild(new Request('http://localhost/api/telemetry/build'), '10.0.0.1');
        expect(response.status).toBe(405);
        expect(response.headers.get('Allow')).toBe('POST');
    });

    test('rate limits one address without touching the others', async () => {
        let refused = 0;
        for (let i = 0; i < 200; i++) {
            if ((await post(validBody)).status === 429) refused++;
        }
        expect(refused).toBeGreaterThan(0);
        expect((await post(validBody, '10.0.0.2')).status).toBe(204);
    });
});

describe('the public series', () => {
    test('returns exactly the requested window, ending today', () => {
        const today = new Date('2026-08-16T09:00:00Z');
        const series = publicSeries(30, today);
        expect(series.days).toHaveLength(30);
        expect(series.days[0].date).toBe('2026-07-18');
        expect(series.days[29].date).toBe('2026-08-16');
    });

    test('reports a day with no builds as zero rather than omitting it', () => {
        const today = new Date('2026-08-16T09:00:00Z');
        countBuild(10, '3.6.3', '3.14.7', new Date('2026-08-14T09:00:00Z'));
        const series = publicSeries(30, today);
        expect(series.days.filter(day => day.builds > 0)).toHaveLength(1);
        expect(series.days.every(day => typeof day.builds === 'number')).toBe(true);
        expect(series.days.find(day => day.date === '2026-08-15')).toEqual({ date: '2026-08-15', builds: 0, avgDurationSeconds: 0 });
    });

    test('collapses several builds of one day into one row, never a list of events', () => {
        const at = new Date('2026-08-16T09:00:00Z');
        countBuild(10, '3.6.3', '3.14.7', at);
        countBuild(20, '3.6.3', '3.14.7', new Date('2026-08-16T23:00:00Z'));
        const series = publicSeries(30, at);

        expect(Object.keys(series).sort()).toEqual(['avgDurationSeconds', 'breakdowns', 'days', 'total']);
        for (const day of series.days) {
            expect(Object.keys(day).sort()).toEqual(['avgDurationSeconds', 'builds', 'date']);
        }
        expect(series.days.at(-1)).toEqual({ date: '2026-08-16', builds: 2, avgDurationSeconds: 15 });
        expect(series.total).toBe(2);
        expect(series.avgDurationSeconds).toBe(15);
        expect(series.breakdowns.versions).toEqual([
            { label: '3.6.3', count: 2, percentage: 100 },
        ]);
        expect(series.breakdowns.pythonVersions).toEqual([
            { label: '3.14.7', count: 2, percentage: 100 },
        ]);
    });

    test('clamps the window a caller asks for', async () => {
        const read = async (query: string): Promise<number> => {
            const response = handleTelemetryBuilds(new URL(`http://localhost/api/telemetry/builds${query}`));
            return ((await response.json()) as { days: unknown[] }).days.length;
        };
        expect(await read('')).toBe(30);
        expect(await read('?days=7')).toBe(7);
        expect(await read('?days=99999')).toBe(365);
        expect(await read('?days=0')).toBe(1);
        expect(await read('?days=nonsense')).toBe(30);
    });

    test('reads back what the endpoint accumulated, and only that', async () => {
        await post(validBody);
        const body = await handleTelemetryBuilds(new URL('http://localhost/api/telemetry/builds?days=30')).json() as {
            days: { date: string; builds: number }[];
            total: number;
            breakdowns: {
                versions: Array<{ label: string; count: number; percentage: number }>;
                pythonVersions: Array<{ label: string; count: number; percentage: number }>;
                durationBuckets: Array<{ label: string; count: number; percentage: number }>;
            };
        };
        expect(body.total).toBe(1);
        expect(body.days.at(-1)).toMatchObject({ date: dayKey(new Date()), builds: 1 });
        expect(body.breakdowns.versions).toEqual([
            { label: '3.6.3', count: 1, percentage: 100 },
        ]);
        expect(body.breakdowns.pythonVersions).toEqual([
            { label: '3.14.7', count: 1, percentage: 100 },
        ]);
        expect(body.breakdowns.durationBuckets).toEqual([
            { label: '10s-15s', count: 1, percentage: 100 },
        ]);
    });
});

describe('the day window helper', () => {
    test('walks back day by day, oldest first', () => {
        expect(windowDays(3, new Date('2026-03-02T12:00:00Z'))).toEqual(['2026-02-28', '2026-03-01', '2026-03-02']);
    });

    test('keys a build by its UTC day, whatever hour it arrived', () => {
        expect(dayKey(new Date('2026-08-16T23:59:59Z'))).toBe('2026-08-16');
        expect(dayKey(new Date('2026-08-17T00:00:01Z'))).toBe('2026-08-17');
    });
});

describe('the event endpoint', () => {
    const conversion = { stream: 'markdown_to_bbcode', labels: { actions: 'copy', inputSizes: '1k-5k' } };

    test('counts a use of a browser-only tool', async () => {
        expect((await postEvent(conversion)).status).toBe(204);
        const series = streamSeries('markdown_to_bbcode', 30);
        expect(series.total).toBe(1);
        expect(series.breakdowns.actions).toEqual([{ label: 'copy', count: 1, percentage: 100 }]);
        expect(series.breakdowns.inputSizes).toEqual([{ label: '1k-5k', count: 1, percentage: 100 }]);
    });

    test('refuses to let a browser add to a counter the server keeps itself', async () => {
        for (const stream of ['cli', 'playground', 'auto_headers']) {
            expect((await postEvent({ stream })).status).toBe(400);
        }
        expect(streamSeries('cli', 30).total).toBe(0);
        expect(streamSeries('playground', 30).total).toBe(0);
        expect(streamSeries('auto_headers', 30).total).toBe(0);
    });

    test('refuses a stream that is not in the registry', async () => {
        expect((await postEvent({ stream: 'made_up' })).status).toBe(400);
        expect((await postEvent({})).status).toBe(400);
    });

    test('refuses a label that could not be a label', async () => {
        expect((await postEvent({ stream: 'markdown_to_bbcode', labels: { actions: 'x'.repeat(64) } })).status).toBe(400);
        expect((await postEvent({ stream: 'markdown_to_bbcode', labels: { actions: 'copy\n; DROP' } })).status).toBe(400);
        expect(streamSeries('markdown_to_bbcode', 30).total).toBe(0);
    });

    test('drops a dimension the stream does not declare rather than refusing the event', async () => {
        expect((await postEvent({ stream: 'markdown_to_bbcode', labels: { actions: 'copy', versions: '3.6.3' } })).status).toBe(204);
        const series = streamSeries('markdown_to_bbcode', 30);
        expect(series.total).toBe(1);
        expect(Object.keys(series.breakdowns).sort()).toEqual(['actions', 'inputSizes']);
    });

    test('never records what the browser sent beyond the two labels', async () => {
        await postEvent({ ...conversion, text: 'my unreleased datapack', labels: { ...conversion.labels } });
        const stored = JSON.stringify(await Bun.file(join(dataDir, 'builds.json')).json());
        expect(stored).not.toContain('unreleased');
        expect(stored).not.toContain('10.0.0.1');
    });

    test('spends its own hourly budget, not the build endpoint one', async () => {
        let refused = 0;
        for (let i = 0; i < 200; i++) {
            if ((await postEvent(conversion)).status === 429) refused++;
        }
        expect(refused).toBeGreaterThan(0);
        expect((await post(validBody)).status).toBe(204);
    });

    test('answers 405 to anything but POST', async () => {
        const response = await handleTelemetryEvent(new Request('http://localhost/api/telemetry/event'), '10.0.0.1');
        expect(response.status).toBe(405);
        expect(response.headers.get('Allow')).toBe('POST');
    });
});

describe('the stream registry', () => {
    test('keeps one counter apart from another', () => {
        const at = new Date('2026-08-16T09:00:00Z');
        recordEvent('playground', { durationSeconds: 2, labels: { outcomes: 'ok' } }, at);
        recordEvent('auto_headers', { durationSeconds: 8, labels: { outcomes: 'ok', packSizes: '1-5 MB' } }, at);

        expect(streamSeries('playground', 30, at).total).toBe(1);
        expect(streamSeries('auto_headers', 30, at).total).toBe(1);
        expect(streamSeries('cli', 30, at).total).toBe(0);
    });

    test('fills the duration breakdown from the event, and only where it is declared', () => {
        const at = new Date('2026-08-16T09:00:00Z');
        recordEvent('playground', { durationSeconds: 12.5, labels: { outcomes: 'ok' } }, at);
        recordEvent('markdown_to_bbcode', { labels: { actions: 'copy' } }, at);

        expect(streamSeries('playground', 30, at).breakdowns.durationBuckets).toEqual([
            { label: '10s-15s', count: 1, percentage: 100 },
        ]);
        expect(streamSeries('markdown_to_bbcode', 30, at).breakdowns.durationBuckets).toBeUndefined();
    });

    test('ignores an id that is not registered instead of inventing a counter', () => {
        const at = new Date('2026-08-16T09:00:00Z');
        // @ts-expect-error: exactly the typo the literal union exists to catch at a call site.
        recordEvent('playgroudn', { labels: { outcomes: 'ok' } }, at);
        expect(streamSeries('playgroudn', 30, at)).toMatchObject({ total: 0, breakdowns: {} });
        expect(Object.keys(allStreams(30, at))).not.toContain('playgroudn');
    });

    test('folds a runaway dimension into one label rather than growing without bound', () => {
        const at = new Date('2026-08-16T09:00:00Z');
        for (let i = 0; i < 200; i++) {
            recordEvent('markdown_to_bbcode', { labels: { actions: `action${i}` } }, at);
        }
        const actions = streamSeries('markdown_to_bbcode', 30, at).breakdowns.actions;
        expect(actions.length).toBeLessThanOrEqual(61);
        expect(actions[0]).toMatchObject({ label: 'other' });
        expect(actions.reduce((sum, item) => sum + item.count, 0)).toBe(200);
    });

    test('answers for every registered counter over one window', async () => {
        const body = await handleTelemetryStreams(new URL('http://localhost/api/telemetry/streams?days=7')).json() as {
            days: number;
            streams: Record<string, { days: unknown[]; total: number }>;
        };
        expect(body.days).toBe(7);
        expect(Object.keys(body.streams).sort()).toEqual(['auto_headers', 'cli', 'markdown_to_bbcode', 'playground']);
        for (const series of Object.values(body.streams)) {
            expect(series.days).toHaveLength(7);
        }
    });
});

describe('the stored file', () => {
    test('reads a file written before there was more than one counter', async () => {
        const at = new Date('2026-08-16T09:00:00Z');
        await Bun.write(join(dataDir, 'builds.json'), JSON.stringify({
            version: 2,
            days: {
                '2026-08-15': {
                    builds: 3,
                    seconds: 30,
                    versions: { '3.6.3': 3 },
                    pythonVersions: { '3.14.7': 3 },
                    durationBuckets: { '10s-15s': 3 },
                },
            },
        }));
        resetTelemetryState();

        const series = publicSeries(30, at);
        expect(series.total).toBe(3);
        expect(series.avgDurationSeconds).toBe(10);
        expect(series.days.find(day => day.date === '2026-08-15')).toEqual({ date: '2026-08-15', builds: 3, avgDurationSeconds: 10 });
        expect(series.breakdowns.versions).toEqual([{ label: '3.6.3', count: 3, percentage: 100 }]);
        expect(series.breakdowns.durationBuckets).toEqual([{ label: '10s-15s', count: 3, percentage: 100 }]);
    });

    test('keeps the migrated history when the next event is written', async () => {
        await Bun.write(join(dataDir, 'builds.json'), JSON.stringify({
            version: 2,
            days: { '2026-08-15': { builds: 3, seconds: 30, versions: {}, pythonVersions: {}, durationBuckets: {} } },
        }));
        resetTelemetryState();

        recordEvent('playground', { labels: { outcomes: 'ok' } }, new Date('2026-08-16T09:00:00Z'));
        const written = await Bun.file(join(dataDir, 'builds.json')).json() as {
            version: number;
            streams: Record<string, Record<string, { events: number }>>;
        };
        expect(written.version).toBe(3);
        expect(written.streams.cli['2026-08-15'].events).toBe(3);
        expect(written.streams.playground['2026-08-16'].events).toBe(1);
    });

    test('treats an unreadable file as empty rather than taking the site down', async () => {
        await Bun.write(join(dataDir, 'builds.json'), 'not json at all');
        resetTelemetryState();
        expect(publicSeries(30).total).toBe(0);
        expect(Object.keys(allStreams(30))).toHaveLength(4);
    });
});

describe('the bucket labels', () => {
    test('names the band a measurement falls in, with the unit written once', () => {
        expect(bucketOf(0.2, [1, 5, 10], ' MB')).toBe('<1 MB');
        expect(bucketOf(3, [1, 5, 10], ' MB')).toBe('1-5 MB');
        expect(bucketOf(40, [1, 5, 10], ' MB')).toBe('10 MB+');
    });

    test('puts a boundary in the band it opens, not the one it closes', () => {
        expect(bucketOf(1, [1, 5], ' MB')).toBe('1-5 MB');
        expect(bucketOf(5, [1, 5], ' MB')).toBe('5 MB+');
    });

    test('treats a measurement that is not a number as zero', () => {
        expect(bucketOf(Number.NaN, [1, 5], ' MB')).toBe('<1 MB');
        expect(bucketOf(-4, [1, 5], ' MB')).toBe('<1 MB');
        expect(durationBucket(Number.POSITIVE_INFINITY)).toBe('0s-5s');
    });

    test('labels a duration in five second bands', () => {
        expect(durationBucket(0)).toBe('0s-5s');
        expect(durationBucket(12.5)).toBe('10s-15s');
    });

    test('labels an upload and a pasted document by size', () => {
        expect(packSizeBucket(500_000)).toBe('<1 MB');
        expect(packSizeBucket(3_000_000)).toBe('1-5 MB');
        expect(packSizeBucket(24_000_000)).toBe('20 MB+');
        expect(inputSizeBucket(400)).toBe('<1k');
        expect(inputSizeBucket(3_500)).toBe('1-5k');
        expect(inputSizeBucket(90_000)).toBe('20k+');
    });
});
