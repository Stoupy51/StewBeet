import { useState } from 'react';
import { motion } from 'framer-motion';
import { HiChevronDown, HiChevronRight } from 'react-icons/hi';

export interface FileNode {
    name: string;
    /** Present on directories, even when empty. */
    children?: FileNode[];
    /** Short muted note shown to the right, e.g. what the file is for. */
    note?: string;
    /** Directories start collapsed when false. */
    open?: boolean;
}

/** Colour per file extension, so a tree reads as datapack / resource pack / function at a glance. */
const EXTENSION_COLORS: Record<string, string> = {
    json: 'text-indigo-300',
    png: 'text-emerald-300',
    mcfunction: 'text-amber-300',
    py: 'text-sky-300',
};

function fileColor(name: string): string {
    const extension = name.slice(name.lastIndexOf('.') + 1);
    return EXTENSION_COLORS[extension] ?? 'text-slate-300';
}

/** Cascade the reveal by nesting level and position, without threading a counter through the tree. */
function revealDelay(depth: number, index: number): number {
    return Math.min((depth * 2 + index) * 0.05, 0.7);
}

const TreeRow = ({ node, depth, index }: { node: FileNode; depth: number; index: number }) => {
    const isDirectory = node.children !== undefined;
    const [open, setOpen] = useState(node.open !== false);

    return (
        <>
            <motion.div
                initial={{ opacity: 0, x: -6 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.25, delay: revealDelay(depth, index) }}
                className="flex items-baseline gap-2 leading-[1.7] whitespace-nowrap"
                style={{ paddingLeft: `${depth * 0.9}rem` }}
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
                        <span className={fileColor(node.name)}>{node.name}</span>
                    </>
                )}
                {node.note && <span className="text-slate-600 text-[0.6875rem] truncate">{node.note}</span>}
            </motion.div>

            {isDirectory && open && node.children?.map((child, childIndex) => (
                <TreeRow key={child.name} node={child} depth={depth + 1} index={childIndex} />
            ))}
        </>
    );
};

/** Same 12px/1.7 as the hero code panel: the tree and the snippet read as one pair, not two widgets. */
export const FileTree: React.FC<{ nodes: FileNode[] }> = ({ nodes }) => (
    <div className="font-mono text-xs">
        {nodes.map((node, index) => (
            <TreeRow key={node.name} node={node} depth={0} index={index} />
        ))}
    </div>
);
