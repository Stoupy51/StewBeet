import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiExternalLink, HiSearch, HiX } from 'react-icons/hi';
import { useLanguage } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { loadIndex, search, TYPE_ORDER } from '../utils/search';
import type { EntryType, SearchResult } from '../utils/search';
import { LIST_SELECTED, LOADER_ACCENT, TEXT_ACCENT } from '../theme';

const DEBOUNCE_MS = 120;
const FILTERS_STORAGE_KEY = 'search-filters';

/** Per-category colors, used by both the filter chips and the section headers. */
const TYPE_STYLES: Record<EntryType, { active: string; text: string }> = {
    doc: { active: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40', text: 'text-indigo-300' },
    api: { active: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40', text: 'text-emerald-300' },
    plugin: { active: 'bg-purple-500/20 text-purple-300 border-purple-500/40', text: 'text-purple-300' },
    site: { active: 'bg-sky-500/20 text-sky-300 border-sky-500/40', text: 'text-sky-300' },
};

const SECTION_KEYS: Record<EntryType, string> = {
    doc: 'search.sectionDoc',
    api: 'search.sectionApi',
    plugin: 'search.sectionPlugin',
    site: 'search.sectionSite',
};

/** Restore the previously enabled categories, defaulting to all of them. */
function readStoredFilters(): Set<EntryType> {
    try {
        const stored = localStorage.getItem(FILTERS_STORAGE_KEY);
        if (stored) {
            const types = (JSON.parse(stored) as EntryType[]).filter((type) => TYPE_ORDER.includes(type));
            if (types.length > 0) return new Set(types);
        }
    } catch {
        // ignore unreadable storage
    }
    return new Set(TYPE_ORDER);
}

export const SearchModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
    const { t } = useTranslation();
    const { language } = useLanguage();
    const navigate = useNavigate();
    const inputRef = useRef<HTMLInputElement>(null);
    const listRef = useRef<HTMLDivElement>(null);

    const [query, setQuery] = useState<string>('');
    const [debounced, setDebounced] = useState<string>('');
    const [matches, setMatches] = useState<SearchResult[]>([]);
    const [filters, setFilters] = useState<Set<EntryType>>(readStoredFilters);
    const [selected, setSelected] = useState<number>(0);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Load the index as soon as the modal opens (usually already warm from the hover prefetch)
    useEffect(() => {
        let cancelled = false;
        loadIndex(language)
            .then(() => !cancelled && setLoading(false))
            .catch((err: Error) => {
                if (cancelled) return;
                setError(err.message);
                setLoading(false);
            });
        return () => {
            cancelled = true;
        };
    }, [language]);

    useEffect(() => {
        const timeout = window.setTimeout(() => setDebounced(query), DEBOUNCE_MS);
        return () => window.clearTimeout(timeout);
    }, [query]);

    useEffect(() => {
        if (!debounced.trim()) return;

        let cancelled = false;
        loadIndex(language).then((index) => {
            if (cancelled) return;
            setMatches(search(debounced, index, filters));
            setSelected(0);
        }).catch(() => undefined);
        return () => {
            cancelled = true;
        };
    }, [debounced, language, filters]);

    const toggleFilter = (type: EntryType) => {
        setFilters((current) => {
            const next = new Set(current);
            if (next.has(type) && next.size > 1) next.delete(type);
            else next.add(type);
            try {
                localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify([...next]));
            } catch {
                // ignore unwritable storage
            }
            return next;
        });
    };

    // Derived so an emptied query drops the previous matches without another render pass
    const results = debounced.trim() ? matches : [];

    // Focus the input and freeze the page behind the overlay
    useEffect(() => {
        inputRef.current?.focus();
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = previousOverflow;
        };
    }, []);

    const goTo = useCallback((result: SearchResult) => {
        onClose();
        if (result.external) {
            window.open(result.url, '_blank', 'noopener,noreferrer');
            return;
        }

        // Same-page anchors (site sections) must be scrolled to manually
        const [path, hash] = result.url.split('#');
        if (hash && (path === '' || path === window.location.pathname)) {
            document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth' });
            return;
        }
        if (result.type === 'site') {
            window.location.href = result.url;
            return;
        }
        navigate(result.url);
    }, [navigate, onClose]);

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            event.preventDefault();
            setSelected((current) => {
                if (results.length === 0) return 0;
                const next = event.key === 'ArrowDown' ? current + 1 : current - 1;
                return (next + results.length) % results.length;
            });
        } else if (event.key === 'Enter' && results[selected]) {
            event.preventDefault();
            goTo(results[selected]);
        } else if (event.key === 'Escape') {
            event.preventDefault();
            onClose();
        }
    };

    // Keep the highlighted row inside the scrollable list (section headers are not rows)
    useEffect(() => {
        listRef.current?.querySelector(`[data-result="${selected}"]`)?.scrollIntoView({ block: 'nearest' });
    }, [selected]);

    const status = useMemo(() => {
        if (error) return error;
        if (loading) return t('search.loading');
        if (!debounced.trim()) return t('search.hint');
        if (results.length === 0) return t('search.noResults');
        return null;
    }, [error, loading, debounced, results.length, t]);

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            onClick={onClose}
            className="fixed inset-0 z-[60] bg-black/70 backdrop-blur-sm p-4 pt-[10vh] flex justify-center"
        >
            <motion.div
                initial={{ scale: 0.97, y: -10 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.97, y: -10 }}
                transition={{ duration: 0.15 }}
                onClick={(event) => event.stopPropagation()}
                onKeyDown={handleKeyDown}
                className="w-full max-w-2xl h-fit max-h-[80vh] flex flex-col bg-slate-900/95 border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
            >
                {/* Input */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
                    <HiSearch className={`text-xl flex-shrink-0 ${TEXT_ACCENT}`} />
                    <input
                        ref={inputRef}
                        type="search"
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder={t('search.placeholder')}
                        className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 outline-none"
                    />
                    <button
                        onClick={onClose}
                        aria-label={t('search.close')}
                        className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/10 transition-colors"
                    >
                        <HiX className="text-xl" />
                    </button>
                </div>

                {/* Category filters */}
                <div className="flex flex-wrap items-center gap-2 px-4 py-2 border-b border-white/10">
                    {TYPE_ORDER.map((type) => (
                        <button
                            key={type}
                            onClick={() => toggleFilter(type)}
                            aria-pressed={filters.has(type)}
                            className={`px-2.5 py-1 rounded-full border text-xs font-medium transition-colors ${
                                filters.has(type)
                                    ? TYPE_STYLES[type].active
                                    : 'bg-transparent border-white/10 text-slate-500 hover:text-slate-300'
                            }`}
                        >
                            {t(SECTION_KEYS[type])}
                        </button>
                    ))}
                </div>

                {/* Results */}
                <div ref={listRef} className="overflow-y-auto">
                    {status && (
                        <div className="flex items-center justify-center gap-3 py-10 text-slate-400 text-sm">
                            {loading && !error && (
                                <span className={`animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 ${LOADER_ACCENT}`} />
                            )}
                            {status}
                        </div>
                    )}

                    {!status && results.map((result, index) => (
                        <div key={`${result.url}-${index}`}>
                            {/* Section header whenever the category changes */}
                            {result.type !== results[index - 1]?.type && (
                                <div className={`px-4 pt-3 pb-1 text-[11px] font-bold uppercase tracking-wider ${TYPE_STYLES[result.type].text}`}>
                                    {t(SECTION_KEYS[result.type])}
                                </div>
                            )}
                            <button
                                data-result={index}
                                onClick={() => goTo(result)}
                                onMouseEnter={() => setSelected(index)}
                                className={`w-full text-left px-4 py-3 border-b border-white/5 transition-colors ${
                                    index === selected ? LIST_SELECTED : 'hover:bg-white/5'
                                }`}
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-xs text-slate-400 truncate">{result.document}</span>
                                    {result.external && <HiExternalLink className="text-xs text-slate-500 flex-shrink-0" />}
                                </div>
                                {result.heading && (
                                    <div className="text-slate-100 font-semibold text-sm mb-0.5 truncate">{result.heading}</div>
                                )}
                                {result.snippet.length > 0 && (
                                    <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                                        {result.snippet.map((segment, segmentIndex) =>
                                            segment.hit
                                                ? <mark key={segmentIndex} className="bg-indigo-500/30 text-indigo-200 rounded px-0.5">{segment.text}</mark>
                                                : <span key={segmentIndex}>{segment.text}</span>,
                                        )}
                                    </p>
                                )}
                            </button>
                        </div>
                    ))}
                </div>

                {/* Footer hints */}
                <div className="flex items-center gap-4 px-4 py-2 border-t border-white/10 text-[11px] text-slate-500">
                    <span><kbd className="px-1 rounded bg-white/10">↑</kbd> <kbd className="px-1 rounded bg-white/10">↓</kbd> {t('search.hintNavigate')}</span>
                    <span><kbd className="px-1 rounded bg-white/10">↵</kbd> {t('search.hintOpen')}</span>
                    <span><kbd className="px-1 rounded bg-white/10">esc</kbd> {t('search.hintClose')}</span>
                </div>
            </motion.div>
        </motion.div>
    );
};

export default SearchModal;
