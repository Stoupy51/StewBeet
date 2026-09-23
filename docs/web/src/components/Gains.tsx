import { useRef } from 'react';
import { useInView } from 'framer-motion';
import { useTranslation } from '../i18n/useTranslation';
import { useShiki } from '../hooks/useShiki';
import { FileTree } from './FileTree';
import { BY_HAND, GAIN_TILES, type GainTile, type GainVisual, type Snippet } from './gainsData';
import { CARD, EYEBROW, PAGE, SECTION_LEAD, SECTION_TITLE } from '../theme';

/**
 * "What you gain": the countable gain first (eight hand-synced files against one definition), then
 * one tile per thing StewBeet writes for you, each showing the real artefact rather than an icon.
 */

const SPAN: Record<GainTile['span'], string> = {
    narrow: 'lg:col-span-5',
    half: 'lg:col-span-6',
    wide: 'lg:col-span-7',
};

const CODE_CLASS = 'font-mono text-[0.75rem] leading-[1.6] [&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!px-4 [&>pre]:!pb-4 [&>pre]:!pt-1';

const HighlightedCode = ({ code, lang }: { code: string; lang: string }) => (
    <div dangerouslySetInnerHTML={{ __html: useShiki(code, lang) }} className={CODE_CLASS} />
);

/** Plain text until the tile scrolls near, so the highlighter only loads for a reader who gets here. */
const SnippetBlock = ({ snippet, highlight }: { snippet: Snippet; highlight: boolean }) => {
    const { t } = useTranslation();
    const label = snippet.labelKey ? t(snippet.labelKey) : snippet.label;
    return (
        <div className="border-t border-ink-800 first:border-t-0">
            {label && <p className="px-4 pt-3 pb-1 font-mono text-[0.6875rem] text-ink-500 truncate">{label}</p>}
            <div className="overflow-x-auto custom-scrollbar">
                {highlight
                    ? <HighlightedCode code={snippet.code} lang={snippet.lang} />
                    : <pre className={`${CODE_CLASS} px-4 pb-4 pt-1 text-ink-300`}><code>{snippet.code}</code></pre>}
            </div>
        </div>
    );
};

const Visual = ({ visual, highlight }: { visual: GainVisual; highlight: boolean }) => {
    const { t } = useTranslation();
    const snippets = visual.snippets ?? [];
    return (
        <div className="flex-1 flex flex-col border-t border-ink-800 bg-ink-950/60">
            {visual.kind === 'image' && (
                <div className={`flex-1 ${visual.pixelated ? 'flex items-center justify-center p-5' : 'relative min-h-52'} ${snippets.length ? 'border-b border-ink-800' : ''}`}>
                    <img
                        src={visual.src}
                        alt={t(visual.altKey)}
                        loading="lazy"
                        decoding="async"
                        className={visual.pixelated ? 'pixelated max-w-full' : 'absolute inset-0 w-full h-full object-cover object-top'}
                    />
                </div>
            )}
            {visual.kind === 'tree' && (
                <div className="px-4 py-3 border-b border-ink-800">
                    <FileTree nodes={visual.nodes} />
                </div>
            )}
            {snippets.map((snippet) => (
                <SnippetBlock key={snippet.code} snippet={snippet} highlight={highlight} />
            ))}
        </div>
    );
};

const Tile = ({ tile }: { tile: GainTile }) => {
    const { t } = useTranslation();
    const node = useRef<HTMLElement>(null);
    const near = useInView(node, { once: true, margin: '300px 0px' });

    return (
        <article ref={node} id={`gain-${tile.id}`} data-rise className={`${CARD} ${SPAN[tile.span]} flex flex-col overflow-hidden`}>
            <div className="p-5 md:p-6">
                <h3 className="text-base md:text-lg font-semibold tracking-tight text-ink-50">{t(tile.titleKey)}</h3>
                <p className="mt-1.5 text-sm text-ink-400 leading-relaxed text-pretty">{t(tile.bodyKey)}</p>
            </div>
            <Visual visual={tile.visual} highlight={near} />
        </article>
    );
};

/** Copper tells the datapack files from the resource pack ones by hue, since fading it fails contrast. */
const PACK_COLOR = { data: 'text-mc-copper', assets: 'text-ink-300' } as const;

const ComparisonTile = () => {
    const { t } = useTranslation();
    return (
        <article data-rise className={`${CARD} md:col-span-2 lg:col-span-12 p-6 md:p-8`}>
            <div className="grid grid-cols-1 md:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,1fr)] gap-8 md:gap-10">
                <div>
                    <p className="font-mono text-xs uppercase tracking-wider text-ink-400">{t('gains.byHandTitle')}</p>
                    <p className="mt-3 flex items-baseline gap-3">
                        <span className="font-mono text-5xl leading-none text-ink-400">8</span>
                        <span className="text-sm text-ink-400">{t('gains.byHandUnit')}</span>
                    </p>
                    <ul className="mt-6 space-y-1.5 font-mono text-xs">
                        {BY_HAND.map(({ path, role, pack }) => (
                            <li key={path} className="flex items-baseline justify-between gap-3">
                                <span className={`${PACK_COLOR[pack]} truncate`}>{path}</span>
                                <span className="text-ink-500 flex-shrink-0">{role}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="md:border-l md:border-ink-800 md:pl-10 flex flex-col">
                    <p className="font-mono text-xs uppercase tracking-wider text-beet-400">{t('gains.withTitle')}</p>
                    <p className="mt-3 flex items-baseline gap-3">
                        <span className="font-mono text-5xl leading-none text-beet-400">1</span>
                        <span className="text-sm text-ink-300">{t('gains.withUnit')}</span>
                    </p>
                    <p className="mt-6 inline-flex self-start rounded-control border border-beet-500/40 bg-beet-500/10 px-2.5 py-1 font-mono text-xs text-beet-300">
                        {t('gains.withFile')}
                    </p>
                    <p className="mt-4 text-sm text-ink-300 leading-relaxed">{t('gains.withNote')}</p>
                </div>

                <div className="md:border-l md:border-ink-800 md:pl-10 flex items-end">
                    <p className="text-sm text-ink-400 leading-relaxed">{t('gains.noPython')}</p>
                </div>
            </div>

        </article>
    );
};

export const Gains: React.FC = () => {
    const { t } = useTranslation();

    return (
        <section id="features" className="py-20 md:py-28 border-t border-ink-800 scroll-mt-14">
            <div className={PAGE}>
                <div data-rise className="max-w-3xl">
                    <p className={EYEBROW}>{t('gains.eyebrow')}</p>
                    <h2 className={`mt-4 ${SECTION_TITLE}`}>{t('gains.title')}</h2>
                    <p className={`mt-4 ${SECTION_LEAD}`}>{t('gains.lead')}</p>
                </div>

                <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-4">
                    <ComparisonTile />
                    {GAIN_TILES.map((tile) => <Tile key={tile.id} tile={tile} />)}
                </div>
            </div>
        </section>
    );
};
