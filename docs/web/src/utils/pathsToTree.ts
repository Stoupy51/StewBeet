/**
 * Turn a flat list of built file paths into the nested shape FileTree renders.
 *
 * The hero's tree is hand-curated, because a real path is three times too long to read in half a
 * hero panel. Nothing to curate here: the playground shows whatever the visitor's code produced, so
 * the tree is derived from the paths themselves and every leaf carries its real one.
 */
import type { FileNode } from '../components/FileTree';

export interface BuiltFile {
    path: string;
    kind?: 'text' | 'image' | 'skipped';
    bytes?: number;
    lines?: number;
}

/**
 * Build the nested tree, directories first and alphabetical within each level.
 *
 * Directories are returned open. A collapsed tree would hide the point of the page, which is that
 * one short definition turns into a lot of files.
 *
 * @param files Flat list from the worker, in any order.
 *
 * @example
 * buildTree([{ path: 'datapack/pack.mcmeta' }]).length === 1
 */
export function buildTree(files: BuiltFile[]): FileNode[] {
    const roots: FileNode[] = [];
    // Every directory already created, keyed by its full path, so a second file in the same folder
    // finds it instead of making a duplicate row.
    const directories = new Map<string, FileNode>();

    for (const file of [...files].sort((a, b) => a.path.localeCompare(b.path))) {
        const segments = file.path.split('/');
        let siblings = roots;
        let prefix = '';

        for (const segment of segments.slice(0, -1)) {
            prefix = prefix === '' ? segment : `${prefix}/${segment}`;
            let directory = directories.get(prefix);
            if (!directory) {
                directory = { name: segment, children: [], open: true };
                directories.set(prefix, directory);
                siblings.push(directory);
            }
            siblings = directory.children ?? [];
        }

        siblings.push({
            name: segments[segments.length - 1],
            path: file.path,
            // A file over the per-file cap has no body to show, so it stays an unselectable row.
            kind: file.kind === 'image' || file.kind === 'text' ? file.kind : undefined,
            bytes: file.bytes,
            lines: file.lines,
        });
    }

    sort(roots);
    return roots;
}

/** Directories above files, then alphabetical, at every level. */
function sort(nodes: FileNode[]): void {
    nodes.sort((a, b) => {
        const aIsDirectory = a.children !== undefined;
        const bIsDirectory = b.children !== undefined;
        if (aIsDirectory !== bIsDirectory) return aIsDirectory ? -1 : 1;
        return a.name.localeCompare(b.name);
    });
    for (const node of nodes) {
        if (node.children) sort(node.children);
    }
}
