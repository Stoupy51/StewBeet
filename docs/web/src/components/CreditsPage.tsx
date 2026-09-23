import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiArrowLeft, HiExternalLink } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { PageHeader } from './PageHeader';
import { LibraryPills } from './LibraryPills';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { HEADING, HOVER_CARD, SELECTION_BRAND, TEXT_ACCENT_HOVER } from '../theme';
import { AUTO_LIBRARIES, BOOKSHELF_MODULE_COUNT, COMPATIBILITIES, DEPENDENCIES_DOC, GIANTS } from './giantsData';

/**
 * The long form of the home page's Standing on Giants section.
 *
 * One card per project, in the same order, with the paragraph the section only had room to
 * summarise in a line. Nothing here is generated: when a dependency is added to OFFICIAL_LIBS,
 * this page is where it gets its name in print.
 */
export const CreditsPage: React.FC = () => {
    const { t, language } = useTranslation();
    const motionSafe = useMotionSafe();

    return (
        <div className={`min-h-screen bg-ink-950 text-ink-100 ${SELECTION_BRAND}`}>
            <Navbar />

            <main>
                <PageHeader eyebrow={t('credits.eyebrow')} title={t('credits.title')} lead={t('credits.subtitle')} width="max-w-3xl" />

                <div className="relative z-10 pb-12 px-4">
                    <div className="max-w-3xl mx-auto space-y-3">
                        {GIANTS.map((giant, index) => (
                            <motion.article
                                key={giant.name}
                                {...motionSafe({
                                    initial: { y: 20 },
                                    animate: { y: 0 },
                                    transition: { delay: 0.15 + index * 0.05 },
                                })}
                                className={`rounded-panel border border-ink-800 bg-ink-900/40 p-5 transition-all ${HOVER_CARD}`}
                            >
                                <div className="flex items-baseline justify-between gap-4 mb-2">
                                    <h2 className="text-lg font-semibold text-ink-50">{giant.name}</h2>
                                    <span className="text-xs font-mono text-ink-400 flex-shrink-0">{giant.owner}</span>
                                </div>

                                {/* Only the Bookshelf paragraph carries {n}; the others pass through untouched */}
                                <p className="text-sm text-ink-300 leading-relaxed">
                                    {t(giant.bodyKey).replace('{n}', String(BOOKSHELF_MODULE_COUNT))}
                                </p>

                                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3">
                                    {giant.links.map((link) => (
                                        <a
                                            key={link.url}
                                            href={link.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className={`inline-flex items-center gap-1 text-xs font-mono ${TEXT_ACCENT_HOVER}`}
                                        >
                                            {link.label}
                                            <HiExternalLink className="text-[0.875em]" aria-hidden="true" />
                                        </a>
                                    ))}
                                </div>
                            </motion.article>
                        ))}
                    </div>
                </div>

                <div className="relative z-10 pb-20 px-4">
                    <div className="max-w-3xl mx-auto pt-6 border-t border-ink-800">
                        <h2 className={`text-xl font-semibold mb-2 ${HEADING}`}>{t('credits.librariesTitle')}</h2>
                        <p className="text-sm text-ink-400 mb-4">{t('credits.librariesNote')}</p>
                        <LibraryPills entries={AUTO_LIBRARIES} />

                        <h2 className={`text-xl font-semibold mt-10 mb-2 ${HEADING}`}>{t('credits.compatTitle')}</h2>
                        <p className="text-sm text-ink-400 mb-4">{t('credits.compatNote')}</p>
                        <LibraryPills entries={COMPATIBILITIES} />

                        <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-3">
                            <Link
                                to={`/markdown?src=${encodeURIComponent(DEPENDENCIES_DOC[language])}`}
                                className={`inline-flex items-center gap-2 text-sm ${TEXT_ACCENT_HOVER} underline-offset-4 hover:underline`}
                            >
                                {t('credits.docsLink')}
                            </Link>
                            <Link
                                to="/#standing-on-giants"
                                className="group inline-flex items-center gap-2 text-sm text-ink-400 hover:text-white transition-colors"
                            >
                                <HiArrowLeft className="group-hover:-translate-x-1 transition-transform" aria-hidden="true" />
                                {t('credits.backHome')}
                            </Link>
                        </div>
                    </div>
                </div>
            </main>

            <Footer />
        </div>
    );
};
