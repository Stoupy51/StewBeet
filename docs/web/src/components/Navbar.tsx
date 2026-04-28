import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { HiMenu, HiX } from 'react-icons/hi';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../context/LanguageContext';
import type { Language } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { GRADIENT_TEXT_LOGO, BTN_PRIMARY, NAV_SHADOW, LIST_SELECTED } from '../theme';

export const Navbar: React.FC = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const { language, setLanguage } = useLanguage();
    const { t } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToSection = (id: string) => {
        // First, check if the element exists on the current page
        const element = document.getElementById(id);
        if (element) {
            // Element exists on current page, just scroll to it
            element.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Element doesn't exist, navigate to home page with hash
            window.location.href = `/#${id}`;
        }
        setIsMobileMenuOpen(false);
    };

    const navItems = [
        { label: t('nav.features'), id: 'features' },
        { label: t('nav.installation'), id: 'installation' },
        { label: t('nav.templates'), id: 'templates' },
        { label: t('nav.plugins'), id: 'plugins' },
    ];

    const handleDocumentationClick = (e: React.MouseEvent) => {
        if (e.ctrlKey || e.metaKey || e.shiftKey) {
            return;
        }
        e.preventDefault();
        navigate('/documentation');
        setIsMobileMenuOpen(false);
    };

    const handleToolsClick = (e: React.MouseEvent) => {
        if (e.ctrlKey || e.metaKey || e.shiftKey) {
            return;
        }
        e.preventDefault();
        navigate('/tools');
        setIsMobileMenuOpen(false);
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
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-300 ${isScrolled
                ? `bg-slate-950/95 backdrop-blur-md shadow-lg ${NAV_SHADOW} border-b border-slate-800/70`
                : 'bg-transparent border-b border-transparent'
                }`}
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
                            if (location.pathname === '/') {
                                scrollToSection('hero');
                            } else {
                                navigate('/');
                            }
                        }}
                        className={`flex items-center gap-2 text-xl font-bold ${GRADIENT_TEXT_LOGO} transition-all`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/docs/stewbeet_1024x1024.png" alt="StewBeet" className="w-8 h-8" />
                        StewBeet
                    </motion.a>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-4">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => scrollToSection(item.id)}
                                className="text-slate-300 hover:text-white transition-colors duration-200 text-sm font-medium"
                            >
                                {item.label}
                            </button>
                        ))}
                        
                        <motion.a
                            href="/documentation"
                            onClick={handleDocumentationClick}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white text-sm font-semibold transition-all shadow-lg shadow-purple-500/30"
                        >
                            {t('nav.documentation')}
                        </motion.a>

                        <motion.a
                            href="/tools"
                            onClick={handleToolsClick}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 rounded-lg text-white text-sm font-semibold transition-all shadow-lg shadow-blue-500/30"
                        >
                            {t('nav.tools')}
                        </motion.a>

                        <motion.a
                            href="https://github.com/Stoupy51/StewBeet"
                            target="_blank"
                            rel="noopener noreferrer"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-lg text-white text-sm font-semibold transition-all shadow-lg shadow-indigo-500/30"
                        >
                            GitHub ↗
                        </motion.a>

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

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="md:hidden text-slate-300 hover:text-white transition-colors"
                    >
                        {isMobileMenuOpen ? <HiX className="text-2xl" /> : <HiMenu className="text-2xl" />}
                    </button>
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
                            {navItems.map((item) => (
                                <button
                                    key={item.id}
                                    onClick={() => scrollToSection(item.id)}
                                    className="block w-full text-left text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-lg transition-all"
                                >
                                    {item.label}
                                </button>
                            ))}
                            <a
                                href="/documentation"
                                onClick={handleDocumentationClick}
                                className={`block w-full text-center px-4 py-2 ${BTN_PRIMARY} rounded-lg text-white font-semibold`}
                            >
                                {t('nav.documentation')}
                            </a>
                            <a
                                href="/tools"
                                onClick={handleToolsClick}
                                className={`block w-full text-center px-4 py-2 ${BTN_PRIMARY} rounded-lg text-white font-semibold`}
                            >
                                {t('nav.tools')}
                            </a>
                            <a
                                href="https://github.com/Stoupy51/StewBeet"
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`block w-full text-center px-4 py-2 ${BTN_PRIMARY} rounded-lg text-white font-semibold`}
                            >
                                GitHub ↗
                            </a>

                            {/* Language Selector - Mobile */}
                            <div className="pt-2 border-t border-white/10">
                                <div className="text-xs text-slate-400 mb-2 px-4 font-medium">{t('nav.language')}</div>
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
        </motion.nav>
    );
};
