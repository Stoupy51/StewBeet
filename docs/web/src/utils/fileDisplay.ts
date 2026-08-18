/**
 * How a generated file is labelled and coloured, shared by every panel that shows one.
 *
 * Its own module rather than exports beside SourceView, because a file that exports both a component
 * and plain functions loses fast refresh for the component.
 */

const BYTES_IN_KB = 1024;

/**
 * Size in the largest unit that still reads as a number rather than as a long decimal.
 *
 * @example
 * formatBytes(900) === '900 B'
 * formatBytes(2048) === '2.0 KB'
 */
export function formatBytes(bytes: number): string {
    if (bytes < BYTES_IN_KB) return `${bytes} B`;
    if (bytes < BYTES_IN_KB ** 2) return `${(bytes / BYTES_IN_KB).toFixed(1)} KB`;
    return `${(bytes / BYTES_IN_KB ** 2).toFixed(1)} MB`;
}

/** Same grammars the rest of the site uses, so a .mcfunction is coloured identically everywhere. */
export function languageOf(path: string): string {
    if (path.endsWith('.mcfunction')) return 'mcfunction';
    if (path.endsWith('.json') || path.endsWith('.mcmeta')) return 'json';
    if (path.endsWith('.py')) return 'python';
    if (path.endsWith('.yml') || path.endsWith('.yaml')) return 'yaml';
    return 'text';
}
