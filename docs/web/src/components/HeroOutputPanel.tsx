import { useCallback, useState } from 'react';
import { HiArrowLeft } from 'react-icons/hi';
import { FileTree, type FileNode } from './FileTree';
import { useTranslation } from '../i18n/useTranslation';
import { useOverflowFade } from '../hooks/useOverflowFade';
import { formatBytes } from '../utils/fileDisplay';

/**
 * The hero's output panel: the generated file tree, and the real content of whichever file the
 * reader clicks.
 *
 * The tree shows shortened labels because the real paths are three times too long for half a hero
 * panel, so the file view leads with the real path: the shortening is a display choice and a
 * reader who wants to check should be able to.
 *
 * The two views swap rather than stack. The hero is meant to fit one screen, and a content pane
 * appended below the tree would push the fold down on exactly the visitors who engaged with it.
 *
 * Bodies live in src/generated/heroContentsHtml.json, already highlighted by prehighlight.ts, and
 * are fetched on the first click. Importing them statically would put every generated file in the
 * landing page bundle, and highlighting them in the browser would pull in a highlighter: the two
 * costs scripts/prehighlight.ts exists to avoid.
 */

type Contents = Record<string, string>;

/** Checkerboard behind transparent PNGs, drawn with a gradient so it costs no request. */
const CHECKERBOARD =
    'bg-[linear-gradient(45deg,#24211e_25%,transparent_25%),linear-gradient(-45deg,#24211e_25%,transparent_25%),linear-gradient(45deg,transparent_75%,#24211e_75%),linear-gradient(-45deg,transparent_75%,#24211e_75%)] bg-[length:16px_16px] bg-[position:0_0,0_8px,8px_-8px,-8px_0]';

/** `active` is the code tab on show; files the other snippets produce are dimmed. */
export const HeroOutputPanel: React.FC<{ nodes: FileNode[]; active: string }> = ({ nodes, active }) => {
    const { t } = useTranslation();
    const [selected, setSelected] = useState<FileNode | null>(null);
    const [contents, setContents] = useState<Contents | null>(null);
    const [failed, setFailed] = useState(false);
    const treeScroll = useOverflowFade();

    const openFile = useCallback(async (node: FileNode) => {
        setSelected(node);
        if (node.kind !== 'text' || contents) return;
        try {
            const module = await import('../generated/heroContentsHtml.json');
            setContents(module.default as Contents);
        } catch {
            setFailed(true);
        }
    }, [contents]);

    if (!selected) {
        return (
            <div ref={treeScroll} className="flex-1 min-h-0 flex flex-col p-4 overflow-auto custom-scrollbar">
                <FileTree nodes={nodes} onSelect={openFile} active={active} />
                <p className="mt-4 pt-3 border-t border-ink-800 text-xs text-ink-400 leading-relaxed">
                    {t('hero.outputNote')}
                </p>
            </div>
        );
    }

    const body = selected.kind === 'text' ? contents?.[selected.path ?? ''] : undefined;

    return (
        <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center gap-2 px-4 py-2 border-b border-ink-800 shrink-0">
                <button
                    onClick={() => setSelected(null)}
                    className="flex items-center gap-1 text-xs text-ink-400 hover:text-ink-50 transition-colors shrink-0"
                >
                    <HiArrowLeft aria-hidden="true" />
                    {t('hero.outputBack')}
                </button>
                <span className="text-ink-600 select-none" aria-hidden="true">|</span>
                <span className="font-mono text-[0.6875rem] text-ink-400 truncate" title={selected.path}>
                    <span className="text-ink-500">{t('hero.outputRealPath')}</span> build/{selected.path}
                </span>
                {selected.bytes !== undefined && (
                    <span className="ml-auto font-mono text-[0.6875rem] text-ink-500 shrink-0 tabular-nums">
                        {formatBytes(selected.bytes)}
                    </span>
                )}
            </div>

            <div className="flex-1 p-4 overflow-auto custom-scrollbar">
                {selected.kind === 'image' ? (
                    <div className={`inline-block p-3 rounded ${CHECKERBOARD}`}>
                        <img
                            src={selected.url}
                            alt={selected.name}
                            className="max-w-full [image-rendering:pixelated]"
                        />
                    </div>
                ) : failed ? (
                    <p className="text-xs text-ink-400">{t('hero.outputUnavailable')}</p>
                ) : body === undefined ? (
                    <p className="text-xs text-ink-500 animate-pulse">{t('hero.outputLoading')}</p>
                ) : (
                    /* Markup comes from scripts/prehighlight.ts, same as the snippet panel, so no
                       highlighter is ever loaded on the landing page. */
                    <div
                        dangerouslySetInnerHTML={{ __html: body }}
                        style={{ fontSize: '0.75rem', lineHeight: '1.55' }}
                        className="font-mono [&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-0"
                    />
                )}
            </div>
        </div>
    );
};
