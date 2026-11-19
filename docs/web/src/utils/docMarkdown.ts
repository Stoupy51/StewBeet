/**
 * Unified plugins that turn a documentation page into the reader's layout. They run after
 * rehype-sanitize, so the classes and attributes they write are kept.
 *
 * - Numbered steps: an `## 1. Install uv` heading and what follows it, up to the next H2, become one
 *   step with a framed "01".
 * - Code tabs: consecutive fenced blocks that each carry `tab="..."` become one panel with tabs.
 * - Table labels: each cell carries its column name, so a phone can show a row as a block.
 */
import type { Element, ElementContent, Root, RootContent } from 'hast';
import type { Nodes as MdastNodes, Root as MdastRoot } from 'mdast';
import { slugify } from './slugify';

const STEP_HEADING = /^(\d+)\.\s+/;
/** Code this narrow fits the 26rem panel beside the text without wrapping, a tab counting 4. */
const SPLIT_MAX_COLUMNS = 52;
/** A block this short is a command or two, which can wrap in the panel without becoming hard to read. */
const SPLIT_MAX_LINES = 3;
/** Past this, the text column beside the code turns into a long narrow strip. */
const SPLIT_MAX_WORDS = 70;

export function textOf(node: Root | RootContent | ElementContent): string {
    if (node.type === 'text') return node.value;
    if ('children' in node) return node.children.map(textOf).join('');
    return '';
}

const isElement = (node: RootContent | ElementContent, tagName?: string): node is Element =>
    node.type === 'element' && (tagName === undefined || node.tagName === tagName);

const isBlank = (node: RootContent | ElementContent) => node.type === 'text' && !node.value.trim();

/** The `title="..."` or `tab="..."` written after the language of a fence. */
export function metaValue(meta: string | undefined, key: string): string | undefined {
    return meta?.match(new RegExp(`${key}="([^"]*)"`))?.[1];
}

/** Keeps the text after a fence's language, which rehype-raw would otherwise drop. */
export function remarkCodeMeta() {
    const visit = (node: MdastNodes): void => {
        if (node.type === 'code' && node.meta) {
            node.data = { ...node.data, hProperties: { ...node.data?.hProperties, dataMeta: node.meta } };
        }
        if ('children' in node) node.children.forEach(visit);
    };
    return (tree: MdastRoot) => visit(tree);
}

const codeOf = (pre: Element) => pre.children.find((child): child is Element => isElement(child, 'code'));

const tabLabel = (node: RootContent) =>
    isElement(node, 'pre') ? metaValue(codeOf(node)?.properties.dataMeta as string | undefined, 'tab') : undefined;

export function rehypeCodeTabs() {
    return (tree: Root) => {
        const children: RootContent[] = [];
        let group: Element | null = null;
        for (const node of tree.children) {
            if (isBlank(node)) {
                children.push(node);
                continue;
            }
            if (tabLabel(node) === undefined) {
                group = null;
                children.push(node);
                continue;
            }
            if (!group) {
                group = { type: 'element', tagName: 'div', properties: { dataTabs: '' }, children: [] };
                children.push(group);
            }
            group.children.push(node as Element);
        }
        tree.children = children;
    };
}

/** Whether a step reads well with its code beside its text: little text, and code that is short or narrow. */
function fitsSideBySide(text: RootContent[], code: RootContent[]): boolean {
    const words = text.map(textOf).join(' ').split(/\s+/).filter(Boolean).length;
    const blocks = code.map((node) => textOf(node).replace(/\n$/, '').split('\n'));
    const short = blocks.every((lines) => lines.length <= SPLIT_MAX_LINES);
    const narrow = blocks.flat().every((line) => line.replace(/\t/g, '    ').length <= SPLIT_MAX_COLUMNS);
    return words <= SPLIT_MAX_WORDS && (short || narrow);
}

function buildStep(heading: Element, body: RootContent[]): { step: Element; fits: boolean } {
    const label = textOf(heading);
    const number = label.match(STEP_HEADING)?.[1] ?? '';
    // The id comes from the full heading, as the contents list and the search index write it
    const titled: Element = {
        ...heading,
        properties: { ...heading.properties, id: slugify(label) },
        children: heading.children.map((child) => child.type === 'text' ? { ...child, value: child.value.replace(STEP_HEADING, '') } : child),
    };

    const content = body.filter((node) => !isBlank(node));
    const isCode = (node: RootContent) => node.type === 'element' && (node.tagName === 'pre' || (node.tagName === 'div' && node.properties.dataTabs !== undefined));
    const ordered = (node: RootContent, index: number) => isElement(node) ? { ...node, properties: { ...node.properties, style: `order:${index}` } } : node;
    const items = [titled, ...content].map(ordered) as ElementContent[];
    const text = items.filter((node) => !isCode(node as RootContent));
    const code = items.filter((node) => isCode(node as RootContent));

    const step: Element = {
        type: 'element',
        tagName: 'section',
        properties: { className: ['md-step'] },
        children: [
            { type: 'element', tagName: 'span', properties: { className: ['md-step-marker'], ariaHidden: 'true' }, children: [{ type: 'text', value: number.padStart(2, '0') }] },
            {
                type: 'element',
                tagName: 'div',
                properties: { className: ['md-step-body'] },
                children: [
                    { type: 'element', tagName: 'div', properties: { className: ['md-step-text'] }, children: text },
                    { type: 'element', tagName: 'div', properties: { className: ['md-step-code'] }, children: code },
                ],
            },
        ],
    };
    return { step, fits: fitsSideBySide(text as RootContent[], code as RootContent[]) };
}

/** Every step of a page takes the same layout: beside its code when they all fit, stacked otherwise. */
export function rehypeSteps() {
    return (tree: Root) => {
        const children: RootContent[] = [];
        const built: { step: Element; fits: boolean }[] = [];
        let open: { heading: Element; body: RootContent[] } | null = null;
        const close = () => {
            if (!open) return;
            const result = buildStep(open.heading, open.body);
            built.push(result);
            children.push(result.step);
            open = null;
        };

        for (const node of tree.children) {
            if (isElement(node, 'h1') || isElement(node, 'h2')) close();
            if (isElement(node, 'h2') && STEP_HEADING.test(textOf(node))) {
                open = { heading: node, body: [] };
                continue;
            }
            if (open) open.body.push(node);
            else children.push(node);
        }
        close();

        const layout = built.every(({ fits }) => fits) ? 'split' : 'stack';
        built.forEach(({ step }) => step.properties.dataLayout = layout);
        tree.children = children;
    };
}

export function rehypeTableLabels() {
    const visit = (node: Root | RootContent) => {
        if (node.type === 'element' && node.tagName === 'table') {
            const rows = node.children.flatMap((part) => isElement(part) ? part.children.filter((row): row is Element => isElement(row, 'tr')) : []);
            const labels = rows[0]?.children.filter((cell): cell is Element => isElement(cell, 'th')).map(textOf) ?? [];
            for (const row of rows.slice(1)) {
                row.children.filter((cell): cell is Element => isElement(cell, 'td')).forEach((cell, index) => {
                    if (labels[index]) cell.properties.dataLabel = labels[index];
                });
            }
            return;
        }
        if ('children' in node) node.children.forEach(visit);
    };
    return (tree: Root) => visit(tree);
}
