import { useState, useEffect, useCallback, memo, lazy, Suspense } from 'react';
import { flushSync } from 'react-dom';
import { useNavigate, useLocation } from 'react-router-dom';
import { HiDesktopComputer, HiMenu, HiMoon, HiSearch, HiSun, HiX } from 'react-icons/hi';
import { SiDiscord, SiGithub } from 'react-icons/si';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { useLanguage, type Language } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { useTheme, type ThemePreference } from '../hooks/useTheme';
import { loadIndex } from '../utils/search';
import { readingPosition, restoreReadingPosition, withViewTransition } from '../utils/pageTransition';
import { VscodeMark } from './VscodeMark';
import stats from '../generated/stats.json';

const SearchModal = lazy(() => import('./SearchModal').then(m => ({ default: m.SearchModal })));

const GITHUB_URL = 'https://github.com/Stoupy51/StewBeet';
const DISCORD_URL = 'https://discord.gg/anxzu6rA9F';
const MARKETPLACE_URL = 'https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet';

const ICON_BUTTON = 'flex items-center justify-center min-w-11 h-11 px-2 text-text-muted hover:text-text transition-colors';

/** Each click moves to the next preference, looping back to the system one. */
const THEME_STEPS = {
    system: { next: 'light', Icon: HiDesktopComputer, labelKey: 'nav.themeSystem' },
    light:  { next: 'dark',   Icon: HiSun,             labelKey: 'nav.themeLight' },
    dark:   { next: 'system', Icon: HiMoon,            labelKey: 'nav.themeDark' },
} as const satisfies Record<ThemePreference, { next: ThemePreference; Icon: React.ComponentType<{ className?: string }>; labelKey: string }>;

/** Routes that light up each entry of the navigation. Showcase has no page of its own yet. */
const SECTIONS = [
    { key: 'nav.documentation', path: '/docs', routes: ['/docs', '/fr/docs'] },
    { key: 'nav.showcase', path: '/showcase', routes: ['/showcase'] },
    { key: 'nav.tools', path: '/tools', routes: ['/tools'] },
];

/** Past this much scrolling down, a doc page on a phone gives the header's height back to the text. */
const HIDE_AFTER_PX = 56;

const ThemeButton = ({ className }: { className: string }) => {
    const { t } = useTranslation();
    const { preference, setPreference } = useTheme();
    const { next, Icon, labelKey } = THEME_STEPS[preference];
    return (
        <button onClick={() => setPreference(next)} aria-label={t(labelKey)} title={t(labelKey)} className={className}>
            <Icon className="w-[18px] h-[18px]" aria-hidden="true" />
        </button>
    );
};

/** True while the reader scrolls down, false as soon as they scroll back up. */
function useScrollingDown(enabled: boolean): boolean {
    const [down, setDown] = useState(false);

    useEffect(() => {
        if (!enabled) return;
        let last = window.scrollY;
        const onScroll = () => {
            const y = window.scrollY;
            if (Math.abs(y - last) < 8) return;
            setDown(y > last && y > HIDE_AFTER_PX);
            last = y;
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => window.removeEventListener('scroll', onScroll);
    }, [enabled]);

    return enabled && down;
}

/**
 * The site header, fixed at the top: 56 px on a phone, 64 px from 1024 px.
 *
 * `subbar` is a doc page's 48 px bar, shown under the header below 1024 px. With one, the header
 * slides away while the reader scrolls down and the bar takes its place at the top.
 *
 * A language change crossfades the page and keeps the reader in the same section. A page that has
 * to load its text in the other language first passes `onLanguageChange` to do it all itself.
 */
export const Navbar = memo(({ subbar, onLanguageChange }: { subbar?: React.ReactNode; onLanguageChange?: (language: Language) => void }) => {
    const prefersReducedMotion = useReducedMotion();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const { language, setLanguage } = useLanguage();
    const { t } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();
    const hidden = useScrollingDown(subbar !== undefined) && !isMobileMenuOpen;

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

    const toggleLanguage = () => {
        const next = language === 'en' ? 'fr' : 'en';
        if (onLanguageChange) return onLanguageChange(next);
        const position = readingPosition();
        withViewTransition('language', () => {
            flushSync(() => setLanguage(next));
            restoreReadingPosition(position);
        });
    };
    const isCurrent = (routes: string[]) => routes.some((route) => location.pathname === route || location.pathname.startsWith(`${route}/`));

    const languageLabel = (
        <span className="font-mono text-xs">
            <span className={language === 'en' ? 'text-text' : ''}>EN</span>
            <span className="px-1 text-ink-600">/</span>
            <span className={language === 'fr' ? 'text-text' : ''}>FR</span>
        </span>
    );

    return (
        <>
            <div className={`site-header fixed top-0 inset-x-0 z-50 transition-transform duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] ${hidden ? '-translate-y-14 lg:translate-y-0' : ''}`}>
                <header className="h-14 lg:h-16 bg-surface border-b border-border">
                    <nav aria-label={t('nav.main')} className="h-full flex items-center gap-1 pl-4 pr-1.5 lg:px-7">
                        <a
                            href="/"
                            onClick={openPage('/')}
                            className="flex items-center gap-2.5 mr-auto lg:mr-5 h-11 text-text text-lg lg:text-[1.1875rem] font-bold flex-shrink-0"
                        >
                            <img src="/stewbeet-logo.png" alt="" width={32} height={32} className="pixelated w-7 h-7 lg:w-8 lg:h-8" />
                            StewBeet
                        </a>

                        <div className="hidden lg:flex items-center mr-auto">
                            {SECTIONS.map((section) => (
                                <a
                                    key={section.key}
                                    href={section.path}
                                    onClick={openPage(section.path)}
                                    aria-current={isCurrent(section.routes) ? 'page' : undefined}
                                    className={`h-11 flex items-center px-3 text-[0.9375rem] transition-colors ${
                                        isCurrent(section.routes) ? 'text-text font-bold' : 'text-text-muted font-medium hover:text-text'
                                    }`}
                                >
                                    {t(section.key)}
                                </a>
                            ))}
                        </div>

                        <button
                            onClick={openSearch}
                            onMouseEnter={prefetchSearch}
                            onFocus={prefetchSearch}
                            className="hidden lg:flex items-center gap-2.5 w-60 h-10 px-2.5 mr-2 border border-border text-sm text-text-muted hover:text-text hover:border-ink-600 transition-colors"
                        >
                            <HiSearch className="w-4 h-4" aria-hidden="true" />
                            <span className="flex-1 text-left">{t('search.button')}</span>
                            <kbd className="font-mono text-[0.6875rem] px-1.5 py-0.5 border border-border">Ctrl K</kbd>
                        </button>
                        <button onClick={openSearch} aria-label={t('search.button')} className={`lg:hidden ${ICON_BUTTON} text-text`}>
                            <HiSearch className="w-5 h-5" aria-hidden="true" />
                        </button>

                        <div className="hidden lg:flex items-center">
                            <ThemeButton className={ICON_BUTTON} />
                            <button onClick={toggleLanguage} aria-label={t('nav.switchLanguage')} title={t('nav.switchLanguage')} className={ICON_BUTTON}>
                                {languageLabel}
                            </button>
                            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" aria-label="GitHub" className={`${ICON_BUTTON} gap-1.5`}>
                                <SiGithub className="w-[18px] h-[18px]" aria-hidden="true" />
                                {stats.stars ? <span className="font-mono text-xs tabular-nums">{stats.stars}</span> : null}
                            </a>
                            <a href={DISCORD_URL} target="_blank" rel="noopener noreferrer" aria-label="Discord" className={ICON_BUTTON}>
                                <SiDiscord className="w-[18px] h-[18px]" aria-hidden="true" />
                            </a>
                        </div>

                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            aria-label={t('nav.menu')}
                            aria-expanded={isMobileMenuOpen}
                            className={`lg:hidden ${ICON_BUTTON} text-text`}
                        >
                            {isMobileMenuOpen ? <HiX className="w-5 h-5" aria-hidden="true" /> : <HiMenu className="w-5 h-5" aria-hidden="true" />}
                        </button>
                    </nav>
                </header>

                {subbar && <div className="lg:hidden">{subbar}</div>}

                <AnimatePresence>
                    {isMobileMenuOpen && (
                        <motion.div
                            initial={prefersReducedMotion ? false : { opacity: 0, y: -8 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }}
                            transition={{ duration: 0.15 }}
                            className="lg:hidden absolute inset-x-0 top-14 bg-surface border-b border-border"
                        >
                            <div className="px-4 pt-2 pb-3 flex flex-col">
                                {SECTIONS.map((section) => (
                                    <a
                                        key={section.key}
                                        href={section.path}
                                        onClick={openPage(section.path)}
                                        aria-current={isCurrent(section.routes) ? 'page' : undefined}
                                        className={`h-12 flex items-center text-base border-b border-border ${isCurrent(section.routes) ? 'font-bold text-text' : 'text-text'}`}
                                    >
                                        {t(section.key)}
                                    </a>
                                ))}
                                <div className="pt-2 flex items-center -ml-2">
                                    <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" aria-label="GitHub" className={`${ICON_BUTTON} gap-1.5`}>
                                        <SiGithub className="w-5 h-5" aria-hidden="true" />
                                        {stats.stars ? <span className="font-mono text-xs tabular-nums">{stats.stars}</span> : null}
                                    </a>
                                    <a href={DISCORD_URL} target="_blank" rel="noopener noreferrer" aria-label="Discord" className={ICON_BUTTON}>
                                        <SiDiscord className="w-5 h-5" aria-hidden="true" />
                                    </a>
                                    <a href={MARKETPLACE_URL} target="_blank" rel="noopener noreferrer" aria-label="VS Code" className={ICON_BUTTON}>
                                        <VscodeMark className="w-5 h-5" aria-hidden="true" />
                                    </a>
                                    <ThemeButton className={`${ICON_BUTTON} ml-auto`} />
                                    <button onClick={toggleLanguage} aria-label={t('nav.switchLanguage')} className={ICON_BUTTON}>
                                        {languageLabel}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Outside the sliding header: a transformed ancestor would carry the fixed modal along with it. */}
            <AnimatePresence>
                {isSearchOpen && (
                    <Suspense fallback={null}>
                        <SearchModal onClose={() => setIsSearchOpen(false)} />
                    </Suspense>
                )}
            </AnimatePresence>
        </>
    );
});
Navbar.displayName = 'Navbar';
