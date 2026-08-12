import { useEffect, useRef } from 'react';
import { EditorState, type Extension } from '@codemirror/state';
import { EditorView, keymap, lineNumbers, highlightActiveLine, highlightActiveLineGutter } from '@codemirror/view';
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands';
import { python } from '@codemirror/lang-python';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags } from '@lezer/highlight';

/**
 * The playground's Python editor.
 *
 * Only ever reached from the /playground route, which is lazy, so CodeMirror stays out of every
 * other page's bundle. Monaco would have been five megabytes for the same job.
 *
 * Colours are hand-mapped to dark-plus rather than pulled from a CodeMirror theme package, so the
 * editor matches the Shiki output the rest of the site already renders. Two highlighters that
 * disagree about what a string looks like is worse than either one alone.
 */

const DARK_PLUS = HighlightStyle.define([
    { tag: tags.keyword, color: '#c586c0' },
    { tag: tags.controlKeyword, color: '#c586c0' },
    { tag: tags.definitionKeyword, color: '#569cd6' },
    { tag: tags.moduleKeyword, color: '#c586c0' },
    { tag: tags.string, color: '#ce9178' },
    { tag: tags.number, color: '#b5cea8' },
    { tag: tags.bool, color: '#569cd6' },
    { tag: tags.null, color: '#569cd6' },
    { tag: tags.comment, color: '#6a9955', fontStyle: 'italic' },
    { tag: tags.function(tags.variableName), color: '#dcdcaa' },
    { tag: tags.definition(tags.variableName), color: '#9cdcfe' },
    { tag: tags.variableName, color: '#9cdcfe' },
    { tag: tags.propertyName, color: '#9cdcfe' },
    { tag: tags.className, color: '#4ec9b0' },
    { tag: tags.typeName, color: '#4ec9b0' },
    { tag: tags.operator, color: '#d4d4d4' },
    { tag: tags.punctuation, color: '#d4d4d4' },
]);

const THEME = EditorView.theme({
    '&': { backgroundColor: 'transparent', color: '#d4d4d4', height: '100%' },
    '.cm-content': { fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace', fontSize: '0.8125rem', padding: '0.75rem 0' },
    '.cm-gutters': { backgroundColor: 'transparent', color: '#4b5563', border: 'none' },
    '.cm-activeLine': { backgroundColor: 'rgba(148, 163, 184, 0.06)' },
    '.cm-activeLineGutter': { backgroundColor: 'transparent', color: '#94a3b8' },
    '.cm-cursor': { borderLeftColor: '#d4d4d4' },
    '.cm-scroller': { overflow: 'auto' },
    '&.cm-focused': { outline: 'none' },
    '.cm-selectionBackground, &.cm-focused .cm-selectionBackground, ::selection': { backgroundColor: 'rgba(56, 189, 248, 0.25)' },
}, { dark: true });

interface CodeEditorProps {
    value: string;
    onChange: (value: string) => void;
    /** Fired on Ctrl/Cmd+Enter, the shortcut the page advertises for Build. */
    onSubmit: () => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ value, onChange, onSubmit }) => {
    const host = useRef<HTMLDivElement>(null);
    const view = useRef<EditorView | null>(null);

    // Kept in refs so the extensions below can close over the latest callbacks without the editor
    // being torn down and rebuilt every time the page re-renders, which would drop the cursor.
    const latestChange = useRef(onChange);
    const latestSubmit = useRef(onSubmit);
    latestChange.current = onChange;
    latestSubmit.current = onSubmit;

    useEffect(() => {
        if (!host.current) return;

        const extensions: Extension[] = [
            lineNumbers(),
            highlightActiveLine(),
            highlightActiveLineGutter(),
            history(),
            python(),
            syntaxHighlighting(DARK_PLUS),
            THEME,
            EditorView.lineWrapping,
            keymap.of([
                {
                    key: 'Mod-Enter',
                    run: () => {
                        latestSubmit.current();
                        return true;
                    },
                },
                // Before defaultKeymap so Tab indents instead of moving focus. That traps keyboard
                // users, so Escape then Tab still leaves: indentWithTab keeps that escape hatch.
                indentWithTab,
                ...defaultKeymap,
                ...historyKeymap,
            ]),
            EditorView.updateListener.of(update => {
                if (update.docChanged) latestChange.current(update.state.doc.toString());
            }),
        ];

        const editor = new EditorView({
            state: EditorState.create({ doc: value, extensions }),
            parent: host.current,
        });
        view.current = editor;
        return () => {
            editor.destroy();
            view.current = null;
        };
        // Built once. `value` is read for the initial document only; syncing it here would fight
        // the user's typing, and the effect below handles the cases where it changes from outside.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Only for changes that did not come from typing, like picking a preset.
    useEffect(() => {
        const editor = view.current;
        if (!editor || editor.state.doc.toString() === value) return;
        editor.dispatch({ changes: { from: 0, to: editor.state.doc.length, insert: value } });
    }, [value]);

    return <div ref={host} className="h-full overflow-hidden" />;
};
