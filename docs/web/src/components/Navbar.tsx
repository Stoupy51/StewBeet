import { useState, useEffect, useCallback, memo, lazy, Suspense } from 'react';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { useNavigate, useLocation } from 'react-router-dom';
import { HiMenu, HiSearch, HiX } from 'react-icons/hi';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { useLanguage } from '../context/LanguageContext';
import type { Language } from '../context/LanguageContext';
import { loadIndex } from '../utils/search';
import { LOGO_TEXT, BTN_PRIMARY, NAV_SHADOW, LIST_SELECTED } from '../theme';

const SearchModal = lazy(() => import('./SearchModal').then(m => ({ default: m.SearchModal })));

export const Navbar = memo(() => {
    const motionSafe = useMotionSafe();
    const prefersReducedMotion = useReducedMotion();
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const { language, setLanguage } = useLanguage();
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

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

    const scrollToSection = (id: string, homePath = '/') => {
        // First, check if the element exists on the current page
        const element = document.getElementById(id);
        if (element) {
            // Element exists on current page, just scroll to it
            element.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Element doesn't exist, navigate to the page that owns the section
            window.location.href = `${homePath}#${id}`;
        }
        setIsMobileMenuOpen(false);
    };

    // Scrolling the page one moment and leaving it the next looked identical, so the two
    // kinds of destination sit in separate groups with a rule between them.
    const pageSections = [
        { label: 'Features', id: 'features', homePath: '/' },
        { label: 'Installation', id: 'installation', homePath: '/' },
        { label: 'Templates', id: 'templates', homePath: '/' },
    ];

    /**
     * Open a page, or scroll it back to the top when it is the page already showing.
     * Routing to the path you are already on does nothing at all, so the entry read as a dead link.
     */
    const goToPage = useCallback((path: string) => {
        if (location.pathname === path) {
            window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
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

    const handlePluginsClick = (e: React.MouseEvent) => {
        if (e.ctrlKey || e.metaKey || e.shiftKey) {
            return;
        }
        e.preventDefault();
        scrollToSection('plugins', '/documentation');
    };

    const handleLanguageChange = (lang: Language) => {
        setLanguage(lang);
        setIsLanguageMenuOpen(false);
    };

    const languageOptions = {
        en: { label: 'English', flag: '🇬🇧' },
        fr: { label: 'Français', flag: '🇫🇷' }
    };

    return (
        <motion.nav
            {...motionSafe({ initial: { y: -100 }, animate: { y: 0 } })}
            /* The bar used to be transparent until the first scroll, so it dissolved into the
               hero and the nav items read as loose words floating over the headline. It now
               always sits on its own surface; scrolling only deepens the shadow. */
            className={`fixed top-0 left-0 right-0 z-50 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/70 transition-shadow duration-300 ${isScrolled ? `shadow-lg ${NAV_SHADOW}` : ''
                }`}
        >
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <motion.a
                        href="/"
                        onClick={(e) => {
                            // Allow ctrl/cmd+click and middle click to open in new tab
                            if (e.ctrlKey || e.metaKey || e.shiftKey) {
                                return;
                            }
                            e.preventDefault();
                            goToPage('/');
                        }}
                        className={`flex items-center gap-2 text-xl font-bold ${LOGO_TEXT} transition-all`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <img src="/stewbeet-logo.png" alt="StewBeet" className="w-8 h-8" />
                        StewBeet
                    </motion.a>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-3">
                        {pageSections.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => scrollToSection(item.id, item.homePath)}
                                className="text-slate-300 hover:text-white transition-colors duration-200 text-sm font-medium"
                            >
                                {item.label}
                            </button>
                        ))}

                        <span className="w-px h-5 bg-white/15" aria-hidden="true" />

                        <a
                            href="/documentation#plugins"
                            onClick={handlePluginsClick}
                            className="text-slate-300 hover:text-white transition-colors duration-200 text-sm font-medium"
                        >
                            Plugins
                        </a>
                        <a
                            href="/tools"
                            onClick={openPage('/tools')}
                            className="text-slate-300 hover:text-white transition-colors duration-200 text-sm font-medium"
                        >
                            Tools
                        </a>

                        <span className="w-px h-5 bg-white/15" aria-hidden="true" />

                        <a
                            href="https://discord.gg/anxzu6rA9F"
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="Discord"
                            className="flex items-center justify-center w-9 h-9 rounded-panel text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
                        >
                            <span className="w-5 h-5 flex items-center">
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" /></svg>
                            </span>
                        </a>
                        <a
                            href="https://github.com/Stoupy51/StewBeet"
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="GitHub"
                            className="flex items-center justify-center w-9 h-9 rounded-panel text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
                        >
                            <span className="w-5 h-5 flex items-center">
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" /></svg>
                            </span>
                        </a>

                        <span className="w-px h-5 bg-white/15" aria-hidden="true" />

                        <button
                            onClick={openSearch}
                            onMouseEnter={prefetchSearch}
                            onFocus={prefetchSearch}
                            className="flex items-center gap-2 pl-3 pr-2 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-slate-300 hover:text-white text-sm font-medium transition-colors border border-white/10"
                        >
                            <HiSearch className="text-lg" />
                            <span>Search</span>
                            <kbd className="hidden lg:inline px-1.5 py-0.5 rounded bg-white/10 text-[10px] text-slate-400 border border-white/10">Ctrl K</kbd>
                        </button>
                        <a
                            href="/documentation"
                            onClick={openPage('/documentation')}
                            className="px-4 py-2 bg-mc-emerald hover:bg-mc-diamond rounded-panel text-slate-950 text-sm font-semibold transition-colors"
                        >
                            Documentation
                        </a>

                        <span className="w-px h-5 bg-white/15" aria-hidden="true" />

                        {/* Language Selector - Desktop */}
                        <div className="relative">
                            <motion.button
                                onClick={() => setIsLanguageMenuOpen(!isLanguageMenuOpen)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-slate-300 hover:text-white text-sm font-medium transition-all border border-white/10"
                            >
                                <span>{languageOptions[language].flag}</span>
                                <span>{languageOptions[language].label}</span>
                            </motion.button>

                            <AnimatePresence>
                                {isLanguageMenuOpen && (
                                    <>
                                        <div
                                            className="fixed inset-0 z-40"
                                            onClick={() => setIsLanguageMenuOpen(false)}
                                        />
                                        <motion.div
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: -10 }}
                                            transition={{ duration: 0.2 }}
                                            className="absolute right-0 mt-2 w-48 bg-slate-800/95 backdrop-blur-md border border-white/10 rounded-lg shadow-xl overflow-hidden z-50"
                                        >
                                            {(Object.entries(languageOptions) as [Language, typeof languageOptions.en][]).map(([lang, option]) => (
                                                <button
                                                    key={lang}
                                                    onClick={() => handleLanguageChange(lang)}
                                                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                                                        language === lang
                                                            ? LIST_SELECTED
                                                            : 'text-slate-300 hover:bg-white/5 hover:text-white'
                                                    }`}
                                                >
                                                    <span className="text-xl">{option.flag}</span>
                                                    <span className="text-sm font-medium">{option.label}</span>
                                                </button>
                                            ))}
                                        </motion.div>
                                    </>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>

                    {/* Mobile Search + Menu Buttons */}
                    <div className="md:hidden flex items-center gap-3">
                        <button
                            onClick={openSearch}
                            aria-label="Search"
                            className="text-slate-300 hover:text-white transition-colors"
                        >
                            <HiSearch className="text-2xl" />
                        </button>
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="text-slate-300 hover:text-white transition-colors"
                        >
                            {isMobileMenuOpen ? <HiX className="text-2xl" /> : <HiMenu className="text-2xl" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden bg-slate-900/95 backdrop-blur-md border-t border-white/5"
                    >
                        <div className="px-4 py-4 space-y-3">
                            <button
                                onClick={openSearch}
                                className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-slate-300 hover:text-white font-medium transition-all border border-white/10"
                            >
                                <HiSearch className="text-lg" />
                                Search
                            </button>
                            {pageSections.map((item) => (
                                <button
                                    key={item.id}
                                    onClick={() => scrollToSection(item.id, item.homePath)}
                                    className="block w-full text-left text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-lg transition-all"
                                >
                                    {item.label}
                                </button>
                            ))}
                            <a
                                href="/documentation"
                                onClick={openPage('/documentation')}
                                className={`block w-full text-center px-4 py-2 ${BTN_PRIMARY} rounded-lg text-white font-semibold`}
                            >
                                Documentation
                            </a>
                            <a
                                href="/tools"
                                onClick={openPage('/tools')}
                                className={`block w-full text-center px-4 py-2 ${BTN_PRIMARY} rounded-lg text-white font-semibold`}
                            >
                                Tools
                            </a>
                            <a
                                href="https://discord.gg/anxzu6rA9F"
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`flex items-center justify-center gap-2 block w-full text-center px-4 py-2 ${BTN_PRIMARY} rounded-lg text-white font-semibold`}
                            >
                                <span className="w-5 h-5 flex items-center">
                                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" /></svg>
                                </span>
                                Discord
                            </a>
                            <a
                                href="https://github.com/Stoupy51/StewBeet"
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`flex items-center justify-center gap-2 block w-full text-center px-4 py-2 ${BTN_PRIMARY} rounded-lg text-white font-semibold`}
                            >
                                <span className="w-5 h-5 flex items-center">
                                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" /></svg>
                                </span>
                                GitHub
                            </a>

                            {/* Language Selector - Mobile */}
                            <div className="pt-2 border-t border-white/10">
                                <div className="text-xs text-slate-400 mb-2 px-4 font-medium">Language</div>
                                <div className="space-y-1">
                                    {(Object.entries(languageOptions) as [Language, typeof languageOptions.en][]).map(([lang, option]) => (
                                        <button
                                            key={lang}
                                            onClick={() => handleLanguageChange(lang)}
                                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all ${
                                                language === lang
                                                    ? LIST_SELECTED
                                                    : 'text-slate-300 hover:bg-white/5 hover:text-white'
                                            }`}
                                        >
                                            <span className="text-xl">{option.flag}</span>
                                            <span className="text-sm font-medium">{option.label}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Search overlay */}
            <AnimatePresence>
                {isSearchOpen && (
                    <Suspense fallback={null}>
                        <SearchModal onClose={() => setIsSearchOpen(false)} />
                    </Suspense>
                )}
            </AnimatePresence>
        </motion.nav>
    );
});
Navbar.displayName = 'Navbar';
