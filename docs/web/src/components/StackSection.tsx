import { useEffect, useMemo, useRef } from 'react';
import { useInView } from 'framer-motion';
import { useTranslation } from '../i18n/useTranslation';
import { STACK_PALETTES, stackDiagramSvg } from './stackDiagram';
import { CARD, PAGE, SECTION_LEAD, SECTION_TITLE, TEXT_ACCENT_HOVER } from '../theme';

/**
 * Where StewBeet sits among beet, bolt and mecha, and who makes each one.
 * Near the bottom of the page: a visitor who reached it has seen what StewBeet does and may now
 * wonder what the other three names are. The files it links are written by scripts/build-stack-diagram.ts.
 */
export const StackSection: React.FC = () => {
    const { t, language } = useTranslation();
    const frame = useRef<HTMLDivElement>(null);
    const inView = useInView(frame, { once: true, amount: 0.4 });
    // Armed after hydration, so the prerendered page and a visitor without JavaScript see the diagram finished
    useEffect(() => frame.current?.setAttribute('data-armed', ''), []);

    const svg = useMemo(() => stackDiagramSvg({ language, palette: STACK_PALETTES.page, autoplay: false }), [language]);
    const file = (theme: 'dark' | 'light', extension: 'png' | 'svg') => `/img/stack/stewbeet-stack.${language}.${theme}.${extension}`;

    return (
        <section id="stack" className="py-14 md:py-28 border-t border-ink-800 scroll-mt-14">
            <div className={PAGE}>
                <div data-rise className="max-w-3xl">
                    <h2 className={SECTION_TITLE}>{t('stack.title')}</h2>
                    <p className={`mt-4 ${SECTION_LEAD}`}>{t('stack.lead')}</p>
                </div>

                <div
                    ref={frame}
                    data-play={inView ? '' : undefined}
                    className={`${CARD} mt-10 overflow-hidden [&>svg]:block [&>svg]:w-full [&>svg]:h-auto`}
                    dangerouslySetInnerHTML={{ __html: svg }}
                />

                <p className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-ink-400">
                    <span>{t('stack.share')}</span>
                    {(['dark', 'light'] as const).map((theme) => (
                        <span key={theme} className="flex gap-3">
                            <a href={file(theme, 'png')} download className={TEXT_ACCENT_HOVER}>PNG, {t(`stack.${theme}`)}</a>
                            <a href={file(theme, 'svg')} target="_blank" rel="noopener noreferrer" className={TEXT_ACCENT_HOVER}>
                                SVG, {t(`stack.${theme}`)}, {t('stack.svgHint')}
                            </a>
                        </span>
                    ))}
                </p>
            </div>
        </section>
    );
};
