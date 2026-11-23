import { useEffect, useRef } from 'react';
import { useInView } from 'framer-motion';
import { useTranslation } from '../i18n/useTranslation';
import { BY_HAND } from './gainsData';
import gainsCode from '../generated/gainsCode.json';

const CODE: Record<string, string> = gainsCode;

const CodePanel = ({ title, code, wrap = false }: { title: string; code: string; wrap?: boolean }) => (
    <div className="min-w-0 bg-code-surface border border-code-border text-code-text">
        <p className="flex items-center min-h-9 py-1.5 px-3.5 border-b border-code-border font-mono text-xs text-code-text-muted">{title}</p>
        <div className={`hero-code ${wrap ? 'gains-wrap' : 'gains-scroll'}`} dangerouslySetInnerHTML={{ __html: CODE[code] }} />
    </div>
);

/** The eight files of one hand-written block are struck through, and the definition that replaces them drops in. */
const Comparison = () => {
    const { t } = useTranslation();
    const frame = useRef<HTMLDivElement>(null);
    const inView = useInView(frame, { once: true, amount: 0.5 });
    // Armed after hydration, so the prerendered page and a visitor without JavaScript see the last frame
    useEffect(() => frame.current?.setAttribute('data-armed', ''), []);

    return (
        <div ref={frame} data-play={inView ? '' : undefined} className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] lg:gap-10 items-start">
            <div>
                <p className="font-pixel text-[0.8125rem] text-text-muted">{t('gains.byHand')}</p>
                <ul className="mt-3 border-t border-border font-mono text-xs">
                    {BY_HAND.map(({ path, role }, index) => (
                        <li key={path} className="strike-row flex items-baseline justify-between gap-3 py-2 border-b border-border" style={{ '--row': index } as React.CSSProperties}>
                            <span className="truncate">{path}</span>
                            <span className="flex-shrink-0 text-text-muted">{role}</span>
                        </li>
                    ))}
                </ul>
            </div>
            <div className="gains-drop">
                <p className="font-pixel text-[0.8125rem] text-generated">{t('gains.withStewbeet')}</p>
                <p className="mt-3 flex items-baseline gap-3">
                    <span className="font-pixel text-5xl leading-none text-generated">1</span>
                    <span className="text-text-muted">{t('gains.withUnit')}</span>
                </p>
                <p className="mt-4 text-pretty">{t('gains.withNote')}</p>
            </div>
        </div>
    );
};

/** What one definition saves: the eight files of a block, then two things a datapack rarely gets by hand. */
export const Gains = () => {
    const { t } = useTranslation();

    return (
        <section id="features" className="frame px-4 py-12 lg:px-12 lg:py-16 border-t border-border scroll-mt-14">
            <h2 className="text-[1.75rem] lg:text-[2.25rem] leading-tight font-bold text-balance">{t('gains.title')}</h2>
            <p className="mt-4 max-w-[40rem] text-text-muted text-pretty">{t('gains.lead')}</p>
            <Comparison />

            <div className="mt-12 grid gap-10 lg:grid-cols-2 lg:gap-12">
                <div className="min-w-0">
                    <h3 className="text-xl font-bold">{t('gains.materialsTitle')}</h3>
                    <p className="mt-2 text-text-muted text-pretty">{t('gains.materialsText')}</p>
                    <div className="mt-4">
                        <CodePanel title="definitions/additions/common.py" code="materials" />
                    </div>
                    <img src="/img/material_tier.png" alt={t('gains.materialsAlt')} width={928} height={120} loading="lazy" className="pixelated mt-3 w-full h-auto" />
                </div>
                <div className="min-w-0">
                    <h3 className="text-xl font-bold">{t('gains.langTitle')}</h3>
                    <p className="mt-2 text-text-muted text-pretty">{t('gains.langText')}</p>
                    <div className="mt-4 flex flex-col gap-3">
                        <CodePanel title={t('gains.langBefore')} code="langBefore" wrap />
                        <CodePanel title={t('gains.langAfter')} code="langAfter" wrap />
                        <CodePanel title="assets/minecraft/lang/en_us.json" code="langFile" wrap />
                    </div>
                </div>
            </div>
        </section>
    );
};
