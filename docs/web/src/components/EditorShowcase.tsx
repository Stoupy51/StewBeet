import { useEffect, useRef } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { HiArrowRight, HiCheck } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { VscodeMark } from './VscodeMark';
import { BTN_SECONDARY, HEADING, ICON_ACCENT, PIXEL_RULE, TEXT_ACCENT_HOVER } from '../theme';

const MARKETPLACE_URL = 'https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet';

export const EditorShowcase: React.FC = () => {
    const { t, language } = useTranslation();
    const motionSafe = useMotionSafe();
    // `useReducedMotion` is null until it has read the media query; treat that as "no preference".
    const prefersReducedMotion = useReducedMotion() === true;
    const videoRef = useRef<HTMLVideoElement>(null);
    const editorDoc = `/markdown?src=${encodeURIComponent(language === 'fr' ? '8_editor/fr.md' : '8_editor/en.md')}`;

    // Clearing `autoplay` on an element that has already begun playing does not stop it, and
    // the preference is only known after the first render, so the pause has to be explicit.
    useEffect(() => {
        if (prefersReducedMotion) videoRef.current?.pause();
    }, [prefersReducedMotion]);

    return (
        <section id="editor" className="py-20 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            {/* The video leads here: the point is what the editor looks like while you type,
                which no amount of prose gets across. */}
            <div className="max-w-6xl mx-auto relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <motion.div
                    {...motionSafe({
                        initial: { scale: 0.96 },
                        whileInView: { scale: 1 },
                        viewport: { once: true },
                        transition: { duration: 0.6, delay: 0.1 },
                    })}
                    className="relative mx-auto w-full max-w-md lg:max-w-none lg:order-first"
                >
                    <video
                        ref={videoRef}
                        className="relative w-full rounded-panel border border-white/10 shadow-2xl"
                        src="/vscode_extension.mp4"
                        autoPlay={!prefersReducedMotion}
                        loop={!prefersReducedMotion}
                        controls
                        muted
                        playsInline
                        preload="auto"
                    >
                        {t('editor.videoFallback')}
                    </video>
                </motion.div>

                <motion.div
                    {...motionSafe({
                        initial: { y: 30 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.6 },
                    })}
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-5 ${HEADING}`}>
                        {t('editor.title')}
                    </h2>
                    <p className="text-slate-400 text-lg leading-relaxed mb-8">
                        {t('editor.description')}
                    </p>

                    <ul className="space-y-3 mb-8">
                        {[t('editor.point1'), t('editor.point2'), t('editor.point3')].map((point) => (
                            <li key={point} className="flex items-start gap-3 text-slate-300">
                                <HiCheck className={`${ICON_ACCENT} flex-shrink-0 mt-1`} />
                                <span>{point}</span>
                            </li>
                        ))}
                    </ul>

                    <div className="flex flex-wrap items-center gap-5">
                        <a
                            href={MARKETPLACE_URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`inline-flex items-center gap-2 px-5 py-3 rounded-panel font-semibold transition-colors ${BTN_SECONDARY}`}
                        >
                            <VscodeMark className="w-5 h-5" aria-hidden="true" />
                            {t('editor.install')}
                        </a>
                        <Link to={editorDoc} className={`inline-flex items-center gap-2 font-medium ${TEXT_ACCENT_HOVER}`}>
                            {t('editor.readMore')}
                            <HiArrowRight />
                        </Link>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
