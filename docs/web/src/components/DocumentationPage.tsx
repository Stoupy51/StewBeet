import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiDocumentText, HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { PluginsTable } from './PluginsTable';
import { useTranslation } from '../i18n/useTranslation';

interface DocItem {
    title: string;
    description: string;
    pathEn: string;
    pathFr: string;
    icon?: string;
}

export const DocumentationPage: React.FC = () => {
    const { t, language } = useTranslation();

    const docs: DocItem[] = [
        {
            title: `🚀 ${t('documentation.gettingStarted')}`,
            description: t('documentation.gettingStartedDesc'),
            pathEn: '0_getting_started/en.md',
            pathFr: '0_getting_started/fr.md',
        },
        {
            title: `📚 ${t('documentation.definitionsSetup')}`,
            description: t('documentation.definitionsSetupDesc'),
            pathEn: '1_definitions_setup/en.md',
            pathFr: '1_definitions_setup/fr.md',
        },
        {
            title: `📝 ${t('documentation.writingToFiles')}`,
            description: t('documentation.writingToFilesDesc'),
            pathEn: '2_writing_to_files/en.md',
            pathFr: '2_writing_to_files/fr.md',
        },
        {
            title: `⚙️ ${t('documentation.beetConfig')}`,
            description: t('documentation.beetConfigDesc'),
            pathEn: '3_beet_config/en.md',
            pathFr: '3_beet_config/fr.md',
        },
        {
            title: `⚡ ${t('documentation.equations')}`,
            description: t('documentation.equationsDesc'),
            pathEn: '4_equations/en.md',
            pathFr: '4_equations/fr.md',
        },
        {
            title: `📦 ${t('documentation.dependencies')}`,
            description: t('documentation.dependenciesDesc'),
            pathEn: '5_dependencies/en.md',
            pathFr: '5_dependencies/fr.md',
        },
        {
            title: `🚀 ${t('documentation.continuousDelivery')}`,
            description: t('documentation.continuousDeliveryDesc'),
            pathEn: '6_continuous_delivery/en.md',
            pathFr: '6_continuous_delivery/fr.md',
        },
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100">
            <Navbar />

            {/* Background decoration */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-20 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px]" />
            </div>

            {/* Hero Section */}
            <div className="relative z-10 pt-32 pb-16 px-4">
                <div className="max-w-7xl mx-auto text-center">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-5xl md:text-6xl font-bold mb-6"
                    >
                        📖 <span className="bg-gradient-to-r from-indigo-200 via-purple-200 to-pink-200 bg-clip-text text-transparent">{t('documentation.title')}</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-slate-300 max-w-3xl mx-auto"
                    >
                        {t('documentation.subtitle')}
                    </motion.p>
                </div>
            </div>

            {/* Documentation List */}
            <div className="relative z-10 pb-20 px-4">
                <div className="max-w-4xl mx-auto">
                    <div className="space-y-4">
                        {/* Getting Started - Full Width */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                        >
                            <Link
                                to={`/markdown?src=${encodeURIComponent(language === 'fr' ? docs[0].pathFr : docs[0].pathEn)}`}
                                className="block group"
                            >
                                <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-indigo-500/50 transition-all hover:bg-slate-900/50 hover:shadow-lg hover:shadow-indigo-500/10">
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <HiDocumentText className="text-2xl text-indigo-400" />
                                                <h2 className="text-2xl font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                                                    {docs[0].title}
                                                </h2>
                                            </div>
                                            <p className="text-slate-400 leading-relaxed">
                                                {docs[0].description}
                                            </p>
                                        </div>
                                        <HiArrowRight className="text-2xl text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
                                    </div>
                                </div>
                            </Link>
                        </motion.div>

                        {/* Remaining docs - 2-column grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {docs.slice(1).map((doc, index) => (
                                <motion.div
                                    key={language === 'fr' ? doc.pathFr : doc.pathEn}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.3 + index * 0.1 }}
                                >
                                    <Link
                                        to={`/markdown?src=${encodeURIComponent(language === 'fr' ? doc.pathFr : doc.pathEn)}`}
                                        className="block group h-full"
                                    >
                                        <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-indigo-500/50 transition-all hover:bg-slate-900/50 hover:shadow-lg hover:shadow-indigo-500/10 h-full">
                                            <div className="flex items-start justify-between gap-4 h-full">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-3 mb-2">
                                                        <HiDocumentText className="text-2xl text-indigo-400" />
                                                        <h2 className="text-2xl font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                                                            {doc.title}
                                                        </h2>
                                                    </div>
                                                    <p className="text-slate-400 leading-relaxed">
                                                        {doc.description}
                                                    </p>
                                                </div>
                                                <HiArrowRight className="text-2xl text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
                                            </div>
                                        </div>
                                    </Link>
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    {/* Coming Soon Section */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="mt-12 text-center"
                    >
                        <p className="text-slate-500 text-sm">
                            More documentation coming soon...
                        </p>
                    </motion.div>
                </div>
            </div>

            {/* Plugins Section */}
            <div id="plugins" className="relative z-10 pb-20 px-4">
                <div className="max-w-7xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-purple-200">
                            {t('documentation.plugins')}
                        </h2>
                        <p className="text-slate-400 text-lg max-w-3xl mx-auto mb-8">
                            {t('documentation.pluginsSubtitle')}<br />
                            <span className="text-sm">Legend: <span className="text-red-400">🔴 Fully dependent</span> <span className="text-yellow-400 ml-2">🟡 Partly dependent</span> <span className="text-green-400 ml-2">🟢 Independent</span></span>
                        </p>
                    </motion.div>

                    <PluginsTable />
                </div>
            </div>

            <Footer />
        </div>
    );
};
