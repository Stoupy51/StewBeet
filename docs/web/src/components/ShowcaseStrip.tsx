import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useInView } from 'framer-motion';
import { HiChevronLeft, HiChevronRight } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { SHOWCASE, TOTAL_BUILT_WITH, type ShowcaseProject } from './builtWithData';

const numberFormat = new Intl.NumberFormat('en-US');

/** A project's pack icon in an inventory slot, or its initial when it has none. */
export const ProjectIcon = ({ project, index = 0 }: { project: ShowcaseProject; index?: number }) => (
    <span className="mc-slot mc-slot-hover flex-shrink-0 w-[4.5rem] h-[4.5rem]">
        {project.icon
            ? <img src={`/showcase/${project.icon}.webp`} alt="" width={64} height={64} loading="lazy" className="slot-fill pixelated w-16 h-16" style={{ '--slot': index } as React.CSSProperties} />
            : <span className="slot-fill font-pixel text-2xl text-white" style={{ '--slot': index } as React.CSSProperties}>{project.name[0]}</span>}
    </span>
);

/** One project: its icon, and how many files the packs measured for it build. */
const ProjectCard = ({ project, index }: { project: ShowcaseProject; index: number }) => {
    const { t } = useTranslation();
    const { stats } = project;

    return (
        <li className="snap-start flex-shrink-0 w-[10.5rem] lg:w-[12rem]">
            <a href={project.url} target="_blank" rel="noopener noreferrer" className="group flex flex-col h-full p-4 border border-border hover:border-ink-600 transition-colors">
                <ProjectIcon project={project} index={index} />
                <span className="mt-3 font-bold group-hover:text-link transition-colors">{project.name}</span>
                <span className="text-sm text-text-muted">
                    {project.owner}{project.community && <span className="text-generated">, {t('builtWith.community')}</span>}
                </span>
                {stats && (
                    <span className="mt-2 text-[0.8125rem] leading-snug text-text-muted">
                        {t('builtWith.filesFrom')
                            .replace('{files}', numberFormat.format(stats.functions + stats.jsonFiles + stats.textures))
                            .replace('{lines}', numberFormat.format(stats.sourceLines))}
                    </span>
                )}
            </a>
        </li>
    );
};

/** Every public project built with StewBeet, as a strip a reader swipes or steps through, never moving on its own. */
export const ShowcaseStrip = () => {
    const { t } = useTranslation();
    const strip = useRef<HTMLUListElement>(null);
    const inView = useInView(strip, { once: true, amount: 0.3 });
    // Armed after hydration, so the prerendered page and a visitor without JavaScript see every slot filled
    useEffect(() => strip.current?.setAttribute('data-armed', ''), []);
    const step = (direction: 1 | -1) => strip.current?.scrollBy({ left: direction * strip.current.clientWidth * 0.8, behavior: 'smooth' });
    const arrow = 'hidden md:flex items-center justify-center w-11 h-11 border border-border hover:border-ink-600 transition-colors active:scale-[0.98]';

    return (
        <section id="built-with" className="frame px-4 py-12 lg:px-12 lg:py-16 border-t border-border scroll-mt-14">
            <div className="flex items-end justify-between gap-6">
                <div>
                    <h2 className="text-[1.75rem] lg:text-[2.25rem] leading-tight font-bold text-balance">{t('builtWith.title').replace('{n}', String(TOTAL_BUILT_WITH))}</h2>
                    <p className="mt-4 text-text-muted text-pretty">
                        {t('builtWith.subtitle')}{' '}
                        <Link to="/showcase" className="text-link underline underline-offset-2">{t('builtWith.seeAll')}</Link>
                    </p>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                    <button type="button" onClick={() => step(-1)} aria-label={t('builtWith.previous')} className={arrow}><HiChevronLeft aria-hidden="true" /></button>
                    <button type="button" onClick={() => step(1)} aria-label={t('builtWith.next')} className={arrow}><HiChevronRight aria-hidden="true" /></button>
                </div>
            </div>
            <ul ref={strip} data-play={inView ? '' : undefined} className="mt-8 -mx-4 px-4 lg:-mx-12 lg:px-12 flex gap-3 overflow-x-auto snap-x snap-mandatory scroll-px-4 lg:scroll-px-12 pb-2 custom-scrollbar">
                {SHOWCASE.map((project, index) => <ProjectCard key={project.url} project={project} index={index} />)}
            </ul>
        </section>
    );
};
