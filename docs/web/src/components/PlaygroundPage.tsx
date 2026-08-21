import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { HiPlay } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { FileTree, type FileNode } from './FileTree';
import { SourceView } from './SourceView';
import { useTranslation } from '../i18n/useTranslation';
import { buildTree, type BuiltFile } from '../utils/pathsToTree';
import { formatBytes, languageOf } from '../utils/fileDisplay';
import { MAX_CODE_BYTES, SANDBOX_LIMITS, WARN_CODE_BYTES } from '../api/sandboxLimits';
import { DEFAULT_CODE, PRESETS } from './playgroundPresets';
import { HEADING, TEXT_ACCENT } from '../theme';

/**
 * /playground: edit a definitions module, see the files StewBeet generates from it.
 *
 * The build happens in a separate container with no route off its network, because StewBeet runs
 * submitted Python by design. Nothing on this page is a security boundary; it only decides what to
 * send and how to show what comes back.
 *
 * The editor is lazy inside a route that is already lazy, so CodeMirror is fetched when someone
 * actually opens the page rather than on the first paint of the site.
 */

const CodeEditor = lazy(() => import('./CodeEditor').then(m => ({ default: m.CodeEditor })));

interface BuildResult {
    ok: boolean;
    cached?: boolean;
    durationMs?: number;
    files?: BuiltFile[];
    text?: Record<string, string>;
    images?: Record<string, string>;
    truncated?: { files: boolean; bytes: boolean };
    logs?: string;
    /** The beet.yml the build actually ran with, returned by the sandbox rather than copied here. */
    config?: string;
    error?: string;
    /** Where a build failure says what went wrong. Far more useful than the log on its own. */
    traceback?: string;
    /** Root cause, already unwrapped from beet's PluginError and stouputils' exit path. */
    message?: string;
    /** Line of the submitted code that failed. Numbering matches the editor exactly. */
    line?: number;
    source?: string;
    /** Close names, when the failure was a NameError. */
    suggestions?: string[];
    retryAfterMs?: number;
}

export const PlaygroundPage: React.FC = () => {
    const { t } = useTranslation();
    const [code, setCode] = useState(DEFAULT_CODE);
    const [result, setResult] = useState<BuildResult | null>(null);
    const [pending, setPending] = useState(false);
    const [selected, setSelected] = useState<FileNode | null>(null);
    const [active, setActive] = useState(PRESETS[0].id);
    const [showConfig, setShowConfig] = useState(false);
    const inFlight = useRef<AbortController | null>(null);

    // A build in flight when the reader navigates away has nowhere to land, and its response would
    // set state on an unmounted tree.
    useEffect(() => () => inFlight.current?.abort(), []);

    const size = useMemo(() => new TextEncoder().encode(code).length, [code]);
    const tooLarge = size > MAX_CODE_BYTES;

    const build = useCallback(async () => {
        if (tooLarge) return;
        inFlight.current?.abort();
        const controller = new AbortController();
        inFlight.current = controller;

        setPending(true);
        setSelected(null);
        setShowConfig(false);
        try {
            const response = await fetch('/api/playground', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code }),
                signal: controller.signal,
            });
            setResult(await response.json() as BuildResult);
        } catch (error) {
            if (error instanceof Error && error.name === 'AbortError') return;
            setResult({ ok: false, error: 'worker_unavailable' });
        } finally {
            if (inFlight.current === controller) {
                inFlight.current = null;
                setPending(false);
            }
        }
    }, [code, tooLarge]);

    const tree: FileNode[] = useMemo(() => buildTree(result?.files ?? []), [result]);
    const fileCount = result?.files?.length ?? 0;

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100">
            <Navbar />

            <div className="relative z-10 pt-28 pb-6 px-4">
                <div className="max-w-7xl mx-auto text-center">
                    <h1 className="text-4xl md:text-5xl font-bold mb-3">
                        🧪 <span className={HEADING}>{t('playground.title')}</span>
                    </h1>
                    <p className="text-lg text-slate-300 max-w-3xl mx-auto">{t('playground.subtitle')}</p>
                </div>
            </div>

            <div className="relative z-10 px-4 pb-16">
                <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-4">

                    {/* ── Editor */}
                    <div className="rounded-xl border border-white/10 bg-slate-900/60 flex flex-col overflow-hidden">
                        <div className="flex items-center gap-2 px-4 py-3 border-b border-white/10 flex-wrap bg-white/[0.03]">
                            <span className="text-sm font-semibold text-slate-200 mr-1">{t('playground.presets')}</span>
                            {PRESETS.map(preset => (
                                <button
                                    key={preset.id}
                                    onClick={() => { setCode(preset.code); setActive(preset.id); setResult(null); setSelected(null); }}
                                    className={`text-sm px-3 py-1.5 rounded-lg border transition-colors ${
                                        active === preset.id
                                            ? 'bg-mc-emerald/20 border-mc-emerald/40 text-mc-emerald'
                                            : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10 hover:text-white'
                                    }`}
                                >
                                    {t(`playground.preset.${preset.id}`)}
                                </button>
                            ))}
                        </div>

                        <div className="h-[28rem] lg:h-[34rem]">
                            <Suspense fallback={<div className="p-4 text-xs text-slate-500">{t('playground.loadingEditor')}</div>}>
                                <CodeEditor value={code} onChange={setCode} onSubmit={build} />
                            </Suspense>
                        </div>

                        <div className="flex items-center gap-3 px-4 py-2 border-t border-white/5">
                            <span className={`text-xs ${tooLarge ? 'text-red-400' : size > WARN_CODE_BYTES ? 'text-amber-400' : 'text-slate-500'}`}>
                                {formatBytes(size)} / {formatBytes(MAX_CODE_BYTES)}
                            </span>
                            <span className="text-[0.7rem] text-slate-600 hidden sm:inline">{t('playground.shortcut')}</span>
                            <button
                                onClick={build}
                                disabled={pending || tooLarge}
                                className="ml-auto flex items-center gap-1.5 text-sm px-4 py-1.5 rounded-lg bg-mc-emerald/20 text-mc-emerald border border-mc-emerald/30 hover:bg-mc-emerald/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                            >
                                <HiPlay className="w-4 h-4" />
                                {pending ? t('playground.building') : t('playground.build')}
                            </button>
                        </div>
                    </div>

                    {/* ── Output */}
                    {/* Exactly as tall as the editor beside it, with the tree scrolling inside.
                        h-0 stops the file list contributing to the grid row, and min-h-full then
                        takes the height the editor column established, so the two always match
                        without a magic number to keep in sync. Below lg they stack, and a fixed
                        height is what stops a 500 file build running off the end of the page. */}
                    <div className="rounded-xl border border-white/10 bg-slate-900/60 flex flex-col overflow-hidden h-[32rem] lg:h-0 lg:min-h-full">
                        <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5">
                            <span className="text-xs text-slate-400">{t('playground.output')}</span>
                            {result?.ok && (
                                <span className="text-xs text-slate-500">
                                    {t('playground.filesGenerated').replace('{count}', String(fileCount))}
                                    {result.durationMs !== undefined && ` · ${result.durationMs} ms`}
                                </span>
                            )}
                            {result?.cached && (
                                <span className="text-[0.65rem] px-1.5 py-0.5 rounded bg-white/5 text-slate-400">
                                    {t('playground.cached')}
                                </span>
                            )}
                            {result?.config && (
                                <button
                                    onClick={() => { setShowConfig(true); setSelected(null); }}
                                    className="ml-auto text-xs px-2 py-1 rounded border border-white/10 bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white transition-colors"
                                >
                                    {t('playground.viewConfig')}
                                </button>
                            )}
                        </div>

                        {!result && !pending && (
                            <p className="p-4 text-sm text-slate-500">{t('playground.empty')}</p>
                        )}
                        {pending && <p className="p-4 text-sm text-slate-500">{t('playground.building')}</p>}

                        {result && !result.ok && !showConfig && (
                            <div className="flex-1 flex flex-col p-4 gap-3 min-h-0">
                                <p className="text-sm text-red-300">
                                    {t(`playground.error.${result.error ?? 'worker_unavailable'}`)}
                                    {result.error === 'rate_limited' && result.retryAfterMs !== undefined &&
                                        ` (${Math.ceil(result.retryAfterMs / 1000)}s)`}
                                </p>

                                {/* The one line the reader can act on, ahead of the traceback that
                                    buries it under thirty frames of beet internals. */}
                                {result.message && (
                                    <div className="rounded-lg border border-red-500/25 bg-red-500/5 p-3 space-y-2">
                                        <p className="text-sm font-medium text-red-200 break-words">{result.message}</p>
                                        {result.line !== undefined && (
                                            <p className="text-xs text-slate-400">
                                                {t('playground.atLine').replace('{line}', String(result.line))}
                                                {result.source && (
                                                    <code className="ml-2 text-slate-300">{result.source}</code>
                                                )}
                                            </p>
                                        )}
                                        {result.suggestions && result.suggestions.length > 0 && (
                                            <p className="text-xs text-slate-400">
                                                {t('playground.didYouMean')}{' '}
                                                <span className="text-slate-300">{result.suggestions.join(', ')}</span>
                                            </p>
                                        )}
                                    </div>
                                )}

                                {(result.traceback ?? result.logs) && (
                                    <details className="flex-1 min-h-0 flex flex-col">
                                        <summary className="text-xs text-slate-500 hover:text-slate-300 cursor-pointer">
                                            {t('playground.fullTraceback')}
                                        </summary>
                                        <pre className="mt-2 flex-1 text-[0.7rem] leading-relaxed text-slate-400 bg-black/30 rounded p-3 overflow-auto custom-scrollbar whitespace-pre-wrap min-h-0">
                                            {result.traceback ?? result.logs}
                                        </pre>
                                    </details>
                                )}
                            </div>
                        )}

                        {showConfig && result?.config && (
                            <SourceView
                                label="beet.yml"
                                body={result.config}
                                language="yaml"
                                onBack={() => setShowConfig(false)}
                                backLabel={t('playground.back')}
                            />
                        )}

                        {result?.ok && !selected && !showConfig && (
                            <div className="flex-1 flex flex-col p-4 overflow-auto custom-scrollbar min-h-0">
                                <FileTree nodes={tree} onSelect={node => node.kind && setSelected(node)} reveal />
                                {result.truncated?.files && (
                                    <p className="mt-3 text-xs text-amber-400">
                                        {t('playground.truncated').replace('{count}', String(SANDBOX_LIMITS.files))}
                                    </p>
                                )}
                            </div>
                        )}

                        {result?.ok && selected && !showConfig && (
                            <SourceView
                                label={selected.path ?? selected.name}
                                body={result.text?.[selected.path ?? ''] ?? ''}
                                language={languageOf(selected.path ?? '')}
                                image={result.images?.[selected.path ?? '']}
                                alt={selected.name}
                                onBack={() => setSelected(null)}
                                backLabel={t('playground.back')}
                            />
                        )}
                    </div>
                </div>

                {/* ── Limitations */}
                {/* Always open. Hiding what the playground cannot do behind a toggle means the
                    reader finds out by being surprised, which is the opposite of the point. */}
                <div className="max-w-7xl mx-auto mt-4">
                    <div className="rounded-xl border border-white/10 bg-slate-900/40 p-5 space-y-3">
                        <p className="text-sm font-semibold text-slate-200">{t('playground.limits')}</p>
                        <p className="text-sm text-slate-400 leading-relaxed">{t('playground.limitsDetail')}</p>
                        <p className="text-sm text-slate-400">
                            {t('playground.limitsNumbers')
                                .replace('{cpu}', String(SANDBOX_LIMITS.cpuSeconds))
                                .replace('{wall}', String(SANDBOX_LIMITS.wallSeconds))
                                .replace('{memory}', String(SANDBOX_LIMITS.memoryMiB))
                                .replace('{files}', String(SANDBOX_LIMITS.files))
                                .replace('{total}', String(SANDBOX_LIMITS.totalMiB))}
                        </p>
                        <p className="text-sm">
                            <a href="/documentation" className={`${TEXT_ACCENT} hover:underline`}>
                                {t('playground.fullOutput')}
                            </a>
                        </p>
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    );
};
