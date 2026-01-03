import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { HiMenu, HiX } from 'react-icons/hi';
import { motion, AnimatePresence } from 'framer-motion';

export const Navbar: React.FC = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
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
        { label: 'Features', id: 'features' },
        { label: 'Installation', id: 'installation' },
        { label: 'Templates', id: 'templates' },
        { label: 'Plugins', id: 'plugins' },
    ];

    const handleDocumentationClick = (e: React.MouseEvent) => {
        if (e.ctrlKey || e.metaKey || e.shiftKey) {
            return;
        }
        e.preventDefault();
        navigate('/documentation');
        setIsMobileMenuOpen(false);
    };

    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
                ? 'bg-slate-950/95 backdrop-blur-md shadow-lg shadow-indigo-500/10 border-b border-white/5'
                : 'bg-transparent'
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
                        className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-indigo-200 to-purple-200 bg-clip-text text-transparent hover:from-indigo-300 hover:to-purple-300 transition-all"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/docs/stewbeet_1024x1024.png" alt="StewBeet" className="w-8 h-8" />
                        StewBeet
                    </motion.a>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-8">
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
                            Documentation
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
                                className="block w-full text-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg text-white font-semibold"
                            >
                                Documentation
                            </a>
                            <a
                                href="https://github.com/Stoupy51/StewBeet"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block w-full text-center px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg text-white font-semibold"
                            >
                                GitHub ↗
                            </a>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.nav>
    );
};
