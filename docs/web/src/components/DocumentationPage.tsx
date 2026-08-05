import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { PluginsTable } from './PluginsTable';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { HEADING, HOVER_CARD, CARD_HOVER_TEXT, CARD_HOVER_ARROW } from '../theme';

interface DocItem {
    title: string;
    description: string;
    pathEn: string;
    pathFr: string;
    iconImg?: string;
}

/** A titled band of the index, so the shape of the documentation is visible at a glance. */
interface DocGroup {
    title: string;
    description: string;
    items: DocItem[];
}

export const DocumentationPage: React.FC = () => {
    const { t, language } = useTranslation();
    const motionSafe = useMotionSafe();
    const location = useLocation();

    // #plugins used to live on the landing page; it now resolves here
    useEffect(() => {
        if (!location.hash) return;
        const element = document.querySelector(location.hash);
        if (element) {
            setTimeout(() => element.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
        }
    }, [location]);

    // Grouped by what the reader is doing, not by the order the files happen to sit in.
    // A flat list of eight peers gives someone arriving with a goal nothing to aim at.
    const groups: DocGroup[] = [
        {
            title: t('documentation.groupStart'),
            description: t('documentation.groupStartDesc'),
            items: [
                {
                    title: t('documentation.gettingStarted'),
                    description: t('documentation.gettingStartedDesc'),
                    pathEn: '0_getting_started/en.md',
                    pathFr: '0_getting_started/fr.md',
                },
            ],
        },
        {
            title: t('documentation.groupGuides'),
            description: t('documentation.groupGuidesDesc'),
            items: [
                {
                    title: t('documentation.definitionsSetup'),
                    description: t('documentation.definitionsSetupDesc'),
                    pathEn: '1_definitions_setup/en.md',
                    pathFr: '1_definitions_setup/fr.md',
                },
                {
                    title: t('documentation.writingToFiles'),
                    description: t('documentation.writingToFilesDesc'),
                    pathEn: '2_writing_to_files/en.md',
                    pathFr: '2_writing_to_files/fr.md',
                },
                {
                    title: t('documentation.beetConfig'),
                    description: t('documentation.beetConfigDesc'),
                    iconImg: 'https://raw.githubusercontent.com/mcbeet/beet/refs/heads/main/logo.png',
                    pathEn: '3_beet_config/en.md',
                    pathFr: '3_beet_config/fr.md',
                },
                {
                    title: t('documentation.dependencies'),
                    description: t('documentation.dependenciesDesc'),
                    pathEn: '5_dependencies/en.md',
                    pathFr: '5_dependencies/fr.md',
                },
                {
                    title: t('documentation.ingameManual'),
                    description: t('documentation.ingameManualDesc'),
                    pathEn: '7_ingame_manual/en.md',
                    pathFr: '7_ingame_manual/fr.md',
                },
                {
                    title: t('documentation.continuousDelivery'),
                    description: t('documentation.continuousDeliveryDesc'),
                    pathEn: '6_continuous_delivery/en.md',
                    pathFr: '6_continuous_delivery/fr.md',
                },
            ],
        },
        {
            title: t('documentation.groupReference'),
            description: t('documentation.groupReferenceDesc'),
            items: [
                {
                    title: t('documentation.equations'),
                    description: t('documentation.equationsDesc'),
                    pathEn: '4_equations/en.md',
                    pathFr: '4_equations/fr.md',
                },
            ],
        },
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100">
            <Navbar />

            {/* Hero Section */}
            <div className="relative z-10 pt-32 pb-16 px-4">
                <div className="max-w-7xl mx-auto text-center">
                    <motion.h1
                        {...motionSafe({
                            initial: { y: 20 },
                            animate: { y: 0 },
                        })}
                        className="text-5xl md:text-6xl font-bold mb-6"
                    >
                        📖 <span className={HEADING}>{t('documentation.title')}</span>
                    </motion.h1>
                    <motion.p
                        {...motionSafe({
                            initial: { y: 20 },
                            animate: { y: 0 },
                            transition: { delay: 0.1 },
                        })}
                        className="text-xl text-slate-300 max-w-3xl mx-auto"
                    >
                        {t('documentation.subtitle')}
                    </motion.p>
                </div>
            </div>

            {/* Documentation List */}
            <div className="relative z-10 pb-20 px-4">
                <div className="max-w-4xl mx-auto space-y-14">
                    {groups.map((group, groupIndex) => (
                        <section key={group.title}>
                            <div className="mb-5">
                                <h2 className="text-sm font-mono uppercase tracking-wider text-mc-emerald mb-1">
                                    {group.title}
                                </h2>
                                <p className="text-slate-400 text-sm">{group.description}</p>
                            </div>

                            <div className={group.items.length === 1 ? '' : 'grid grid-cols-1 md:grid-cols-2 gap-4'}>
                                {group.items.map((doc, index) => (
                                    <motion.div
                                        key={doc.pathEn}
                                        {...motionSafe({
                                            initial: { y: 20 },
                                            animate: { y: 0 },
                                            transition: { delay: 0.1 + groupIndex * 0.05 + index * 0.05 },
                                        })}
                                    >
                                        <Link
                                            to={`/markdown?src=${encodeURIComponent(language === 'fr' ? doc.pathFr : doc.pathEn)}`}
                                            className="block group h-full"
                                        >
                                            <div className={`bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-panel p-6 ${HOVER_CARD} transition-all hover:bg-slate-900/50 h-full`}>
                                                <div className="flex items-start justify-between gap-4 h-full">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-3 mb-2">
                                                            {doc.iconImg && (
                                                                <img src={doc.iconImg} alt="" className="w-7 h-7 object-contain flex-shrink-0" />
                                                            )}
                                                            <h3 className={`text-xl font-bold text-slate-100 ${CARD_HOVER_TEXT}`}>
                                                                {doc.title}
                                                            </h3>
                                                        </div>
                                                        <p className="text-slate-400 leading-relaxed">
                                                            {doc.description}
                                                        </p>
                                                    </div>
                                                    <HiArrowRight className={CARD_HOVER_ARROW} />
                                                </div>
                                            </div>
                                        </Link>
                                    </motion.div>
                                ))}
                            </div>
                        </section>
                    ))}

                    <p className="text-slate-400 text-sm text-center">
                        {t('documentation.comingSoon')}
                    </p>
                </div>
            </div>

            {/* Plugins Section */}
            <div id="plugins" className="relative z-10 pb-20 px-4">
                <div className="max-w-7xl mx-auto">
                    <motion.div
                        {...motionSafe({
                            initial: { y: 30 },
                            whileInView: { y: 0 },
                            viewport: { once: true },
                            transition: { duration: 0.6 },
                        })}
                        className="text-center mb-16"
                    >
                        <h2 className={`text-4xl md:text-5xl font-bold mb-4 ${HEADING}`}>
                            {t('documentation.plugins')}
                        </h2>
                        <p className="text-slate-400 text-lg max-w-3xl mx-auto mb-8">
                            {t('showcase.subtitle')}<br />
                            <span className="text-sm">{t('showcase.legend')} <span className="text-red-400">🔴 {t('showcase.fullyDependent')}</span> <span className="text-yellow-400 ml-2">🟡 {t('showcase.partlyDependent')}</span> <span className="text-green-400 ml-2">🟢 {t('showcase.independent')}</span></span>
                        </p>
                    </motion.div>

                    <PluginsTable />
                </div>
            </div>

            <Footer />
        </div>
    );
};
