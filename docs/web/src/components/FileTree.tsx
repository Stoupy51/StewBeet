import { useState } from 'react';
import { HiChevronDown, HiChevronRight } from 'react-icons/hi';

export interface FileNode {
    name: string;
    /** Present on directories, even when empty. */
    children?: FileNode[];
    /** Short muted note shown to the right, e.g. what the file is for. */
    note?: string;
    /** Directories start collapsed when false. */
    open?: boolean;
    /**
     * Path of the real generated file this row stands for, relative to `build/`.
     * `name` is the shortened label the panel can fit; this is where the bytes actually live.
     * A leaf that has one becomes selectable when the tree is given an `onSelect`.
     */
    path?: string;
    /** Whether the real file is text or an image. Set by build_hero_output.py. */
    kind?: 'text' | 'image';
    /** Size of the real file in bytes. */
    bytes?: number;
    /** Line count, for text files only. */
    lines?: number;
    /** Public URL of the real file, for images only. */
    url?: string;
    /** Id of the hero code tab whose snippet produces this file, e.g. 'block'. */
    snippet?: string;
}

/** Colour per file extension, so a tree reads as datapack / resource pack / function at a glance. */
const EXTENSION_COLORS: Record<string, string> = {
    json: 'text-sky-300',
    png: 'text-leaf-400',
    mcfunction: 'text-mc-gold',
    py: 'text-beet-300',
};

function fileColor(name: string): string {
    const extension = name.slice(name.lastIndexOf('.') + 1);
    return EXTENSION_COLORS[extension] ?? 'text-ink-300';
}

/**
 * Rows carry their position in document order as `--row`, which the entrance animation turns
 * into a delay so files land top to bottom. A per-parent index would restart the count inside
 * every directory and the stream would arrive out of order, so the number is threaded through
 * the recursion: each child starts after everything its previous siblings expand to.
 */
function visibleRowCount(node: FileNode): number {
    const expanded = node.children !== undefined && node.open !== false;
    if (!expanded) return 1;
    return 1 + (node.children ?? []).reduce((total, child) => total + visibleRowCount(child), 0);
}

/**
 * How long the cascade may span, however many rows the tree has.
 * A pack with two hundred functions streamed for eight seconds at full pace; with the 320ms row
 * fade on top of this, a tree of any size has landed inside a second.
 */
const REVEAL_BUDGET_MS: number = 600;

/** Delay between two rows, matching index.css, for a tree small enough to fit the budget at full pace. */
const REVEAL_STEP_MS: number = 42;

/** Positions each node at its place in the flattened, document-order sequence. */
function rowOffsets(nodes: FileNode[], from: number): number[] {
    const offsets: number[] = [];
    let running = from;
    for (const node of nodes) {
        offsets.push(running);
        running += visibleRowCount(node);
    }
    return offsets;
}

/** Whether a row belongs to the active snippet: a file by its tag, a directory by any file below it. */
function fromSnippet(node: FileNode, active: string): boolean {
    if (node.children) return node.children.some((child) => fromSnippet(child, active));
    return node.snippet === undefined || node.snippet === active;
}

interface TreeRowProps {
    node: FileNode;
    depth: number;
    order: number;
    selected?: string;
    onSelect?: (node: FileNode) => void;
    active?: string;
}

const TreeRow = ({ node, depth, order, selected, onSelect, active }: TreeRowProps) => {
    const isDirectory = node.children !== undefined;
    const [open, setOpen] = useState(node.open !== false);
    const childOffsets = rowOffsets(node.children ?? [], order + 1);
    const isSelectable = !isDirectory && node.path !== undefined && onSelect !== undefined;
    const dimmed = active !== undefined && !fromSnippet(node, active);

    return (
        <>
            {/* The row's entrance animation holds its opacity, so the dimming sits on an inner wrapper. */}
            <div
                className="intro-row leading-[1.55] whitespace-nowrap"
                style={{ paddingLeft: `${depth * 0.9}rem`, '--row': order } as React.CSSProperties}
            >
                <div className={`flex items-baseline gap-2 transition-opacity duration-200 ${dimmed ? 'opacity-30' : ''}`}>
                    {isDirectory ? (
                        <button
                            onClick={() => setOpen(!open)}
                            className="flex items-baseline gap-1 text-ink-300 hover:text-ink-50 transition-colors"
                        >
                            <span className="translate-y-0.5">{open ? <HiChevronDown /> : <HiChevronRight />}</span>
                            <span className="font-medium">{node.name}</span>
                        </button>
                    ) : (
                        <>
                            <span className="text-ink-600 select-none">└</span>
                            {isSelectable ? (
                                <button
                                    onClick={() => onSelect(node)}
                                    aria-current={node.path === selected ? 'true' : undefined}
                                    className={`${fileColor(node.name)} hover:underline underline-offset-2 decoration-dotted transition-colors ${
                                        node.path === selected ? 'underline decoration-solid' : ''
                                    }`}
                                >
                                    {node.name}
                                </button>
                            ) : (
                                <span className={fileColor(node.name)}>{node.name}</span>
                            )}
                        </>
                    )}
                    {node.note && <span className="text-ink-400 text-[0.6875rem] truncate">{node.note}</span>}
                </div>
            </div>

            {isDirectory && open && node.children?.map((child, index) => (
                <TreeRow
                    key={child.name}
                    node={child}
                    depth={depth + 1}
                    order={childOffsets[index]}
                    selected={selected}
                    onSelect={onSelect}
                    active={active}
                />
            ))}
        </>
    );
};

interface FileTreeProps {
    nodes: FileNode[];
    /** `path` of the row to mark as current. */
    selected?: string;
    /** Omit to render a plain, non-interactive tree, which is what Features.tsx wants. */
    onSelect?: (node: FileNode) => void;
    /**
     * Cascade the rows in as soon as this tree renders, for a tree that appears on a click.
     * Prerendered trees leave it off and let the `[data-intro='play']` gate decide, so a returning
     * visitor is not shown an entrance the server already painted as finished.
     */
    reveal?: boolean;
    /** Id of the hero code tab on show: files another snippet produces are dimmed, not hidden. */
    active?: string;
}

/** Same 12px/1.55 as the hero code panel: the tree and the snippet read as one pair, not two widgets. */
export const FileTree: React.FC<FileTreeProps> = ({ nodes, selected, onSelect, reveal, active }) => {
    const offsets = rowOffsets(nodes, 0);
    const rows = nodes.reduce((total, node) => total + visibleRowCount(node), 0);
    const step = Math.min(REVEAL_STEP_MS, REVEAL_BUDGET_MS / Math.max(rows, 1));
    return (
        <div
            className="font-mono text-xs"
            data-reveal={reveal ? '' : undefined}
            style={reveal ? ({ '--row-step': `${step}ms` } as React.CSSProperties) : undefined}
        >
            {nodes.map((node, index) => (
                <TreeRow
                    key={node.name}
                    node={node}
                    depth={0}
                    order={offsets[index]}
                    selected={selected}
                    onSelect={onSelect}
                    active={active}
                />
            ))}
        </div>
    );
};
