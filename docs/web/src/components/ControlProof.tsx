import { Fragment, useState } from 'react';
import { useTranslation } from '../i18n/useTranslation';
import { BLOCK_FILES } from '../heroBuild';
import { DOC_PAGES, docHref } from '../docsPages';
import heroFiles from '../generated/heroFiles.json';

const HIGHLIGHTED: Record<string, string> = heroFiles;
const FIRST_FILE = 'datapack/data/stardust/function/custom_blocks/life_crystal_block/place_secondary.mcfunction';
const HEADCONOMICS_URL = 'https://modrinth.com/datapack/headconomics';
const sourceMaps = DOC_PAGES.find((page) => page.slug === 'plugins/source_maps')!;

/** The block's files as the build wrote them, one at a time: listed on the left of a desktop, as tabs scrolling sideways on a phone. */
const BuiltFiles = () => {
    const { t } = useTranslation();
    const [selected, setSelected] = useState(FIRST_FILE);
    const file = BLOCK_FILES.find(({ path }) => path === selected)!;

    return (
        <div className="min-w-0 self-start bg-code-surface border border-code-border text-code-text lg:grid lg:grid-cols-[16rem_minmax(0,1fr)]">
            <div role="tablist" aria-label={t('control.files')} className="flex lg:flex-col overflow-x-auto border-b lg:border-b-0 lg:border-r border-code-border lg:py-1.5">
                {BLOCK_FILES.map(({ name, path }, index) => {
                    const pack = path!.split('/')[0];
                    return (
                        <Fragment key={path}>
                            {pack !== BLOCK_FILES[index - 1]?.path!.split('/')[0] && (
                                <p className="hidden lg:block px-3.5 pt-2.5 pb-1 font-mono text-[0.6875rem] text-code-text-muted">{pack}/</p>
                            )}
                            <button
                                type="button"
                                role="tab"
                                aria-selected={path === selected}
                                onClick={() => setSelected(path!)}
                                className={`flex-shrink-0 min-h-10 lg:min-h-0 py-1.5 px-3.5 lg:pl-6 text-left font-mono text-xs whitespace-nowrap lg:whitespace-normal lg:[overflow-wrap:anywhere] transition-colors ${
                                    path === selected ? 'bg-code-text/[0.08] text-code-text font-semibold' : 'text-code-text-muted hover:text-code-text'
                                }`}
                            >
                                {name!.split('/').map((part, at, parts) => <Fragment key={at}>{part}{at < parts.length - 1 && <>/<wbr /></>}</Fragment>)}
                            </button>
                        </Fragment>
                    );
                })}
            </div>
            <div className="min-w-0 flex flex-col">
                <p className="flex items-center min-h-10 py-2 px-3.5 border-b border-code-border font-mono text-xs text-code-text-muted break-all">{file.path}</p>
                {file.kind === 'image' ? (
                    // An animated texture is its frames stacked: the square box shows the first
                    <img src={file.url} alt={file.name} width={128} height={128} className="pixelated m-4 w-32 h-32 object-cover object-top" />
                ) : (
                    <div className="hero-code h-[24rem] lg:h-auto lg:grow lg:basis-0 overflow-auto" dangerouslySetInnerHTML={{ __html: HIGHLIGHTED[selected] }} />
                )}
            </div>
        </div>
    );
};

/** The answer to "a pre-compiler takes control away": a user who feared it, beside every file the hero's block became. */
export const ControlProof = () => {
    const { t, language } = useTranslation();
    const translated = t('control.translated');

    return (
        <section className="frame px-4 py-12 lg:px-12 lg:py-16 border-t border-border grid gap-10 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] lg:gap-12">
            <div>
                <h2 className="text-[1.75rem] lg:text-[2.25rem] leading-tight font-bold text-balance">{t('control.title')}</h2>
                <p className="mt-4 text-text-muted text-pretty">
                    {t('control.text').replace('{n}', String(BLOCK_FILES.length))}{' '}
                    <a href={docHref(sourceMaps, language)} className="text-link underline underline-offset-2">{t('control.sourceMaps')}</a>
                </p>
                <figure className="mt-8 pt-5 border-t border-border">
                    <blockquote className="text-[1.0625rem] leading-normal text-pretty">{t('control.racoonQuote')}</blockquote>
                    <figcaption className="mt-3.5 flex items-center gap-2.5 text-sm text-text-muted">
                        <img src="/testimonials/headconomics.webp" alt="" width={36} height={36} className="pixelated w-9 h-9 flex-shrink-0" />
                        <span>
                            <strong className="font-semibold text-text">RacoonJohn</strong>, {t('control.racoonCaption')}{' '}
                            <a href={HEADCONOMICS_URL} target="_blank" rel="noopener noreferrer" className="text-link underline underline-offset-2">Headconomics</a>
                            {translated && <span> ({translated})</span>}
                        </span>
                    </figcaption>
                </figure>
            </div>
            <BuiltFiles />
        </section>
    );
};
