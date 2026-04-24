import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { useTranslation } from '../i18n/useTranslation';

interface ToolItem {
    title: string;
    description: string;
    path: string;
    icon: string;
}

export const ToolsPage: React.FC = () => {
    const { t } = useTranslation();

    const tools: ToolItem[] = [
        {
            title: t('tools.markdownToBBCode'),
            description: t('tools.markdownToBBCodeDesc'),
            path: '/markdown_to_pmc_bbcode',
            icon: '🔄',
        },
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100">
            <Navbar />

            {/* Background decoration */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-20 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px]" />
            </div>

            {/* Hero Section */}
            <div className="relative z-10 pt-32 pb-16 px-4">
                <div className="max-w-7xl mx-auto text-center">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-5xl md:text-6xl font-bold mb-6"
                    >
                        🛠️ <span className="bg-gradient-to-r from-blue-200 via-cyan-200 to-teal-200 bg-clip-text text-transparent">{t('tools.title')}</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-slate-300 max-w-3xl mx-auto"
                    >
                        {t('tools.subtitle')}
                    </motion.p>
                </div>
            </div>

            {/* Tools List */}
            <div className="relative z-10 pb-20 px-4">
                <div className="max-w-4xl mx-auto">
                    <div className="space-y-4">
                        {tools.map((tool, index) => (
                            <motion.div
                                key={tool.path}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 + index * 0.1 }}
                            >
                                <Link to={tool.path} className="block group">
                                    <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-blue-500/50 transition-all hover:bg-slate-900/50 hover:shadow-lg hover:shadow-blue-500/10">
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className="text-2xl">{tool.icon}</span>
                                                    <h2 className="text-2xl font-bold text-slate-100 group-hover:text-blue-300 transition-colors">
                                                        {tool.title}
                                                    </h2>
                                                </div>
                                                <p className="text-slate-400 leading-relaxed">
                                                    {tool.description}
                                                </p>
                                            </div>
                                            <HiArrowRight className="text-2xl text-slate-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
                                        </div>
                                    </div>
                                </Link>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    );
};
