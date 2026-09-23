import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { DependencyMark, PluginsTable } from './PluginsTable';
import { useTranslation } from '../i18n/useTranslation';
import { CARD, CARD_HOVER_ARROW, CARD_HOVER_TEXT, EYEBROW, HOVER_CARD, PAGE, SECTION_LEAD, SECTION_TITLE } from '../theme';

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
                    title: t('documentation.quickstart'),
                    description: t('documentation.quickstartDesc'),
                    pathEn: 'quickstart/en.md',
                    pathFr: 'quickstart/fr.md',
                },
                {
                    title: t('documentation.gettingStarted'),
                    description: t('documentation.gettingStartedDesc'),
                    pathEn: '0_getting_started/en.md',
                    pathFr: '0_getting_started/fr.md',
                },
                {
                    title: t('documentation.editorSupport'),
                    description: t('documentation.editorSupportDesc'),
                    pathEn: '8_editor/en.md',
                    pathFr: '8_editor/fr.md',
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
                    title: t('documentation.cookbook'),
                    description: t('documentation.cookbookDesc'),
                    pathEn: '2_writing_to_files/cookbook/en.md',
                    pathFr: '2_writing_to_files/cookbook/fr.md',
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
                    title: t('documentation.helperReference'),
                    description: t('documentation.helperReferenceDesc'),
                    pathEn: '2_writing_to_files/reference/en.md',
                    pathFr: '2_writing_to_files/reference/fr.md',
                },
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
        <div className="min-h-screen bg-ink-950 text-ink-200">
            <Navbar />

            <header className={`${PAGE} pt-28 md:pt-32 pb-12`}>
                <p className={EYEBROW}>{t('documentation.eyebrow')}</p>
                <h1 className="mt-4 text-4xl md:text-5xl font-semibold tracking-tight text-ink-50">{t('documentation.title')}</h1>
                <p className={`mt-4 max-w-2xl ${SECTION_LEAD}`}>{t('documentation.subtitle')}</p>
            </header>

            <div className={`${PAGE} pb-20 space-y-14`}>
                {groups.map((group) => (
                    <section key={group.title} className="grid grid-cols-1 lg:grid-cols-[16rem_minmax(0,1fr)] gap-4 lg:gap-12 pt-8 border-t border-ink-800">
                        <div>
                            <h2 className="text-lg font-semibold tracking-tight text-ink-50">{group.title}</h2>
                            <p className="mt-1 text-sm text-ink-400 leading-relaxed">{group.description}</p>
                        </div>

                        <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {group.items.map((doc) => (
                                <li key={doc.pathEn}>
                                    <Link
                                        to={`/markdown?src=${encodeURIComponent(language === 'fr' ? doc.pathFr : doc.pathEn)}`}
                                        className={`group flex items-start justify-between gap-4 h-full p-5 ${CARD} ${HOVER_CARD}`}
                                    >
                                        <div>
                                            <div className="flex items-center gap-2.5">
                                                {doc.iconImg && <img src={doc.iconImg} alt="" className="w-5 h-5 object-contain flex-shrink-0" />}
                                                <h3 className={`font-semibold text-ink-50 ${CARD_HOVER_TEXT}`}>{doc.title}</h3>
                                            </div>
                                            <p className="mt-1.5 text-sm text-ink-400 leading-relaxed">{doc.description}</p>
                                        </div>
                                        <HiArrowRight className={CARD_HOVER_ARROW} aria-hidden="true" />
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </section>
                ))}

                <p className="text-ink-500 text-sm">{t('documentation.comingSoon')}</p>
            </div>

            <section id="plugins" className="border-t border-ink-800 scroll-mt-14">
                <div className={`${PAGE} py-20`}>
                    <div className="max-w-3xl mb-10">
                        <p className={EYEBROW}>{t('documentation.pluginsEyebrow')}</p>
                        <h2 className={`mt-4 ${SECTION_TITLE}`}>{t('documentation.plugins')}</h2>
                        <p className={`mt-4 ${SECTION_LEAD}`}>{t('showcase.subtitle')}</p>
                        <p className="mt-4 flex flex-wrap gap-x-5 gap-y-1 text-sm text-ink-400">
                            <span>{t('showcase.legend')}</span>
                            <DependencyMark level="full" />
                            <DependencyMark level="partial" />
                            <DependencyMark level="none" />
                        </p>
                    </div>

                    <PluginsTable />
                </div>
            </section>

            <Footer />
        </div>
    );
};
