import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { HiChevronDown, HiChevronRight, HiExternalLink, HiMenuAlt2, HiX } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import {
    API_REFERENCE, DOC_PAGES, PLUGIN_GROUPS, SECTIONS, docHref, neighbours,
    type DocPage, type PluginGroup, type Section,
} from '../docsPages';

export interface TocHeading {
    id: string;
    text: string;
}

const REPO_DOCS = 'https://github.com/Stoupy51/StewBeet/edit/main/docs/web/public/docs';

/** Lowercased and stripped of accents, so "reference" finds "Référence". */
const fold = (text: string) => text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();

/** A section's name with its colour square, as the page list, the breadcrumb and the docs home show it. */
const SectionLabel = ({ section, className = '' }: { section: Section; className?: string }) => {
    const { language } = useTranslation();
    return (
        <p className={`label flex items-center gap-2 ${SECTIONS[section].text} ${className}`}>
            <span className={`w-2 h-2 flex-shrink-0 ${SECTIONS[section].bg}`} aria-hidden="true" />
            {SECTIONS[section].title[language]}
        </p>
    );
};

/**
 * Every page, grouped by section. The desktop sidebar has 34 px rows on a rule, the phone panel
 * 44 px rows, which a thumb can hit. In the sidebar, the current page's marker glides to the next
 * page's row during a page transition.
 */
export const PageList = ({ current, variant, filter = '', onNavigate }: {
    current?: DocPage;
    variant: 'sidebar' | 'panel';
    filter?: string;
    onNavigate?: (page: DocPage) => void;
}) => {
    const { t, language } = useTranslation();
    const compact = variant === 'sidebar';
    const [pluginsOpen, setPluginsOpen] = useState(current?.section === 'plugins');
    const [openedFor, setOpenedFor] = useState(current);
    const currentRow = useRef<HTMLAnchorElement>(null);
    const query = fold(filter.trim());
    const shown = DOC_PAGES.filter((page) => !query || fold(page.title[language]).includes(query));
    const pluginCount = DOC_PAGES.filter((page) => page.section === 'plugins').length;

    // Arriving on a plugin page opens its group, in the same render, so the marker has a row to land on
    if (current !== openedFor) {
        setOpenedFor(current);
        if (current?.section === 'plugins') setPluginsOpen(true);
    }

    // The sidebar scrolls on its own, and the current page stays in it in sight
    useLayoutEffect(() => {
        if (compact) currentRow.current?.scrollIntoView({ block: 'nearest' });
    }, [compact, current]);

    const row = (page: DocPage) => {
        const isCurrent = page === current;
        return (
            <Link
                key={page.src.en}
                ref={isCurrent ? currentRow : undefined}
                to={docHref(page, language)}
                onClick={() => onNavigate?.(page)}
                aria-current={isCurrent ? 'page' : undefined}
                className={compact
                    ? `relative flex items-center min-h-[2.125rem] py-1.5 pl-3 text-sm leading-snug border-l border-border transition-colors ${isCurrent ? 'text-text font-bold' : 'text-text-muted hover:text-text'}`
                    : `flex items-center min-h-11 py-2 px-3 text-[0.9375rem] leading-snug border-l-2 ${isCurrent ? `${SECTIONS[page.section].border} bg-text/5 font-bold` : 'border-transparent'} text-text`}
            >
                {compact && isCurrent && <span className={`doc-marker absolute -left-px inset-y-0 w-0.5 ${SECTIONS[page.section].bg}`} aria-hidden="true" />}
                {page.title[language]}
            </Link>
        );
    };

    const plugins = (Object.keys(PLUGIN_GROUPS) as PluginGroup[]).map((group) => {
        const pages = shown.filter((page) => page.group === group);
        if (!pages.length) return null;
        return (
            <div key={group} className="mt-2 first:mt-0">
                <p className={`text-xs text-text-muted ${compact ? 'pl-3 py-1' : 'px-3 py-1.5'}`}>{PLUGIN_GROUPS[group][language]}</p>
                {pages.map(row)}
            </div>
        );
    });

    const sections = (Object.keys(SECTIONS) as Section[]).map((section) => {
        const pages = shown.filter((page) => page.section === section);
        const apiShown = section === 'reference' && (!query || fold(API_REFERENCE.title[language]).includes(query));
        if (!pages.length && !apiShown) return null;
        const open = section !== 'plugins' || pluginsOpen || query !== '';
        return (
            <div key={section} className={compact ? 'mt-6 first:mt-0' : 'mt-6'}>
                <SectionLabel section={section} className={compact ? 'mb-2' : 'mb-1.5 px-3'} />
                {section === 'plugins' && !query && (
                    <button
                        type="button"
                        onClick={() => setPluginsOpen(!pluginsOpen)}
                        aria-expanded={pluginsOpen}
                        className={compact
                            ? 'flex items-center justify-between w-full min-h-[2.125rem] pl-3 text-sm text-text-muted hover:text-text border-l border-border'
                            : 'flex items-center justify-between w-full min-h-11 px-3 text-[0.9375rem] text-text border-l-2 border-transparent'}
                    >
                        {t(compact ? 'markdown.pluginsShort' : 'markdown.pluginsCount').replace('{n}', String(pluginCount))}
                        <HiChevronDown className={`w-4 h-4 transition-transform ${pluginsOpen ? 'rotate-180' : ''}`} aria-hidden="true" />
                    </button>
                )}
                {section === 'plugins' ? open && <div className={compact ? 'mt-1' : ''}>{plugins}</div> : pages.map(row)}
                {apiShown && (
                    <a
                        href={API_REFERENCE.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={compact
                            ? 'flex items-center justify-between min-h-[2.125rem] pl-3 text-sm text-text-muted hover:text-text border-l border-border'
                            : 'flex items-center justify-between min-h-11 px-3 text-[0.9375rem] text-text border-l-2 border-transparent'}
                    >
                        {API_REFERENCE.title[language]}
                        <HiExternalLink className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
                    </a>
                )}
            </div>
        );
    });

    return (
        <nav aria-label={t('markdown.pages')}>
            {sections}
            {query && !shown.length && <p className="mt-6 px-3 text-sm text-text-muted">{t('markdown.noMatch')}</p>}
        </nav>
    );
};

/** The phone's full-screen list of pages, with a filter at the top. It stays open until the page picked is ready, which closes it. */
export const PagesPanel = ({ current, onClose }: { current?: DocPage; onClose: () => void }) => {
    const { t } = useTranslation();
    const [filter, setFilter] = useState('');

    useEffect(() => {
        const previous = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        const onKey = (event: KeyboardEvent) => event.key === 'Escape' && onClose();
        window.addEventListener('keydown', onKey);
        return () => {
            document.body.style.overflow = previous;
            window.removeEventListener('keydown', onKey);
        };
    }, [onClose]);

    return (
        <div role="dialog" aria-modal="true" aria-label={t('markdown.pages')} className="doc-panel lg:hidden fixed inset-0 z-[60] flex flex-col bg-surface">
            <div className="h-14 flex-shrink-0 flex items-center justify-between pl-4 pr-1.5 border-b border-border">
                <span className="text-[1.375rem] font-bold">{t('markdown.pages')}</span>
                <button type="button" onClick={onClose} aria-label={t('markdown.close')} className="flex items-center justify-center w-11 h-11 text-text">
                    <HiX className="w-5 h-5" aria-hidden="true" />
                </button>
            </div>
            <div className="flex-1 overflow-y-auto">
                <div className="frame min-h-full pt-3 pb-10">
                    <div className="px-3">
                        <label htmlFor="page-filter" className="label block">{t('markdown.filter')}</label>
                        <input
                            id="page-filter"
                            type="search"
                            value={filter}
                            onChange={(event) => setFilter(event.target.value)}
                            placeholder={t('markdown.filterPlaceholder')}
                            className="mt-1.5 w-full h-11 px-3 bg-transparent border border-border text-[0.9375rem] text-text placeholder:text-text-muted/70"
                        />
                    </div>
                    <PageList current={current} variant="panel" filter={filter} onNavigate={(page) => page === current && onClose()} />
                </div>
            </div>
        </div>
    );
};

/** The 48 px bar a doc page keeps at the top of a phone: the page list on the left, this page's headings on the right. */
export const DocBar = ({ headings, onOpenPages, onJump }: {
    headings: TocHeading[];
    onOpenPages: () => void;
    onJump: (id: string) => (event: React.MouseEvent) => void;
}) => {
    const { t } = useTranslation();
    const [tocOpen, setTocOpen] = useState(false);

    return (
        <div className="relative h-12 flex items-center justify-between px-1.5 bg-surface border-b border-border">
            <button type="button" onClick={onOpenPages} className="flex items-center gap-2 h-11 px-2.5 text-[0.9375rem] font-semibold text-text">
                <HiMenuAlt2 className="w-[18px] h-[18px]" aria-hidden="true" />
                {t('markdown.pages')}
            </button>
            {headings.length > 0 && (
                <button
                    type="button"
                    onClick={() => setTocOpen(!tocOpen)}
                    aria-expanded={tocOpen}
                    className="flex items-center gap-2 h-11 px-2.5 text-[0.9375rem] text-text-muted"
                >
                    {t('markdown.onThisPage')}
                    <HiChevronDown className={`w-4 h-4 transition-transform ${tocOpen ? 'rotate-180' : ''}`} aria-hidden="true" />
                </button>
            )}
            {tocOpen && (
                <div className="absolute inset-x-0 top-full max-h-[60vh] overflow-y-auto bg-surface border-b border-border">
                    <div className="frame py-2">
                        {headings.map((heading) => (
                            <a
                                key={heading.id}
                                href={`#${heading.id}`}
                                onClick={(event) => {
                                    setTocOpen(false);
                                    onJump(heading.id)(event);
                                }}
                                className="flex items-center min-h-11 py-2 px-4 text-[0.9375rem] text-text"
                            >
                                {heading.text}
                            </a>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

/** Which heading the reader is in: the last one whose top has gone under the pinned header. */
function useActiveHeading(headings: TocHeading[]): string | undefined {
    const [active, setActive] = useState<string>();
    useEffect(() => {
        let frame = 0;
        const update = () => {
            frame = 0;
            const passed = headings.filter(({ id }) => (document.getElementById(id)?.getBoundingClientRect().top ?? Infinity) < 120);
            setActive(passed.at(-1)?.id);
        };
        const onScroll = () => {
            if (!frame) frame = requestAnimationFrame(update);
        };
        update();
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => {
            window.removeEventListener('scroll', onScroll);
            cancelAnimationFrame(frame);
        };
    }, [headings]);
    return active;
}

/** The desktop's right column: this page's headings, then where to edit or read its source. */
export const PageAside = ({ headings, src, accent, onJump }: {
    headings: TocHeading[];
    src: string;
    accent: string;
    onJump: (id: string) => (event: React.MouseEvent) => void;
}) => {
    const { t } = useTranslation();
    const active = useActiveHeading(headings);

    return (
        <>
            {headings.length > 0 && (
                <>
                    <p className="label mb-2.5">{t('markdown.onThisPage')}</p>
                    <nav aria-label={t('markdown.onThisPage')} className="flex flex-col">
                        {headings.map((heading) => (
                            <a
                                key={heading.id}
                                href={`#${heading.id}`}
                                onClick={onJump(heading.id)}
                                className={`py-1.5 pl-3 text-[0.8125rem] leading-snug border-l transition-colors ${
                                    heading.id === active ? `border-l-2 ${accent} text-text` : 'border-border text-text-muted hover:text-text'
                                }`}
                            >
                                {heading.text}
                            </a>
                        ))}
                    </nav>
                </>
            )}
            <p className="label mt-7 mb-2.5">{t('markdown.thisPage')}</p>
            <SourceLinks src={src} className="flex flex-col gap-2 text-[0.8125rem]" />
        </>
    );
};

export const SourceLinks = ({ src, className }: { src: string; className: string }) => {
    const { t } = useTranslation();
    return (
        <div className={className}>
            <a href={`${REPO_DOCS}/${src}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center min-h-6 text-text-muted hover:text-text transition-colors">
                {t('markdown.editOnGithub')}
            </a>
            <a href={`/docs/${src}`} className="inline-flex items-center min-h-6 text-text-muted hover:text-text transition-colors">
                {t('markdown.readMarkdown')}
            </a>
        </div>
    );
};

export const Breadcrumb = ({ page }: { page?: DocPage }) => {
    const { t, language } = useTranslation();
    return (
        <nav aria-label={t('markdown.breadcrumb')} className="label flex flex-wrap items-center gap-x-1.5">
            <Link to="/docs" className="inline-flex items-center min-h-6 hover:text-text transition-colors">{t('nav.documentation')}</Link>
            {page && (
                <>
                    <span aria-hidden="true">/</span>
                    <span className={SECTIONS[page.section].text}>{SECTIONS[page.section].title[language]}</span>
                    {page.group && (
                        <>
                            <span aria-hidden="true">/</span>
                            <span>{PLUGIN_GROUPS[page.group][language]}</span>
                        </>
                    )}
                </>
            )}
        </nav>
    );
};

/** The pages before and after this one in its section, the next one first on a phone. */
export const PreviousNext = ({ page }: { page: DocPage }) => {
    const { t, language } = useTranslation();
    const { previous, next } = useMemo(() => neighbours(page), [page]);
    if (!previous && !next) return null;

    const card = (target: DocPage, direction: 'previous' | 'next') => {
        const isNext = direction === 'next';
        return (
            <Link
                to={docHref(target, language)}
                className={`group flex items-center gap-3 py-3.5 px-4 border border-border hover:border-ink-600 transition-colors ${isNext ? 'order-1 sm:order-2 sm:col-start-2' : 'order-2 sm:order-1'}`}
            >
                {!isNext && <HiChevronRight className="w-[18px] h-[18px] flex-shrink-0 rotate-180 text-text-muted group-hover:text-text" aria-hidden="true" />}
                <span className={`flex-1 ${isNext ? 'sm:text-right' : ''}`}>
                    <span className="label block">{t(`markdown.${direction}`)}</span>
                    <span className="block mt-1.5 text-base font-bold text-text">{target.title[language]}</span>
                </span>
                {isNext && <HiChevronRight className="w-[18px] h-[18px] flex-shrink-0 text-text-muted group-hover:text-text" aria-hidden="true" />}
            </Link>
        );
    };

    return (
        <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 gap-3">
            {previous && card(previous, 'previous')}
            {next && card(next, 'next')}
        </div>
    );
};
