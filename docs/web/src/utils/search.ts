/**
 * Full-text search over the documentation.
 *
 * Markdown guides, plugin pages and Python API symbols come from the index built by
 * scripts/build-search-index.ts and fetched on first use. Landing-page sections are
 * derived from the i18n translations, which are already in the bundle.
 */
import type { Language } from '../context/LanguageContext';
import { translations } from '../i18n/translations';

export type EntryType = 'doc' | 'plugin' | 'api' | 'site';

/** One searchable unit: a markdown heading section, an API symbol, or a site section. */
export interface SearchEntry {
    /** Entry kind. */
    t: EntryType;
    /** `src` param (doc, plugin), Sphinx-relative uri (api), or route (site). */
    p: string;
    /** Document label shown in the result row. */
    d: string;
    /** Heading or symbol name. */
    h: string;
    /** Anchor slug within the document, may be empty. */
    a: string;
    /** Searchable body text. */
    b: string;
}

/** An entry with its fields pre-normalized, so typing does not re-normalize the index. */
interface IndexedEntry {
    entry: SearchEntry;
    document: string;
    heading: string;
    body: string;
}

export interface SearchIndex {
    entries: IndexedEntry[];
    apiBase: string;
}

/** Raw shape of the JSON produced by scripts/build-search-index.ts. */
export interface SearchIndexFile {
    apiBase?: string;
    entries?: SearchEntry[];
}

/** A piece of snippet text, flagged when it matches a search term. */
export interface Segment {
    text: string;
    hit: boolean;
}

export interface SearchResult {
    type: EntryType;
    /** Document label (plugin name, guide folder, module path, site section). */
    document: string;
    /** Heading or symbol name. */
    heading: string;
    /** Destination, either an app route or an absolute URL when `external`. */
    url: string;
    external: boolean;
    snippet: Segment[];
    score: number;
}

const MAX_RESULTS = 40;
const MAX_PER_DOCUMENT = 3;
// Relevance alone would let the ~1000 API symbols fill the whole list for a word like
// `manual`; the cap keeps the best hit on top while leaving room for the other categories.
const MAX_PER_TYPE = 6;

// A section stops at the point where its hits become incidental mentions, rather than
// padding itself to MAX_PER_TYPE and pushing the next section off the screen.
const MIN_SCORE_RATIO = 0.4;
const SNIPPET_RADIUS = 70;

/** Results are grouped in this order; the chips follow it too. */
export const TYPE_ORDER: readonly EntryType[] = ['doc', 'api', 'plugin', 'site'];

/** Weights per field: a hit in a heading beats a hit buried in a paragraph. */
const WEIGHT_DOCUMENT = 8;
const WEIGHT_HEADING = 6;
const WEIGHT_BODY = 1;

// Naming the thing exactly outweighs any field placement: `resource` must land on the
// `Resource` class rather than on a page that only mentions resource packs.
const BONUS_EXACT_HEADING = 24;
const BONUS_EXACT_DOCUMENT = 10;

// A section that keeps coming back to the term is what the term is about. Counted raw
// rather than per character: density would favour a two-line section over a real one.
const WEIGHT_BODY_REPEAT = 1;
const MAX_BODY_REPEATS = 5;


// ── Normalization ─────────────────────────────────────────────────────────────

// Accent folding is done with a 1:1 character map (not NFD) so that normalized and
// raw strings keep the same length, letting snippets be sliced from the raw text.
const ACCENT_GROUPS: [string, string][] = [
    ['a', 'àáâãäåāăą'],
    ['c', 'çćĉċč'],
    ['e', 'èéêëēĕėęě'],
    ['i', 'ìíîïĩīĭįı'],
    ['n', 'ñńņň'],
    ['o', 'òóôõöøōŏőœ'],
    ['u', 'ùúûüũūŭůűų'],
    ['y', 'ýÿŷ'],
    ['z', 'žźż'],
];
const ACCENT_MAP: Record<string, string> = Object.fromEntries(
    ACCENT_GROUPS.flatMap(([plain, accents]) => [...accents].map((char) => [char, plain])),
);

/** Lowercase + accent-fold, preserving string length. */
export function normalize(text: string): string {
    return text.toLowerCase().replace(/[À-ſ]/g, (char) => ACCENT_MAP[char] ?? char);
}

// ── Index loading ─────────────────────────────────────────────────────────────

const cache = new Map<Language, Promise<SearchIndex>>();

function indexEntry(entry: SearchEntry): IndexedEntry {
    return {
        entry,
        document: normalize(entry.d),
        heading: normalize(entry.h),
        body: normalize(entry.b),
    };
}

/** Section ids on the home page, and routes for the other indexed site areas. */
const SITE_ROUTES: Record<string, string> = {
    hero: '/#hero',
    whatIs: '/#what-is',
    features: '/#features',
    installation: '/#installation',
    templates: '/#templates',
    showcase: '/#plugins',
    pluginsTable: '/documentation#plugins',
    documentation: '/documentation',
    tools: '/tools',
};

const SITE_LABELS: Record<string, string> = {
    hero: 'Home',
    whatIs: 'What is StewBeet',
    features: 'Features',
    installation: 'Installation',
    templates: 'Templates',
    showcase: 'Plugins',
    pluginsTable: 'Plugins',
    documentation: 'Documentation',
    tools: 'Tools',
};

/**
 * Turn the bundled translations into searchable entries for the static pages.
 * One entry per section: the individual keys are too fragmented to be useful rows.
 */
function buildSiteEntries(language: Language): SearchEntry[] {
    const groups = translations[language] as unknown as Record<string, Record<string, unknown>>;
    const entries: SearchEntry[] = [];

    for (const [group, route] of Object.entries(SITE_ROUTES)) {
        const values = Object.values(groups[group] ?? {}).filter((value) => typeof value === 'string');
        if (values.length === 0) continue;
        entries.push({ t: 'site', p: route, d: SITE_LABELS[group], h: '', a: '', b: values.join(' · ') });
    }
    return entries;
}

/** Merge the generated entries with the site sections and pre-normalize everything. */
export function createIndex(language: Language, data: SearchIndexFile): SearchIndex {
    return {
        apiBase: data.apiBase ?? '',
        entries: [...buildSiteEntries(language), ...(data.entries ?? [])].map(indexEntry),
    };
}

/** Fetch (once per language) the generated index and merge in the site sections. */
export function loadIndex(language: Language): Promise<SearchIndex> {
    const cached = cache.get(language);
    if (cached) return cached;

    const promise = fetch(`/search-index.${language}.json`)
        .then(async (response) => {
            if (!response.ok) throw new Error(`Failed to load search index (${response.status})`);
            return createIndex(language, await response.json());
        })
        .catch((error) => {
            cache.delete(language);
            throw error;
        });

    cache.set(language, promise);
    return promise;
}

// ── Scoring ───────────────────────────────────────────────────────────────────

// `_`, `-` and `.` count as boundaries so that snake_case and dotted module paths are
// matched segment by segment: `pack` is a whole word inside `resource_pack`.
const WORD_CHAR = /[a-z0-9]/;

/** Score one term against one already-normalized field. Whole word > prefix > substring. */
function scoreField(field: string, term: string, weight: number): number {
    const index = field.indexOf(term);
    if (index < 0) return 0;

    const startsWord = index === 0 || !WORD_CHAR.test(field[index - 1]);
    const endsWord = !WORD_CHAR.test(field[index + term.length] ?? ' ');

    if (startsWord && endsWord) return weight * 3;
    if (startsWord) return weight * 2;
    return weight;
}

/** Extra credit for a body that repeats the term, capped so long pages cannot run away with it. */
function scoreRepeats(body: string, term: string): number {
    let count = 0;
    let index = body.indexOf(term);
    while (index >= 0 && count <= MAX_BODY_REPEATS) {
        count++;
        index = body.indexOf(term, index + term.length);
    }
    return count > 1 ? Math.min(count - 1, MAX_BODY_REPEATS) * WEIGHT_BODY_REPEAT : 0;
}

/** Destination for a result, resolving Sphinx uris and markdown anchors. */
function resolveUrl(entry: SearchEntry, apiBase: string): { url: string; external: boolean } {
    if (entry.t === 'site') {
        return { url: entry.p, external: false };
    }
    if (entry.t === 'api') {
        const fullName = entry.d === entry.h ? entry.h : `${entry.d}.${entry.h}`;
        return { url: apiBase + entry.p.replace('$', fullName), external: true };
    }
    const anchor = entry.a ? `#${entry.a}` : '';
    return { url: `/markdown?src=${encodeURIComponent(entry.p)}${anchor}`, external: false };
}

/** Cut a readable excerpt around the first match and flag every term occurrence. */
function buildSnippet(entry: IndexedEntry, terms: string[]): Segment[] {
    const raw = entry.entry.b;
    if (!raw) return [];

    let start = 0;
    let first = -1;
    for (const term of terms) {
        const index = entry.body.indexOf(term);
        if (index >= 0 && (first < 0 || index < first)) first = index;
    }
    if (first > SNIPPET_RADIUS) {
        // Start on a word boundary when there is one nearby
        const space = raw.indexOf(' ', first - SNIPPET_RADIUS);
        start = space >= 0 && space < first ? space + 1 : first - SNIPPET_RADIUS;
    }

    const end = Math.min(raw.length, start + SNIPPET_RADIUS * 2);
    const text = (start > 0 ? '...' : '') + raw.slice(start, end).trim() + (end < raw.length ? '...' : '');
    const normalized = normalize(text);

    // Collect every term occurrence, then walk the excerpt turning them into segments
    const hits: [number, number][] = [];
    for (const term of terms) {
        let index = normalized.indexOf(term);
        while (index >= 0) {
            hits.push([index, index + term.length]);
            index = normalized.indexOf(term, index + term.length);
        }
    }
    hits.sort((a, b) => a[0] - b[0]);

    const segments: Segment[] = [];
    let cursor = 0;
    for (const [from, to] of hits) {
        if (from < cursor) continue;
        if (from > cursor) segments.push({ text: text.slice(cursor, from), hit: false });
        segments.push({ text: text.slice(from, to), hit: true });
        cursor = to;
    }
    if (cursor < text.length) segments.push({ text: text.slice(cursor), hit: false });
    return segments;
}

/**
 * Rank the index against a query. Every term must match somewhere in an entry, so
 * additional words narrow the results rather than widening them. Results come back
 * grouped by type following TYPE_ORDER, scored within each group.
 *
 * `types` restricts the search to the enabled categories.
 */
export function search(query: string, index: SearchIndex, types?: ReadonlySet<EntryType>): SearchResult[] {
    const normalized = normalize(query.trim());
    if (!normalized) return [];

    const terms = normalized.split(/\s+/).filter(Boolean);
    const scored: { entry: IndexedEntry; score: number }[] = [];

    for (const entry of index.entries) {
        if (types && !types.has(entry.entry.t)) continue;

        let total = 0;
        let matchesAll = true;

        for (const term of terms) {
            const best = Math.max(
                scoreField(entry.document, term, WEIGHT_DOCUMENT),
                scoreField(entry.heading, term, WEIGHT_HEADING),
                scoreField(entry.body, term, WEIGHT_BODY),
            );
            if (best === 0) {
                matchesAll = false;
                break;
            }
            total += best + scoreRepeats(entry.body, term);
        }
        if (!matchesAll) continue;

        // Reward the whole query appearing as one phrase
        if (terms.length > 1) {
            if (entry.heading.includes(normalized)) total += WEIGHT_HEADING * 3;
            else if (entry.body.includes(normalized)) total += WEIGHT_BODY * 3;
        }

        // The query naming the entry outright: the `Resource` class for `resource`
        if (entry.heading === normalized) total += BONUS_EXACT_HEADING;
        if (entry.document.slice(entry.document.lastIndexOf('.') + 1) === normalized) total += BONUS_EXACT_DOCUMENT;

        scored.push({ entry, score: total });
    }

    // Group first, score second: the sections are what the reader scans
    scored.sort((a, b) =>
        TYPE_ORDER.indexOf(a.entry.entry.t) - TYPE_ORDER.indexOf(b.entry.entry.t) || b.score - a.score,
    );

    const results: SearchResult[] = [];
    const perDocument = new Map<string, number>();
    const perType = new Map<EntryType, number>();
    const bestByType = new Map<EntryType, number>();

    for (const { entry, score } of scored) {
        const type = entry.entry.t;
        const typeCount = perType.get(type) ?? 0;
        if (typeCount >= MAX_PER_TYPE) continue;

        // Entries are grouped then sorted, so the first of a type is that section's best
        const best = bestByType.get(type) ?? score;
        if (score < best * MIN_SCORE_RATIO) continue;
        bestByType.set(type, best);

        const key = `${type}:${entry.entry.d}`;
        const count = perDocument.get(key) ?? 0;
        if (count >= MAX_PER_DOCUMENT) continue;
        perDocument.set(key, count + 1);
        perType.set(type, typeCount + 1);

        results.push({
            type: entry.entry.t,
            document: entry.entry.d,
            heading: entry.entry.h,
            ...resolveUrl(entry.entry, index.apiBase),
            snippet: buildSnippet(entry, terms),
            score,
        });
        if (results.length >= MAX_RESULTS) break;
    }
    return results;
}
