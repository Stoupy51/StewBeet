import { useTranslation } from '../i18n/useTranslation';
import { FLAGSHIPS, TOTAL_BUILT_WITH, type Flagship } from './builtWithData';

const numberFormat = new Intl.NumberFormat('en-US');

/** One flagship pack: every item it holds, what it costs to write beside what it produces. */
const FlagshipCard = ({ project }: { project: Flagship }) => {
    const { t } = useTranslation();
    const outputs: [number, string][] = [
        [project.functions, t('builtWith.unitFunctions')],
        [project.jsonFiles, t('builtWith.unitJson')],
        [project.textures, t('builtWith.unitTextures')],
    ];

    // The pack points at Modrinth, where a player installs it; a separate link keeps the source reachable.
    return (
        <article className="min-w-0 border border-border">
            <a href={project.modrinth} target="_blank" rel="noopener noreferrer" className="block border-b border-border">
                <img src={project.image} alt={t('builtWith.itemsAlt').replace('{project}', project.name)} loading="lazy" decoding="async" className="w-full h-48 object-cover object-top" />
            </a>
            <div className="p-4 lg:p-5">
                <p className="flex items-baseline justify-between gap-3">
                    <a href={project.modrinth} target="_blank" rel="noopener noreferrer" className="text-lg font-bold hover:text-link transition-colors">{project.name}</a>
                    <a href={project.url} target="_blank" rel="noopener noreferrer" className="font-mono text-xs text-text-muted hover:text-text transition-colors">{t('builtWith.sourceLink')}</a>
                </p>
                <p className="mt-1.5 text-[0.9375rem] text-text-muted text-pretty">{t(project.descriptionKey)}</p>
                <p className="mt-4 text-[0.9375rem]">
                    <span className="font-pixel">{numberFormat.format(project.sourceLines)}</span> <span className="text-text-muted">{t('builtWith.unitSourceLines')}</span>
                </p>
                <dl className="mt-2 grid grid-cols-3 gap-2 text-[0.9375rem]">
                    {outputs.map(([count, unit]) => (
                        <div key={unit}>
                            <dt className="sr-only">{unit}</dt>
                            <dd className="font-pixel text-generated">{numberFormat.format(count)}</dd>
                            <dd className="text-text-muted">{unit}</dd>
                        </div>
                    ))}
                </dl>
            </div>
        </article>
    );
};

/** Does anyone use this? The count answers in the heading, two packs show what it handles at scale. */
export const BuiltWith = () => {
    const { t } = useTranslation();

    return (
        <section id="built-with" className="frame px-4 py-12 lg:px-12 lg:py-16 border-t border-border scroll-mt-14">
            <h2 className="text-[1.75rem] lg:text-[2.25rem] leading-tight font-bold text-balance">{t('builtWith.title').replace('{n}', String(TOTAL_BUILT_WITH))}</h2>
            <p className="mt-4 text-text-muted text-pretty">
                {t('builtWith.subtitle')}{' '}
                <a href="https://github.com/Stoupy51/StewBeet#-what-projects-use-stewbeet" target="_blank" rel="noopener noreferrer" className="text-link underline underline-offset-2">{t('builtWith.seeAll')}</a>
            </p>
            <div className="mt-8 grid gap-4 md:grid-cols-2">
                {FLAGSHIPS.map((project) => <FlagshipCard key={project.url} project={project} />)}
            </div>
        </section>
    );
};
