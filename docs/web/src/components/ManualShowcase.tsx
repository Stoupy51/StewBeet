import { useEffect, useRef } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { HiArrowRight, HiCheck } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { HEADING, ICON_ACCENT, PIXEL_RULE, TEXT_ACCENT_HOVER } from '../theme';

export const ManualShowcase: React.FC = () => {
    const { t, language } = useTranslation();
    const motionSafe = useMotionSafe();
    // `useReducedMotion` is null until it has read the media query; treat that as "no preference".
    const prefersReducedMotion = useReducedMotion() === true;
    const videoRef = useRef<HTMLVideoElement>(null);
    const manualDoc = `/markdown?src=${encodeURIComponent(language === 'fr' ? '7_ingame_manual/fr.md' : '7_ingame_manual/en.md')}`;

    // Clearing `autoplay` on an element that has already begun playing does not stop it, and
    // the preference is only known after the first render, so the pause has to be explicit.
    useEffect(() => {
        if (prefersReducedMotion) videoRef.current?.pause();
    }, [prefersReducedMotion]);

    return (
        <section id="manual" className="py-20 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            <div className="max-w-6xl mx-auto relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <motion.div
                    {...motionSafe({
                        initial: { y: 30 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.6 },
                    })}
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-5 ${HEADING}`}>
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
                    {...motionSafe({
                        initial: { scale: 0.96 },
                        whileInView: { scale: 1 },
                        viewport: { once: true },
                        transition: { duration: 0.6, delay: 0.1 },
                    })}
                    className="relative mx-auto w-full max-w-md lg:max-w-none"
                >
                    {/* A looping autoplay video is motion the visitor did not ask for. Controls
                        are always present: an autoplaying video the viewer cannot stop is the
                        case NN/g singles out. And the preference suppresses playback entirely. */}
                    <video
                        ref={videoRef}
                        className="relative w-full rounded-panel border border-white/10 shadow-2xl"
                        src="/ingame_manual.mp4"
                        poster="/ingame_manual_poster.jpg"
                        autoPlay={!prefersReducedMotion}
                        loop={!prefersReducedMotion}
                        controls
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
