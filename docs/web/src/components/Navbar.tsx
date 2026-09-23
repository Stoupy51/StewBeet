import { useState, useEffect, useCallback, memo, lazy, Suspense } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { HiMenu, HiSearch, HiX } from 'react-icons/hi';
import { SiDiscord, SiGithub } from 'react-icons/si';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { useLanguage } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { loadIndex } from '../utils/search';
import { VscodeMark } from './VscodeMark';
import stats from '../generated/stats.json';
import { PAGE } from '../theme';

const SearchModal = lazy(() => import('./SearchModal').then(m => ({ default: m.SearchModal })));

const GITHUB_URL = 'https://github.com/Stoupy51/StewBeet';
const DISCORD_URL = 'https://discord.gg/anxzu6rA9F';
const MARKETPLACE_URL = 'https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet';

const ICON_LINK = 'flex items-center justify-center h-9 px-2 rounded-control text-ink-400 hover:text-ink-50 hover:bg-ink-850 transition-colors';

export const Navbar = memo(() => {
    const prefersReducedMotion = useReducedMotion();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const { language, setLanguage } = useLanguage();
    const { t } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();

    // Ctrl/Cmd+K opens the search from anywhere on the site
    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key.toLowerCase() === 'k' && (event.ctrlKey || event.metaKey)) {
                event.preventDefault();
                setIsSearchOpen(true);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const openSearch = () => {
        setIsSearchOpen(true);
        setIsMobileMenuOpen(false);
    };

    /** Warm the modal chunk and the index, so opening the search feels instant. */
    const prefetchSearch = useCallback(() => {
        import('./SearchModal').catch(() => undefined);
        loadIndex(language).catch(() => undefined);
    }, [language]);

    // Prefetch once the browser is idle, unless the connection asks us not to
    useEffect(() => {
        const connection = (navigator as Navigator & {
            connection?: { saveData?: boolean; effectiveType?: string };
        }).connection;
        if (connection?.saveData || /(^|-)2g$/.test(connection?.effectiveType ?? '')) return;

        if (!window.requestIdleCallback) {
            const timeout = window.setTimeout(prefetchSearch, 2000);
            return () => window.clearTimeout(timeout);
        }
        const handle = window.requestIdleCallback(prefetchSearch, { timeout: 5000 });
        return () => window.cancelIdleCallback(handle);
    }, [prefetchSearch]);

    /**
     * Open a page, or scroll it back to the top when it is the page already showing.
     * Routing to the path you are already on does nothing at all, so the entry read as a dead link.
     */
    const goToPage = useCallback((path: string) => {
        const [pathname, hash] = path.split('#');
        if (location.pathname === pathname) {
            const target = hash ? document.getElementById(hash) : null;
            if (target) target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth' });
            else window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
        } else {
            navigate(path);
        }
        setIsMobileMenuOpen(false);
    }, [location.pathname, navigate, prefersReducedMotion]);

    /** Ctrl, cmd and shift clicks are the visitor asking for a new tab, so the link keeps its href. */
    const openPage = (path: string) => (event: React.MouseEvent) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey) return;
        event.preventDefault();
        goToPage(path);
    };

    const toggleLanguage = () => setLanguage(language === 'en' ? 'fr' : 'en');

    const pages = [
        { label: t('nav.documentation'), path: '/documentation' },
        { label: t('nav.plugins'), path: '/documentation#plugins' },
        { label: t('nav.playground'), path: '/playground' },
        { label: t('nav.tools'), path: '/tools' },
    ];
    const isCurrent = (path: string) => !path.includes('#') && location.pathname === path;

    return (
        <nav className="fixed top-0 inset-x-0 z-50 h-14 bg-ink-950/90 backdrop-blur-md border-b border-ink-800">
            <div className={`${PAGE} h-full flex items-center gap-6`}>
                <a
                    href="/"
                    onClick={openPage('/')}
                    className="flex items-center gap-2.5 text-ink-50 font-semibold tracking-tight flex-shrink-0"
                >
                    <img src="/stewbeet-logo.png" alt="" className="w-7 h-7" />
                    StewBeet
                </a>

                <div className="hidden md:flex items-center gap-1">
                    {pages.map((page) => (
                        <a
                            key={page.path}
                            href={page.path}
                            onClick={openPage(page.path)}
                            aria-current={isCurrent(page.path) ? 'page' : undefined}
                            className={`h-9 flex items-center px-3 rounded-control text-sm transition-colors ${
                                isCurrent(page.path) ? 'text-ink-50 bg-ink-850' : 'text-ink-300 hover:text-ink-50'
                            }`}
                        >
                            {page.label}
                        </a>
                    ))}
                </div>

                <div className="hidden md:flex items-center gap-1 ml-auto">
                    <button
                        onClick={openSearch}
                        onMouseEnter={prefetchSearch}
                        onFocus={prefetchSearch}
                        className="flex items-center gap-2 h-9 pl-2.5 pr-1.5 mr-2 rounded-control border border-ink-800 bg-ink-900 text-sm text-ink-400 hover:text-ink-100 hover:border-ink-600 transition-colors lg:w-52"
                    >
                        <HiSearch aria-hidden="true" />
                        <span>{t('search.button')}</span>
                        <kbd className="ml-auto hidden lg:inline font-mono text-[0.625rem] px-1.5 py-0.5 rounded border border-ink-700 text-ink-400">Ctrl K</kbd>
                    </button>
                    <button
                        onClick={toggleLanguage}
                        aria-label={t('nav.switchLanguage')}
                        title={t('nav.switchLanguage')}
                        className={`${ICON_LINK} font-mono text-xs gap-1`}
                    >
                        <span className={language === 'en' ? 'text-ink-50' : ''}>EN</span>
                        <span className="text-ink-600">/</span>
                        <span className={language === 'fr' ? 'text-ink-50' : ''}>FR</span>
                    </button>
                    <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" aria-label="GitHub" className={`${ICON_LINK} gap-1.5`}>
                        <SiGithub className="w-[18px] h-[18px]" aria-hidden="true" />
                        {stats.stars ? <span className="font-mono text-xs tabular-nums">{stats.stars}</span> : null}
                    </a>
                    <a href={DISCORD_URL} target="_blank" rel="noopener noreferrer" aria-label="Discord" className={ICON_LINK}>
                        <SiDiscord className="w-[18px] h-[18px]" aria-hidden="true" />
                    </a>
                </div>

                <div className="md:hidden flex items-center gap-1 ml-auto">
                    <button onClick={openSearch} aria-label={t('search.button')} className={ICON_LINK}>
                        <HiSearch className="text-xl" />
                    </button>
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        aria-label="Menu"
                        aria-expanded={isMobileMenuOpen}
                        className={ICON_LINK}
                    >
                        {isMobileMenuOpen ? <HiX className="text-xl" /> : <HiMenu className="text-xl" />}
                    </button>
                </div>
            </div>

            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={prefersReducedMotion ? false : { opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }}
                        transition={{ duration: 0.15 }}
                        className="md:hidden bg-ink-950 border-b border-ink-800"
                    >
                        <div className="px-4 py-3 flex flex-col">
                            {pages.map((page) => (
                                <a
                                    key={page.path}
                                    href={page.path}
                                    onClick={openPage(page.path)}
                                    className="py-3 text-ink-200 hover:text-ink-50 border-b border-ink-850"
                                >
                                    {page.label}
                                </a>
                            ))}
                            <div className="pt-3 flex items-center gap-1">
                                <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" aria-label="GitHub" className={ICON_LINK}>
                                    <SiGithub className="w-5 h-5" aria-hidden="true" />
                                </a>
                                <a href={DISCORD_URL} target="_blank" rel="noopener noreferrer" aria-label="Discord" className={ICON_LINK}>
                                    <SiDiscord className="w-5 h-5" aria-hidden="true" />
                                </a>
                                <a href={MARKETPLACE_URL} target="_blank" rel="noopener noreferrer" aria-label="VS Code" className={ICON_LINK}>
                                    <VscodeMark className="w-5 h-5" aria-hidden="true" />
                                </a>
                                <button onClick={toggleLanguage} aria-label={t('nav.switchLanguage')} className={`${ICON_LINK} ml-auto font-mono text-sm gap-1.5`}>
                                    <span className={language === 'en' ? 'text-ink-50' : ''}>EN</span>
                                    <span className="text-ink-600">/</span>
                                    <span className={language === 'fr' ? 'text-ink-50' : ''}>FR</span>
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence>
                {isSearchOpen && (
                    <Suspense fallback={null}>
                        <SearchModal onClose={() => setIsSearchOpen(false)} />
                    </Suspense>
                )}
            </AnimatePresence>
        </nav>
    );
});
Navbar.displayName = 'Navbar';
