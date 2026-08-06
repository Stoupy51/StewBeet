/**
 * Fetches the project's public numbers once at build time and writes them to
 * src/generated/stats.json, which the trust strip reads synchronously.
 *
 * The site used to ask the GitHub tags API for the version on every page load: an
 * unauthenticated, per-IP, 60-requests-per-hour endpoint that silently fell back to a
 * hardcoded string. Baking the values into the bundle removes that request from the
 * critical path and lets the prerendered HTML carry real numbers.
 *
 * A metric that cannot be fetched is written as null and dropped from the strip rather
 * than rendered stale: a wrong number costs more trust than a missing one. The file is
 * committed, so a build with no network keeps the previous values instead of emptying.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

const OUTPUT_PATH: string = join(import.meta.dir, '..', 'src', 'generated', 'stats.json');

/** Shape written to disk. `null` means "could not fetch"; the UI omits those tiles. */
interface Stats {
    version: string | null;
    releasedAt: string | null;
    stars: number | null;
    downloadsPerMonth: number | null;
    fetchedAt: string;
}

async function fetchJson<T>(url: string): Promise<T | null> {
    try {
        const response = await fetch(url, {
            headers: { 'User-Agent': 'stewbeet-website-build' },
            signal: AbortSignal.timeout(10_000),
        });
        if (!response.ok) return null;
        return (await response.json()) as T;
    } catch {
        return null;
    }
}

function readPrevious(): Partial<Stats> {
    try {
        return JSON.parse(readFileSync(OUTPUT_PATH, 'utf-8')) as Partial<Stats>;
    } catch {
        return {};
    }
}

const previous = readPrevious();

const release = await fetchJson<{ tag_name?: string; published_at?: string }>(
    'https://api.github.com/repos/Stoupy51/StewBeet/releases/latest',
);
const repo = await fetchJson<{ stargazers_count?: number }>(
    'https://api.github.com/repos/Stoupy51/StewBeet',
);
const downloads = await fetchJson<{ data?: { last_month?: number } }>(
    'https://pypistats.org/api/packages/stewbeet/recent',
);

const tag = release?.tag_name;

const stats: Stats = {
    version: (tag?.startsWith('v') ? tag.slice(1) : tag) ?? previous.version ?? null,
    releasedAt: release?.published_at ?? previous.releasedAt ?? null,
    stars: repo?.stargazers_count ?? previous.stars ?? null,
    downloadsPerMonth: downloads?.data?.last_month ?? previous.downloadsPerMonth ?? null,
    fetchedAt: new Date().toISOString(),
};

mkdirSync(join(import.meta.dir, '..', 'src', 'generated'), { recursive: true });
writeFileSync(OUTPUT_PATH, `${JSON.stringify(stats, null, 4)}\n`);

const reported = Object.entries(stats)
    .filter(([key]) => key !== 'fetchedAt')
    .map(([key, value]) => `${key}=${value ?? 'unavailable'}`)
    .join(' ');
console.log(`[build-stats] ${reported}`);
