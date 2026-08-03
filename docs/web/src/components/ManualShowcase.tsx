import { motion } from 'framer-motion';
import { HiArrowRight, HiCheck } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { GLOW_PRIMARY, GLOW_SECONDARY, GRADIENT_TEXT, ICON_ACCENT, TEXT_ACCENT_HOVER } from '../theme';

export const ManualShowcase: React.FC = () => {
    const { t, language } = useTranslation();
    const manualDoc = `/markdown?src=${encodeURIComponent(language === 'fr' ? '7_ingame_manual/fr.md' : '7_ingame_manual/en.md')}`;

    return (
        <section id="manual" className="py-20 px-4 relative overflow-hidden bg-gradient-to-b from-slate-950 to-slate-900">
            <div className="absolute inset-0 overflow-hidden">
                <div className={`absolute top-1/4 -left-40 w-80 h-80 ${GLOW_PRIMARY} rounded-full blur-[100px]`} />
                <div className={`absolute bottom-1/4 -right-40 w-80 h-80 ${GLOW_SECONDARY} rounded-full blur-[100px]`} />
            </div>

            <div className="max-w-6xl mx-auto relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-5 ${GRADIENT_TEXT}`}>
                        {t('manual.title')}
                    </h2>
                    <p className="text-slate-400 text-lg leading-relaxed mb-8">
                        {t('manual.description')}
                    </p>

                    <ul className="space-y-3 mb-8">
                        {[t('manual.point1'), t('manual.point2'), t('manual.point3')].map((point) => (
                            <li key={point} className="flex items-start gap-3 text-slate-300">
                                <HiCheck className={`${ICON_ACCENT} flex-shrink-0 mt-1`} />
                                <span>{point}</span>
                            </li>
                        ))}
                    </ul>

                    <Link to={manualDoc} className={`inline-flex items-center gap-2 font-medium ${TEXT_ACCENT_HOVER}`}>
                        {t('manual.readMore')}
                        <HiArrowRight />
                    </Link>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.96 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="relative mx-auto w-full max-w-sm"
                >
                    <div className="absolute -inset-3 bg-gradient-to-br from-indigo-500/20 to-purple-600/20 rounded-2xl blur-[32px]" />
                    <video
                        className="relative w-full rounded-xl border border-white/10 shadow-2xl"
                        src="/ingame_manual.mp4"
                        poster="/ingame_manual_poster.jpg"
                        autoPlay
                        loop
                        muted
                        playsInline
                        preload="metadata"
                    >
                        {t('manual.videoFallback')}
                    </video>
                </motion.div>
            </div>
        </section>
    );
};
