import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { HiArrowRight } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { HEADING, PIXEL_RULE, TEXT_ACCENT_HOVER } from '../theme';
import { LibraryPills } from './LibraryPills';
import { AUTO_LIBRARIES, DEPENDENCIES_DOC, GIANTS, type Giant } from './giantsData';

/**
 * The section that credits what the framework runs on.
 *
 * It sits right after the packs built with StewBeet, because both answer the same question
 * from opposite ends: one shows who trusts the framework, this one shows what the framework
 * itself trusts. Rows rather than cards, one line each: the paragraphs are on /credits, and
 * a second wall of panels this far down the page is what a visitor scrolls past.
 */

const GiantRow = ({ giant }: { giant: Giant }) => {
    const { t } = useTranslation();

    return (
        <a
            href={giant.links[0].url}
            target="_blank"
            rel="noopener noreferrer"
            className="group block border-l-2 border-white/10 hover:border-mc-emerald/60 pl-4 py-1 transition-colors"
        >
            <div className="flex items-baseline gap-2">
                <span className="font-semibold text-slate-100 group-hover:text-mc-emerald transition-colors">
                    {giant.name}
                </span>
                <span className="text-xs font-mono text-slate-500">{giant.owner}</span>
            </div>
            <p className="text-sm text-slate-400 leading-snug">{t(giant.roleKey)}</p>
        </a>
    );
};

export const StandingOnGiants: React.FC = () => {
    const { t, language } = useTranslation();
    const motionSafe = useMotionSafe();

    return (
        <section id="standing-on-giants" className="py-14 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            <div className="max-w-6xl mx-auto relative z-10">
                <motion.div
                    {...motionSafe({
                        initial: { y: 30 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.6 },
                    })}
                    className="mb-8 max-w-2xl"
                >
                    <h2 className={`text-2xl md:text-3xl font-bold mb-3 ${HEADING}`}>{t('giants.title')}</h2>
                    <p className="text-slate-300">{t('giants.subtitle')}</p>
                </motion.div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-5">
                    {GIANTS.map((giant) => (
                        <GiantRow key={giant.name} giant={giant} />
                    ))}
                </div>

                <div className="mt-10 pt-6 border-t border-white/10">
                    <p className="text-sm text-slate-400 mb-4">{t('giants.autoNote')}</p>
                    <LibraryPills entries={AUTO_LIBRARIES} />
                </div>

                <div className="mt-6 flex flex-wrap items-center gap-x-8 gap-y-2">
                    <Link
                        to="/credits"
                        className={`group inline-flex items-center gap-2 text-sm ${TEXT_ACCENT_HOVER} underline-offset-4 hover:underline`}
                    >
                        {t('giants.readCredits')}
                        <HiArrowRight className="group-hover:translate-x-1 transition-transform" aria-hidden="true" />
                    </Link>
                    <Link
                        to={`/markdown?src=${encodeURIComponent(DEPENDENCIES_DOC[language])}`}
                        className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors underline-offset-4 hover:underline"
                    >
                        {t('giants.readDocs')}
                    </Link>
                </div>
            </div>
        </section>
    );
};
