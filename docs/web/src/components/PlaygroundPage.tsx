import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { HiArrowLeft, HiPlay } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { FileTree, type FileNode } from './FileTree';
import { useShiki } from '../hooks/useShiki';
import { useTranslation } from '../i18n/useTranslation';
import { buildTree, type BuiltFile } from '../utils/pathsToTree';
import { MAX_CODE_BYTES, SANDBOX_LIMITS, WARN_CODE_BYTES } from '../api/playgroundLimits';
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
    error?: string;
    retryAfterMs?: number;
}

const BYTES_IN_KB = 1024;

/** Checkerboard behind transparent PNGs, drawn with a gradient so it costs no request. */
const CHECKERBOARD =
    'bg-[linear-gradient(45deg,#1a1a1a_25%,transparent_25%),linear-gradient(-45deg,#1a1a1a_25%,transparent_25%),linear-gradient(45deg,transparent_75%,#1a1a1a_75%),linear-gradient(-45deg,transparent_75%,#1a1a1a_75%)] bg-[length:16px_16px] bg-[position:0_0,0_8px,8px_-8px,-8px_0]';

function formatBytes(bytes: number): string {
    return bytes < BYTES_IN_KB ? `${bytes} B` : `${(bytes / BYTES_IN_KB).toFixed(1)} KB`;
}

/** Same grammars the rest of the site uses, so a .mcfunction is coloured identically everywhere. */
function languageOf(path: string): string {
    if (path.endsWith('.mcfunction')) return 'mcfunction';
    if (path.endsWith('.json') || path.endsWith('.mcmeta')) return 'json';
    if (path.endsWith('.py')) return 'python';
    return 'text';
}

const FileView: React.FC<{ node: FileNode; result: BuildResult; onBack: () => void; backLabel: string }> = ({
    node, result, onBack, backLabel,
}) => {
    const path = node.path ?? '';
    const body = result.text?.[path] ?? '';
    const image = result.images?.[path];
    const html = useShiki(image ? '' : body, languageOf(path));

    return (
        <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5">
                <button
                    onClick={onBack}
                    className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                    <HiArrowLeft className="w-3 h-3" /> {backLabel}
                </button>
                <code className="ml-auto text-[0.7rem] text-slate-500 truncate">{path}</code>
            </div>

            <div className="flex-1 overflow-auto custom-scrollbar p-4">
                {image ? (
                    <div className={`inline-block p-4 rounded ${CHECKERBOARD}`}>
                        <img
                            src={`data:image/png;base64,${image}`}
                            alt={node.name}
                            className="w-32 h-32 object-contain [image-rendering:pixelated]"
                        />
                    </div>
                ) : (
                    <div
                        className="text-[0.75rem] leading-[1.55] [&_pre]:!bg-transparent [&_pre]:whitespace-pre"
                        dangerouslySetInnerHTML={{ __html: html }}
                    />
                )}
            </div>
        </div>
    );
};

export const PlaygroundPage: React.FC = () => {
    const { t } = useTranslation();
    const [code, setCode] = useState(DEFAULT_CODE);
    const [result, setResult] = useState<BuildResult | null>(null);
    const [pending, setPending] = useState(false);
    const [selected, setSelected] = useState<FileNode | null>(null);
    const [showLimits, setShowLimits] = useState(false);
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

                    {/* ── Editor ─────────────────────────────────────────────── */}
                    <div className="rounded-xl border border-white/10 bg-slate-900/60 flex flex-col overflow-hidden">
                        <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5 flex-wrap">
                            <span className="text-xs text-slate-500 mr-1">{t('playground.presets')}</span>
                            {PRESETS.map(preset => (
                                <button
                                    key={preset.id}
                                    onClick={() => { setCode(preset.code); setResult(null); setSelected(null); }}
                                    className="text-xs px-2 py-1 rounded bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
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

                    {/* ── Output ─────────────────────────────────────────────── */}
                    <div className="rounded-xl border border-white/10 bg-slate-900/60 flex flex-col overflow-hidden min-h-[24rem]">
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
                        </div>

                        {!result && !pending && (
                            <p className="p-4 text-sm text-slate-500">{t('playground.empty')}</p>
                        )}
                        {pending && <p className="p-4 text-sm text-slate-500">{t('playground.building')}</p>}

                        {result && !result.ok && (
                            <div className="p-4 space-y-3">
                                <p className="text-sm text-red-300">
                                    {t(`playground.error.${result.error ?? 'worker_unavailable'}`)}
                                    {result.error === 'rate_limited' && result.retryAfterMs !== undefined &&
                                        ` (${Math.ceil(result.retryAfterMs / 1000)}s)`}
                                </p>
                                {result.logs && (
                                    <pre className="text-[0.7rem] leading-relaxed text-slate-400 bg-black/30 rounded p-3 overflow-auto max-h-72 custom-scrollbar whitespace-pre-wrap">
                                        {result.logs}
                                    </pre>
                                )}
                            </div>
                        )}

                        {result?.ok && !selected && (
                            <div className="flex-1 flex flex-col p-4 overflow-auto custom-scrollbar">
                                <FileTree nodes={tree} onSelect={node => node.kind && setSelected(node)} />
                                {result.truncated?.files && (
                                    <p className="mt-3 text-xs text-amber-400">
                                        {t('playground.truncated').replace('{count}', String(SANDBOX_LIMITS.files))}
                                    </p>
                                )}
                            </div>
                        )}

                        {result?.ok && selected && (
                            <FileView
                                node={selected}
                                result={result}
                                onBack={() => setSelected(null)}
                                backLabel={t('playground.back')}
                            />
                        )}
                    </div>
                </div>

                {/* ── Limitations ────────────────────────────────────────────── */}
                <div className="max-w-7xl mx-auto mt-4">
                    <div className="rounded-xl border border-white/10 bg-slate-900/40 p-4">
                        <button
                            onClick={() => setShowLimits(!showLimits)}
                            className="text-sm text-slate-400 hover:text-slate-200 transition-colors text-left"
                        >
                            {t('playground.limits')} {showLimits ? '▾' : '▸'}
                        </button>

                        {showLimits && (
                            <div className="mt-3 space-y-3 text-sm text-slate-400">
                                <p>{t('playground.limitsDetail')}</p>
                                <p>
                                    {t('playground.limitsNumbers')
                                        .replace('{cpu}', String(SANDBOX_LIMITS.cpuSeconds))
                                        .replace('{wall}', String(SANDBOX_LIMITS.wallSeconds))
                                        .replace('{memory}', String(SANDBOX_LIMITS.memoryMiB))
                                        .replace('{files}', String(SANDBOX_LIMITS.files))
                                        .replace('{total}', String(SANDBOX_LIMITS.totalMiB))}
                                </p>
                                <p>
                                    <a href="/documentation" className={`${TEXT_ACCENT} hover:underline`}>
                                        {t('playground.fullOutput')}
                                    </a>
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    );
};
