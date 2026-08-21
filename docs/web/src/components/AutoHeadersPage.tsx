import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { unzipSync } from 'fflate';
import { HiArrowRight, HiDownload, HiPlay, HiPuzzle, HiUpload } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { FileTree, type FileNode } from './FileTree';
import { SourceView } from './SourceView';
import { useTranslation } from '../i18n/useTranslation';
import { buildTree, type BuiltFile } from '../utils/pathsToTree';
import { formatBytes, languageOf } from '../utils/fileDisplay';
import { HEADERS_LIMITS, MAX_PACK_BYTES } from '../api/sandboxLimits';
import { BTN_SECONDARY, HEADING, TEXT_ACCENT } from '../theme';

/**
 * /auto_headers: upload a datapack, get it back with a header on every function.
 *
 * A successful response is the rewritten archive itself, not a description of one, so the download
 * button is a blob URL the browser already holds: there is no second round trip and the server keeps
 * no copy of anything. The file tree beside it is read from those same bytes with fflate, which is
 * why nothing is fetched again when a reader clicks through the pack.
 *
 * Only `.mcfunction` files come back changed. The pass runs a beet pipeline with
 * stewbeet.plugins.auto.headers and nothing else, and writes the result over the extracted upload
 * rather than dumping the pack, so every other file is returned exactly as it was uploaded.
 */

/** What the worker could not put in a zip body, read back from the response header. */
interface HeadersMeta {
    durationMs?: number;
    functions?: number;
    changed?: number;
    warnings?: string[];
    /** How many warnings did not fit the header, so a trimmed list never looks like a complete one. */
    warningsDropped?: number;
}

/** A JSON response, which is the only shape a failure ever takes. */
interface HeadersFailure {
    error?: string;
    /** Root cause, already unwrapped from beet's PluginError and stouputils' exit path. */
    message?: string;
    traceback?: string;
    logs?: string;
    retryAfterMs?: number;
}

/** A successful response, once the archive has been read. Held until the next run replaces it. */
interface HeadersOutput {
    /** Download name, derived from the upload so it is recognisable in a downloads folder. */
    name: string;
    /** Blob URL of the archive. Revoked when it is replaced, so a long session leaks nothing. */
    url: string;
    bytes: number;
    entries: Record<string, Uint8Array>;
    files: BuiltFile[];
    meta: HeadersMeta;
}

/** Extensions worth opening in the viewer. Anything else stays an unselectable row. */
const TEXT_EXTENSIONS = ['.mcfunction', '.json', '.mcmeta', '.txt', '.md', '.yml', '.yaml', '.snbt'];

/** Chunk size for base64, since spreading a whole texture into fromCharCode blows the call stack. */
const BASE64_CHUNK = 0x8000;

function kindOf(path: string): BuiltFile['kind'] {
    if (path.endsWith('.png')) return 'image';
    return TEXT_EXTENSIONS.some(extension => path.endsWith(extension)) ? 'text' : undefined;
}

/**
 * Read the metadata header, which is base64 of UTF-8 JSON.
 *
 * `atob` alone would be wrong: it yields one char per byte, so a warning naming a function with an
 * accent in it would arrive mojibake. The bytes go through TextDecoder instead.
 */
function decodeMeta(encoded: string): HeadersMeta {
    if (!encoded) return {};
    try {
        const binary = atob(encoded);
        const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
        return JSON.parse(new TextDecoder().decode(bytes)) as HeadersMeta;
    } catch {
        return {};
    }
}

function toBase64(bytes: Uint8Array): string {
    let binary = '';
    for (let offset = 0; offset < bytes.length; offset += BASE64_CHUNK) {
        binary += String.fromCharCode(...bytes.subarray(offset, offset + BASE64_CHUNK));
    }
    return btoa(binary);
}

/** The plugin's own page, linked from the header and from the panel at the bottom. */
const PLUGIN_DOC = `/markdown?src=${encodeURIComponent('plugins/auto.headers.md')}`;

/** `MyPack.zip` -> `MyPack_headers.zip`, so the result never overwrites the upload it came from. */
function downloadName(uploaded: string): string {
    return `${uploaded.replace(/\.zip$/i, '')}_headers.zip`;
}

export const AutoHeadersPage: React.FC = () => {
    const { t } = useTranslation();
    const [file, setFile] = useState<File | null>(null);
    const [pending, setPending] = useState(false);
    const [output, setOutput] = useState<HeadersOutput | null>(null);
    const [failure, setFailure] = useState<HeadersFailure | null>(null);
    const [selected, setSelected] = useState<FileNode | null>(null);
    const [dragging, setDragging] = useState(false);
    const picker = useRef<HTMLInputElement>(null);
    const inFlight = useRef<AbortController | null>(null);

    // A run in flight when the reader navigates away has nowhere to land, and its response would set
    // state on an unmounted tree.
    useEffect(() => () => inFlight.current?.abort(), []);

    // Revoking on the way out of an effect keyed by the URL covers both cases at once: a second run
    // replacing the first archive, and the reader leaving. Without it a long session holds every
    // archive it ever produced, at tens of megabytes each.
    const outputUrl = output?.url;
    useEffect(() => () => { if (outputUrl) URL.revokeObjectURL(outputUrl); }, [outputUrl]);

    const tooLarge = file !== null && file.size > MAX_PACK_BYTES;

    const accept = useCallback((picked: File | null) => {
        setFile(picked);
        setOutput(null);
        setFailure(null);
        setSelected(null);
    }, []);

    const run = useCallback(async () => {
        if (!file || tooLarge) return;
        inFlight.current?.abort();
        const controller = new AbortController();
        inFlight.current = controller;

        setPending(true);
        setFailure(null);
        setSelected(null);
        try {
            const response = await fetch('/api/tools/headers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/zip' },
                body: file,
                signal: controller.signal,
            });

            if (!response.headers.get('content-type')?.startsWith('application/zip')) {
                setOutput(null);
                setFailure(await response.json() as HeadersFailure);
                return;
            }

            const archive = new Uint8Array(await response.arrayBuffer());
            const entries = unzipSync(archive);
            const files: BuiltFile[] = Object.entries(entries).map(([path, bytes]) => ({
                path,
                kind: kindOf(path),
                bytes: bytes.length,
            }));

            setOutput({
                name: downloadName(file.name),
                url: URL.createObjectURL(new Blob([archive], { type: 'application/zip' })),
                bytes: archive.length,
                entries,
                files,
                meta: decodeMeta(response.headers.get('X-Sandbox-Meta') ?? ''),
            });
        } catch (error) {
            if (error instanceof Error && error.name === 'AbortError') return;
            setOutput(null);
            // A zip the browser cannot open after the worker wrote it is not a network failure, but
            // both leave the reader with nothing, and only one of them is worth a different sentence.
            setFailure({ error: 'worker_unavailable' });
        } finally {
            if (inFlight.current === controller) {
                inFlight.current = null;
                setPending(false);
            }
        }
    }, [file, tooLarge]);

    const tree: FileNode[] = useMemo(() => buildTree(output?.files ?? []), [output]);

    const body = useMemo(() => {
        const bytes = selected?.path !== undefined ? output?.entries[selected.path] : undefined;
        if (!bytes || selected?.kind !== 'text') return '';
        return new TextDecoder().decode(bytes).replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    }, [output, selected]);

    const image = useMemo(() => {
        const bytes = selected?.path !== undefined ? output?.entries[selected.path] : undefined;
        return bytes && selected?.kind === 'image' ? toBase64(bytes) : undefined;
    }, [output, selected]);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100">
            <Navbar />

            <div className="relative z-10 pt-28 pb-6 px-4">
                <div className="max-w-7xl mx-auto text-center">
                    <h1 className="text-4xl md:text-5xl font-bold mb-3">
                        🏷️ <span className={HEADING}>{t('autoHeaders.title')}</span>
                    </h1>
                    <p className="text-lg text-slate-300 max-w-3xl mx-auto">{t('autoHeaders.subtitle')}</p>
                </div>
            </div>

            <div className="relative z-10 px-4 pb-16">
                <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-4">

                    {/* ── Upload */}
                    {/* Both columns take the same explicit height rather than one measuring the
                        other, because there is no editor here to set it: a drop zone is as tall as
                        you make it, and left to itself it made the result panel too short to read a
                        function in. Below lg they stack and the upload panel shrinks to its content. */}
                    <div className="rounded-xl border border-white/10 bg-slate-900/60 flex flex-col overflow-hidden lg:h-[34rem]">
                        {/* A button rather than a div with an onClick, so the picker opens from the
                            keyboard too. The input is its sibling and not its child: inside it, the
                            click it receives from picker.click() would bubble straight back into this
                            handler and open it again. */}
                        <button
                            type="button"
                            onDragOver={event => { event.preventDefault(); setDragging(true); }}
                            onDragLeave={() => setDragging(false)}
                            onDrop={event => {
                                event.preventDefault();
                                setDragging(false);
                                accept(event.dataTransfer.files[0] ?? null);
                            }}
                            onClick={() => picker.current?.click()}
                            className={`m-4 flex-1 min-h-[16rem] rounded-xl border-2 border-dashed flex flex-col items-center justify-center gap-3 p-6 text-center transition-colors ${
                                dragging ? 'border-mc-emerald/60 bg-mc-emerald/5' : 'border-white/15 hover:border-white/30 hover:bg-white/[0.02]'
                            }`}
                        >
                            <HiUpload className="w-8 h-8 text-slate-500" />
                            <span className="text-sm text-slate-300">{t('autoHeaders.drop')}</span>
                            <span className="text-xs text-slate-500">
                                {t('autoHeaders.maxSize').replace('{size}', String(HEADERS_LIMITS.packMiB))}
                            </span>
                            {file && (
                                <span className={`text-sm ${tooLarge ? 'text-red-400' : 'text-mc-emerald'}`}>
                                    {file.name} · {formatBytes(file.size)}
                                </span>
                            )}
                            {tooLarge && (
                                <span className="text-xs text-red-400">{t('autoHeaders.error.pack_too_large')}</span>
                            )}
                        </button>
                        <input
                            ref={picker}
                            type="file"
                            accept=".zip,application/zip"
                            className="hidden"
                            onChange={event => accept(event.target.files?.[0] ?? null)}
                        />

                        <div className="flex items-center gap-3 px-4 py-2 border-t border-white/5">
                            <span className="text-xs text-slate-500">{t('autoHeaders.pipeline')}</span>
                            <button
                                onClick={run}
                                disabled={!file || pending || tooLarge}
                                className="ml-auto flex items-center gap-1.5 text-sm px-4 py-1.5 rounded-lg bg-mc-emerald/20 text-mc-emerald border border-mc-emerald/30 hover:bg-mc-emerald/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                            >
                                <HiPlay className="w-4 h-4" />
                                {pending ? t('autoHeaders.running') : t('autoHeaders.run')}
                            </button>
                        </div>
                    </div>

                    {/* ── Output */}
                    {/* A fixed height, not a fitted one: it is what stops a four thousand file pack
                        running off the end of the page, and the tree scrolls inside it instead. */}
                    <div className="rounded-xl border border-white/10 bg-slate-900/60 flex flex-col overflow-hidden h-[32rem] lg:h-[34rem]">
                        <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5 flex-wrap">
                            <span className="text-xs text-slate-400">{t('autoHeaders.output')}</span>
                            {output && (
                                <span className="text-xs text-slate-500">
                                    {t('autoHeaders.rewritten')
                                        .replace('{changed}', String(output.meta.changed ?? 0))
                                        .replace('{functions}', String(output.meta.functions ?? 0))}
                                    {output.meta.durationMs !== undefined && ` · ${output.meta.durationMs} ms`}
                                </span>
                            )}
                            {output && (
                                <a
                                    href={output.url}
                                    download={output.name}
                                    className="ml-auto flex items-center gap-1.5 text-xs px-2.5 py-1 rounded border border-mc-emerald/30 bg-mc-emerald/20 text-mc-emerald hover:bg-mc-emerald/30 transition-colors"
                                >
                                    <HiDownload className="w-3.5 h-3.5" />
                                    {t('autoHeaders.download').replace('{size}', formatBytes(output.bytes))}
                                </a>
                            )}
                        </div>

                        {!output && !failure && !pending && (
                            <p className="p-4 text-sm text-slate-500">{t('autoHeaders.empty')}</p>
                        )}
                        {pending && <p className="p-4 text-sm text-slate-500">{t('autoHeaders.running')}</p>}

                        {failure && (
                            <div className="flex-1 flex flex-col p-4 gap-3 min-h-0">
                                <p className="text-sm text-red-300">
                                    {t(`autoHeaders.error.${failure.error ?? 'worker_unavailable'}`)}
                                    {failure.error === 'rate_limited' && failure.retryAfterMs !== undefined &&
                                        ` (${Math.ceil(failure.retryAfterMs / 1000)}s)`}
                                </p>

                                {failure.message && (
                                    <div className="rounded-lg border border-red-500/25 bg-red-500/5 p-3">
                                        <p className="text-sm font-medium text-red-200 break-words">{failure.message}</p>
                                    </div>
                                )}

                                {(failure.traceback ?? failure.logs) && (
                                    <details className="flex-1 min-h-0 flex flex-col">
                                        <summary className="text-xs text-slate-500 hover:text-slate-300 cursor-pointer">
                                            {t('autoHeaders.fullTraceback')}
                                        </summary>
                                        <pre className="mt-2 flex-1 text-[0.7rem] leading-relaxed text-slate-400 bg-black/30 rounded p-3 overflow-auto custom-scrollbar whitespace-pre-wrap min-h-0">
                                            {failure.traceback ?? failure.logs}
                                        </pre>
                                    </details>
                                )}
                            </div>
                        )}

                        {output && !selected && (
                            <div className="flex-1 flex flex-col p-4 overflow-auto custom-scrollbar min-h-0">
                                {(output.meta.warnings?.length ?? 0) > 0 && (
                                    <div className="mb-3 rounded-lg border border-amber-500/25 bg-amber-500/5 p-3 space-y-1">
                                        {output.meta.warnings?.map(warning => (
                                            <p key={warning} className="text-xs text-amber-200 break-words">{warning}</p>
                                        ))}
                                        {output.meta.warningsDropped !== undefined && (
                                            <p className="text-xs text-amber-400/70">
                                                {t('autoHeaders.warningsDropped').replace('{count}', String(output.meta.warningsDropped))}
                                            </p>
                                        )}
                                    </div>
                                )}
                                <FileTree nodes={tree} onSelect={node => node.kind && setSelected(node)} reveal />
                            </div>
                        )}

                        {output && selected && (
                            <SourceView
                                label={selected.path ?? selected.name}
                                body={body}
                                language={languageOf(selected.path ?? '')}
                                image={image}
                                alt={selected.name}
                                onBack={() => setSelected(null)}
                                backLabel={t('autoHeaders.back')}
                            />
                        )}
                    </div>
                </div>

                {/* ── The plugin behind it */}
                {/* Between the tool and its limitations, which is where a reader who just used it
                    once looks next: the tool is the second-best way to use auto.headers, and someone
                    who never learns it is a plugin they can put in their own pipeline has been sold
                    the wrong thing. */}
                <div className="max-w-7xl mx-auto mt-4 text-center">
                    <Link
                        to={PLUGIN_DOC}
                        className={`inline-flex items-center gap-2 text-sm px-4 py-2 rounded-lg ${BTN_SECONDARY} transition-colors`}
                    >
                        <HiPuzzle className="w-4 h-4" />
                        {t('autoHeaders.pluginLink')}
                        <HiArrowRight className="w-4 h-4" />
                    </Link>
                </div>

                {/* ── Limitations */}
                <div className="max-w-7xl mx-auto mt-4">
                    <div className="rounded-xl border border-white/10 bg-slate-900/40 p-5 space-y-3">
                        <p className="text-sm font-semibold text-slate-200">{t('autoHeaders.limits')}</p>
                        <p className="text-sm text-slate-400 leading-relaxed">{t('autoHeaders.limitsDetail')}</p>
                        <p className="text-sm text-slate-400">
                            {t('autoHeaders.limitsNumbers')
                                .replace('{pack}', String(HEADERS_LIMITS.packMiB))
                                .replace('{extracted}', String(HEADERS_LIMITS.extractedMiB))
                                .replace('{entries}', String(HEADERS_LIMITS.entries))
                                .replace('{cpu}', String(HEADERS_LIMITS.cpuSeconds))
                                .replace('{wall}', String(HEADERS_LIMITS.wallSeconds))
                                .replace('{memory}', String(HEADERS_LIMITS.memoryMiB))}
                        </p>
                        <p className="text-sm text-slate-400 leading-relaxed">{t('autoHeaders.standalone')}</p>
                        <p className="text-sm">
                            <Link to={PLUGIN_DOC} className={`${TEXT_ACCENT} hover:underline`}>
                                {t('autoHeaders.readDocs')}
                            </Link>
                        </p>
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    );
};
