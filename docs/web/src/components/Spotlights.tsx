import { useEffect, useRef } from 'react';
import { useReducedMotion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { DOC_PAGES, docHref } from '../docsPages';
import { useTranslation } from '../i18n/useTranslation';
import { VscodeMark } from './VscodeMark';

const MARKETPLACE_URL = 'https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet';
const docPage = (slug: string) => DOC_PAGES.find((page) => page.slug === slug)!;

interface SpotlightProps {
    /** Translation namespace holding title, description and videoFallback. */
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
        <div id={ns} className="frame px-4 py-12 lg:px-12 lg:py-16 border-t border-border scroll-mt-14 grid gap-8 lg:grid-cols-2 lg:gap-12 items-center">
            <div className={videoFirst ? 'lg:order-last' : ''}>
                <h2 className="text-[1.75rem] lg:text-[2.25rem] leading-tight font-bold text-balance">{t(`${ns}.title`)}</h2>
                <p className="mt-4 text-text-muted text-pretty">{t(`${ns}.description`)}</p>
                <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3">{children}</div>
            </div>
            <div className={`${frame} border border-border overflow-hidden`}>
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

/** The two things StewBeet does beyond writing files, each shown as a video beside its pitch. */
export const Spotlights = () => {
    const { t, language } = useTranslation();
    const link = 'text-link underline underline-offset-2';

    return (
        <>
            {/* Portrait clip (574x686): capped in width so it does not tower over its text. */}
            <Spotlight ns="manual" video="/ingame_manual.mp4" poster="/ingame_manual_poster.jpg" frame="w-full max-w-[26rem] mx-auto aspect-[574/686]">
                <Link to={docHref(docPage('manual'), language)} className={link}>{t('manual.readMore')}</Link>
            </Spotlight>
            <Spotlight ns="editor" video="/vscode_extension.mp4" poster="/vscode_extension_poster.jpg" frame="w-full aspect-[960/598]" videoFirst>
                <a href={MARKETPLACE_URL} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 h-11 px-4 border border-border hover:border-ink-600 font-semibold transition-colors active:scale-[0.98]">
                    <VscodeMark className="w-5 h-5" aria-hidden="true" />
                    {t('editor.install')}
                </a>
                <Link to={docHref(docPage('editor'), language)} className={link}>{t('editor.readMore')}</Link>
            </Spotlight>
        </>
    );
};
