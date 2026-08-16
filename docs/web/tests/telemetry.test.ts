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

const { countBuild, dayKey, handleTelemetryBuild, handleTelemetryBuilds, publicSeries, resetTelemetryState, windowDays } =
    await import('../src/api/telemetry.ts');

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

const validBody = { stewbeet_version: '3.6.3', python_version: '3.14.7', duration_seconds: 12.5 };

describe('the build endpoint', () => {
    test('accepts a documented payload and counts it', async () => {
        expect((await post(validBody)).status).toBe(204);
        expect(publicSeries(30).total).toBe(1);
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
        countBuild(10, new Date('2026-08-14T09:00:00Z'));
        const series = publicSeries(30, today);
        expect(series.days.filter(day => day.builds > 0)).toHaveLength(1);
        expect(series.days.every(day => typeof day.builds === 'number')).toBe(true);
        expect(series.days.find(day => day.date === '2026-08-15')).toEqual({ date: '2026-08-15', builds: 0, avgDurationSeconds: 0 });
    });

    test('collapses several builds of one day into one row, never a list of events', () => {
        const at = new Date('2026-08-16T09:00:00Z');
        countBuild(10, at);
        countBuild(20, new Date('2026-08-16T23:00:00Z'));
        const series = publicSeries(30, at);

        expect(Object.keys(series).sort()).toEqual(['avgDurationSeconds', 'days', 'total']);
        for (const day of series.days) {
            expect(Object.keys(day).sort()).toEqual(['avgDurationSeconds', 'builds', 'date']);
        }
        expect(series.days.at(-1)).toEqual({ date: '2026-08-16', builds: 2, avgDurationSeconds: 15 });
        expect(series.total).toBe(2);
        expect(series.avgDurationSeconds).toBe(15);
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
        };
        expect(body.total).toBe(1);
        expect(body.days.at(-1)).toMatchObject({ date: dayKey(new Date()), builds: 1 });
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
