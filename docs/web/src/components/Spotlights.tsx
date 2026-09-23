import { useEffect, useRef } from 'react';
import { useReducedMotion } from 'framer-motion';
import { HiArrowRight, HiCheck } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { VscodeMark } from './VscodeMark';
import { BTN_SECONDARY, EYEBROW, PAGE, SECTION_LEAD, SECTION_TITLE, TEXT_ACCENT_HOVER } from '../theme';

const MARKETPLACE_URL = 'https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet';

/**
 * The two things StewBeet does beyond writing files, each shown as a video beside its pitch.
 * They alternate sides so the page does not read as a column of identical blocks.
 */

interface SpotlightProps {
    /** Translation namespace holding eyebrow, title, description, point1 to point3 and videoFallback. */
    ns: 'manual' | 'editor';
    video: string;
    poster: string;
    /** Size and aspect ratio of the frame, matching the video so it shows without bars. */
    frame: string;
    /** Puts the video on the left from lg up. */
    videoFirst?: boolean;
    children: React.ReactNode;
}

/**
 * A looping video is motion the visitor did not ask for, so controls are always present and the
 * reduced-motion preference suppresses playback entirely. Clearing `autoplay` on an element that
 * already started does not stop it, and the preference is only known after the first render, so
 * the pause is explicit.
 */
const Spotlight = ({ ns, video, poster, frame, videoFirst = false, children }: SpotlightProps) => {
    const { t } = useTranslation();
    // `useReducedMotion` is null until it has read the media query; treat that as "no preference".
    const prefersReducedMotion = useReducedMotion() === true;
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        if (prefersReducedMotion) videoRef.current?.pause();
    }, [prefersReducedMotion]);

    return (
        <div id={ns} data-rise className="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center scroll-mt-20">
            <div className={videoFirst ? 'lg:order-last' : ''}>
                <p className={EYEBROW}>{t(`${ns}.eyebrow`)}</p>
                <h2 className={`mt-4 ${SECTION_TITLE}`}>{t(`${ns}.title`)}</h2>
                <p className={`mt-4 ${SECTION_LEAD}`}>{t(`${ns}.description`)}</p>
                <ul className="mt-6 space-y-2.5">
                    {[1, 2, 3].map((index) => (
                        <li key={index} className="flex items-start gap-3 text-ink-200">
                            <HiCheck className="text-leaf-400 flex-shrink-0 mt-1" aria-hidden="true" />
                            <span>{t(`${ns}.point${index}`)}</span>
                        </li>
                    ))}
                </ul>
                <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-3">{children}</div>
            </div>

            <div className={`${frame} rounded-panel border border-ink-800 bg-ink-900 overflow-hidden`}>
                <video
                    ref={videoRef}
                    className="w-full h-full object-contain"
                    src={video}
                    poster={poster}
                    autoPlay={!prefersReducedMotion}
                    loop={!prefersReducedMotion}
                    controls
                    muted
                    playsInline
                    preload="metadata"
                >
                    {t(`${ns}.videoFallback`)}
                </video>
            </div>
        </div>
    );
};

export const Spotlights: React.FC = () => {
    const { t, language } = useTranslation();
    const doc = (path: string) => `/markdown?src=${encodeURIComponent(`${path}/${language === 'fr' ? 'fr' : 'en'}.md`)}`;

    return (
        <section className="py-20 md:py-28 border-t border-ink-800">
            <div className={`${PAGE} space-y-16 md:space-y-20`}>
                {/* Portrait clip (574x686): capped in width so it does not tower over its text. */}
                <Spotlight ns="manual" video="/ingame_manual.mp4" poster="/ingame_manual_poster.jpg" frame="w-full max-w-[26rem] mx-auto aspect-[574/686]">
                    <Link to={doc('7_ingame_manual')} className={`inline-flex items-center gap-2 font-medium ${TEXT_ACCENT_HOVER}`}>
                        {t('manual.readMore')}
                        <HiArrowRight aria-hidden="true" />
                    </Link>
                </Spotlight>

                <Spotlight ns="editor" video="/vscode_extension.mp4" poster="/vscode_extension_poster.jpg" frame="w-full aspect-[960/598]" videoFirst>
                    <a href={MARKETPLACE_URL} target="_blank" rel="noopener noreferrer" className={`${BTN_SECONDARY} h-11 px-4`}>
                        <VscodeMark className="w-5 h-5" aria-hidden="true" />
                        {t('editor.install')}
                    </a>
                    <Link to={doc('8_editor')} className={`inline-flex items-center gap-2 font-medium ${TEXT_ACCENT_HOVER}`}>
                        {t('editor.readMore')}
                        <HiArrowRight aria-hidden="true" />
                    </Link>
                </Spotlight>
            </div>
        </section>
    );
};
