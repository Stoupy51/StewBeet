import { motion } from 'framer-motion';
import { HiOutlineExclamationCircle } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { ALERT_ACCENT, HEADING, PIXEL_RULE } from '../theme';

/**
 * The page explained what the framework does and showed the output, but never what was
 * wrong with the alternative — so a visitor who has not personally suffered hand-written
 * mcfunction had no reason to care. This section is the only place on the site written in
 * the maintainer's voice, and it carries the honest limitations, which is the part readers
 * quote to other people.
 */
export const WhyStewBeet: React.FC = () => {
    const { t } = useTranslation();
    const motionSafe = useMotionSafe();

    const painPoints = [t('why.pain1'), t('why.pain2'), t('why.pain3')];

    return (
        <section id="why" className="py-20 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            {/* Outer container matches the neighbouring sections so the left edge lines up;
                the inner column keeps the prose at a readable measure. */}
            <div className="max-w-6xl mx-auto relative z-10">
                <motion.div
                    className="max-w-3xl"
                    {...motionSafe({
                        initial: { y: 24 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.5 },
                    })}
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-6 ${HEADING}`}>{t('why.title')}</h2>

                    <p className="text-lg text-slate-300 leading-relaxed mb-6">{t('why.intro')}</p>

                    <ul className="space-y-3 mb-6">
                        {painPoints.map((point) => (
                            <li key={point} className="flex gap-3 text-slate-300 leading-relaxed">
                                <span className="text-mc-copper font-mono flex-shrink-0" aria-hidden="true">—</span>
                                <span>{point}</span>
                            </li>
                        ))}
                    </ul>

                    <p className="text-lg text-slate-300 leading-relaxed mb-10">{t('why.resolution')}</p>

                    <div className={`rounded-panel p-6 ${ALERT_ACCENT}`}>
                        <div className="flex items-start gap-3">
                            <HiOutlineExclamationCircle className="text-mc-copper text-xl flex-shrink-0 mt-0.5" aria-hidden="true" />
                            <div>
                                <h3 className="font-semibold text-slate-100 mb-2">{t('why.limitsTitle')}</h3>
                                <p className="text-slate-300 text-sm leading-relaxed">{t('why.limitsBody')}</p>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
