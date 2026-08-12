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
}

/** Colour per file extension, so a tree reads as datapack / resource pack / function at a glance. */
const EXTENSION_COLORS: Record<string, string> = {
    json: 'text-mc-diamond',
    png: 'text-emerald-300',
    mcfunction: 'text-amber-300',
    py: 'text-sky-300',
};

function fileColor(name: string): string {
    const extension = name.slice(name.lastIndexOf('.') + 1);
    return EXTENSION_COLORS[extension] ?? 'text-slate-300';
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

interface TreeRowProps {
    node: FileNode;
    depth: number;
    order: number;
    selected?: string;
    onSelect?: (node: FileNode) => void;
}

const TreeRow = ({ node, depth, order, selected, onSelect }: TreeRowProps) => {
    const isDirectory = node.children !== undefined;
    const [open, setOpen] = useState(node.open !== false);
    const childOffsets = rowOffsets(node.children ?? [], order + 1);
    const isSelectable = !isDirectory && node.path !== undefined && onSelect !== undefined;

    return (
        <>
            <div
                className="intro-row flex items-baseline gap-2 leading-[1.55] whitespace-nowrap"
                style={{ paddingLeft: `${depth * 0.9}rem`, '--row': order } as React.CSSProperties}
            >
                {isDirectory ? (
                    <button
                        onClick={() => setOpen(!open)}
                        className="flex items-baseline gap-1 text-slate-400 hover:text-white transition-colors"
                    >
                        <span className="translate-y-0.5">{open ? <HiChevronDown /> : <HiChevronRight />}</span>
                        <span className="font-medium">{node.name}</span>
                    </button>
                ) : (
                    <>
                        <span className="text-slate-700 select-none">└</span>
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
                {node.note && <span className="text-slate-400 text-[0.6875rem] truncate">{node.note}</span>}
            </div>

            {isDirectory && open && node.children?.map((child, index) => (
                <TreeRow
                    key={child.name}
                    node={child}
                    depth={depth + 1}
                    order={childOffsets[index]}
                    selected={selected}
                    onSelect={onSelect}
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
}

/** Same 12px/1.55 as the hero code panel: the tree and the snippet read as one pair, not two widgets. */
export const FileTree: React.FC<FileTreeProps> = ({ nodes, selected, onSelect }) => {
    const offsets = rowOffsets(nodes, 0);
    return (
        <div className="font-mono text-xs">
            {nodes.map((node, index) => (
                <TreeRow
                    key={node.name}
                    node={node}
                    depth={0}
                    order={offsets[index]}
                    selected={selected}
                    onSelect={onSelect}
                />
            ))}
        </div>
    );
};
