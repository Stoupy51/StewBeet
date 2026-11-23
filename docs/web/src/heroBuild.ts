import type { FileNode } from './components/FileTree';
import heroOutput from './generated/heroOutput.json';

function leaves(nodes: FileNode[]): FileNode[] {
    return nodes.flatMap((node) => node.children ? leaves(node.children) : [node]);
}

/** The files the build wrote from the hero's block definition, as python_package/scripts/build_hero_output.py recorded them, each with its `path`. */
export const BLOCK_FILES = leaves(heroOutput.tree as FileNode[]).filter((leaf) => leaf.snippet === 'block');
