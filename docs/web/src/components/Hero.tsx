import { HiArrowNarrowRight, HiArrowRight } from 'react-icons/hi';
import { useLayoutEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { introWillPlay, useIntro } from '../hooks/useIntro';
import { useOverflowFade } from '../hooks/useOverflowFade';
import { HeroOutputPanel } from './HeroOutputPanel';
import { CodeTab } from './CodeTab';
import { CopyCommand } from './CopyCommand';
import { TrustStrip } from './TrustStrip';
import type { FileNode } from './FileTree';
import heroCode from '../generated/heroCode.json';
import heroOutput from '../generated/heroOutput.json';
import stats from '../generated/stats.json';
import { BTN_PRIMARY, PAGE } from '../theme';

const RELEASES_URL = 'https://github.com/Stoupy51/StewBeet/releases';

function daysSince(iso: string): number {
    return Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000));
}

function releaseAge(days: number, t: (key: string) => string): string {
    if (days === 0) return t('hero.releasedToday');
    if (days === 1) return t('hero.releasedYesterday');
    return t('hero.releasedDaysAgo').replace('{n}', String(days));
}

/**
 * Counts up to the number of generated files while they stream into the tree.
 *
 * The text is written through a ref rather than state, so the rendered output always matches the
 * prerendered markup and a visitor who is not shown the intro never sees a rewind. Only the first
 * label counts up: a later one (another tab, another language) is written as is.
 */
const FileCounter = ({ label }: { label: string }) => {
    const node = useRef<HTMLSpanElement>(null);
    const initial = useRef(label);
    const counted = useRef(false);

    useLayoutEffect(() => {
        const total = Number(label.match(/\d+/)?.[0] ?? 0);
        const element = node.current;
        if (!element) return;
        // The count below replaces the text node React rendered, so React can no longer update it.
        element.textContent = label;
        if (!total || counted.current || label !== initial.current || !introWillPlay()) return;

        // Matches the row cascade in index.css: 760ms before the first file, 42ms apart.
        const START = 760;
        const STEP = 42;
        const write = (value: number) => {
            element.textContent = label.replace(String(total), String(value));
        };

        write(0);
        let frame = 0;
        const begun = performance.now();
        const tick = () => {
            const landed = Math.max(0, Math.min(total, Math.floor((performance.now() - begun - START) / STEP)));
            write(landed);
            if (landed < total) frame = requestAnimationFrame(tick);
            else counted.current = true;
        };
        frame = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(frame);
    }, [label]);

    return <span ref={node} className="font-mono text-xs text-leaf-400 tabular-nums">{label}</span>;
};

const step = (index: number) => ({ '--step': index }) as React.CSSProperties;

/** Files of the tree that the given snippet produces. */
function filesFrom(nodes: FileNode[], snippet: string): number {
    return nodes.reduce((total, node) => total + (node.children ? filesFrom(node.children, snippet) : Number(node.snippet === snippet)), 0);
}

const tree = heroOutput.tree as FileNode[];

/** Code panel showing the longest snippet: 2px of border, the 2.5rem tab, 2rem of padding and 0.75rem lines at 1.55. */
const CODE_HEIGHT = `calc(${Math.max(...heroCode.snippets.map(({ lines }) => lines))} * 1.1625rem + 4.5rem + 2px)`;

export const Hero: React.FC = () => {
    const { t, language } = useTranslation();
    const gettingStarted = `/markdown?src=${encodeURIComponent(language === 'fr' ? '0_getting_started/fr.md' : '0_getting_started/en.md')}`;
    useIntro();
    const [active, setActive] = useState(heroCode.snippets[0].id);
    const snippet = heroCode.snippets.find(({ id }) => id === active) ?? heroCode.snippets[0];
    const codeScroll = useOverflowFade();

    return (
        <section id="hero" className="pt-14">
            <div className={`${PAGE} pt-8 md:pt-10 short:pt-5 pb-12`}>
                <div className="text-center">
                    <a
                        href={RELEASES_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="intro-step inline-flex items-center gap-2 font-mono text-xs text-ink-400 hover:text-ink-100 transition-colors"
                        style={step(0)}
                    >
                        <span className="w-1.5 h-1.5 bg-leaf-400" aria-hidden="true" />
                        v{stats.version}
                        {/* The age is computed again in the browser, days after the prerender, so the text may differ. */}
                        {stats.releasedAt && <span suppressHydrationWarning> · {releaseAge(daysSince(stats.releasedAt), t)}</span>}
                        {' · '}{t('hero.license')}
                    </a>

                    <h1
                        className="intro-step mt-4 short:mt-3 text-[2rem] sm:text-5xl lg:text-[2.875rem] font-semibold tracking-[-0.025em] leading-[1.08] text-ink-50 text-balance"
                        style={step(1)}
                    >
                        {t('hero.title')}
                    </h1>

                    <p className="intro-step mt-4 short:mt-3 max-w-2xl mx-auto text-base sm:text-lg text-ink-300 leading-relaxed text-pretty" style={step(2)}>
                        {t('hero.subtitle')}
                    </p>

                    <div className="intro-step mt-6 short:mt-5 flex flex-col sm:flex-row flex-wrap items-center justify-center gap-3" style={step(3)}>
                        <Link to={gettingStarted} className={`${BTN_PRIMARY} h-11 px-5`}>
                            {t('hero.getStarted')}
                            <HiArrowRight aria-hidden="true" />
                        </Link>
                        <CopyCommand command="pip install stewbeet" />
                        <Link
                            to="/playground"
                            className="group inline-flex items-center gap-1.5 h-11 px-3 text-sm font-medium text-ink-200 hover:text-ink-50 transition-colors"
                        >
                            {t('hero.tryPlayground')}
                            <HiArrowRight className="text-ink-400 group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
                        </Link>
                    </div>

                    <div className="intro-step mt-6 short:mt-4" style={step(4)}>
                        <TrustStrip />
                    </div>
                </div>

                {/* Side by side from lg, not xl: 1920x1080 at 150% leaves ~1265px once the
                    scrollbar is counted, and the output must not fall under the fold there.
                    The height is the longest snippet's, capped at the room left under the header
                    (26.25rem, 23.25rem on short screens) plus a margin, and the minmax row keeps
                    the taller file tree from stretching it. */}
                <div
                    className="mt-7 short:mt-5 grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_1.5rem_minmax(0,1fr)] lg:grid-rows-[minmax(0,1fr)] gap-3 lg:gap-2 lg:h-[min(var(--code-height),clamp(16rem,calc(100svh-26.25rem),32.5rem))] lg:short:h-[min(var(--code-height),clamp(15rem,calc(100svh-23.25rem),32.5rem))]"
                    style={{ '--code-height': CODE_HEIGHT } as React.CSSProperties}
                >
                    <div className="intro-panel min-w-0 min-h-[var(--code-height)] lg:min-h-0 max-h-[31rem] lg:max-h-none" style={step(0)}>
                        <CodeTab
                            path={t('hero.codeCaption')}
                            accessory={
                                <div role="group" aria-label={t('hero.snippetTabs')} className="flex items-center gap-1">
                                    {heroCode.snippets.map(({ id, label }) => (
                                        <button
                                            key={id}
                                            onClick={() => setActive(id)}
                                            aria-pressed={id === active}
                                            className={`h-6 px-2 rounded-control font-mono text-[0.6875rem] transition-colors ${
                                                id === active ? 'bg-ink-800 text-ink-50' : 'text-ink-400 hover:text-ink-100'
                                            }`}
                                        >
                                            {label}
                                        </button>
                                    ))}
                                </div>
                            }
                        >
                            <div ref={codeScroll} className="relative flex-1 min-h-0 p-4 overflow-auto custom-scrollbar">
                                <div
                                    aria-hidden="true"
                                    className="intro-scan pointer-events-none absolute inset-x-0 top-0 h-16 opacity-0 bg-gradient-to-b from-transparent via-beet-500/20 to-transparent"
                                />
                                <div
                                    dangerouslySetInnerHTML={{ __html: snippet.html }}
                                    className="font-mono text-[0.75rem] leading-[1.55] [&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-0 [&_code]:font-mono"
                                />
                            </div>
                        </CodeTab>
                    </div>

                    <div className="flex items-center justify-center text-ink-500" aria-hidden="true">
                        <HiArrowNarrowRight className="text-xl rotate-90 lg:rotate-0" />
                    </div>

                    <div
                        className="intro-panel min-w-0 min-h-0 max-h-[30rem] lg:max-h-none"
                        // --row-start holds the tree back until the scan has passed over the definition.
                        style={{ ...step(1), '--row-start': '760ms' } as React.CSSProperties}
                    >
                        <CodeTab
                            path={t('hero.outputCaption')}
                            accessory={
                                <FileCounter
                                    label={t('hero.outputSummary')
                                        .replace('{count}', String(filesFrom(tree, active)))
                                        .replace('{total}', String(heroOutput.fileCount))}
                                />
                            }
                        >
                            <HeroOutputPanel nodes={tree} active={active} />
                        </CodeTab>
                    </div>
                </div>
            </div>
        </section>
    );
};
