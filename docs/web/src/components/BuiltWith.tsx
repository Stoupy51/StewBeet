import { HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { CARD, EYEBROW, PAGE, SECTION_LEAD, SECTION_TITLE, TEXT_ACCENT_HOVER } from '../theme';
import { FLAGSHIPS, TOTAL_BUILT_WITH, type Flagship } from './builtWithData';

const numberFormat = new Intl.NumberFormat('en-US');

/**
 * Does anyone actually use this? The count answers it in the heading, two packs show what the
 * framework handles at scale, and the roster of every project lives on GitHub.
 */

/** One flagship pack: what it costs to write, beside what it produces. */
const FlagshipCard = ({ project }: { project: Flagship }) => {
    const { t } = useTranslation();
    const outputs: [number, string][] = [
        [project.functions, t('builtWith.unitFunctions')],
        [project.jsonFiles, t('builtWith.unitJson')],
        [project.textures, t('builtWith.unitTextures')],
    ];

    // The pack points at Modrinth, where a player installs it; a separate link keeps the source reachable.
    return (
        <article data-rise className={`${CARD} group overflow-hidden hover:border-ink-600 transition-colors`}>
            <a href={project.modrinth} target="_blank" rel="noopener noreferrer" className="block border-b border-ink-800">
                <img
                    src={project.image}
                    alt={t('builtWith.itemsAlt').replace('{project}', project.name)}
                    loading="lazy"
                    decoding="async"
                    className="w-full h-52 object-cover object-top"
                />
            </a>

            <div className="p-6">
                <div className="flex items-baseline justify-between gap-3">
                    <a
                        href={project.modrinth}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-lg font-semibold tracking-tight text-ink-50 hover:text-beet-300 transition-colors"
                    >
                        {project.name}
                        <HiExternalLink className="text-ink-500" aria-hidden="true" />
                    </a>
                    <a
                        href={project.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-mono text-xs text-ink-400 hover:text-ink-100 transition-colors flex-shrink-0"
                    >
                        {t('builtWith.sourceLink')}
                    </a>
                </div>

                <p className="mt-2 text-sm text-ink-400 leading-relaxed">{t(project.descriptionKey)}</p>

                <p className="mt-5 font-mono text-sm">
                    <span className="text-ink-100">{numberFormat.format(project.sourceLines)}</span>{' '}
                    <span className="text-ink-400">{t('builtWith.unitSourceLines')}</span>
                </p>

                <dl className="mt-3 pt-4 border-t border-ink-800 grid grid-cols-3 gap-2">
                    {outputs.map(([count, unit]) => (
                        <div key={unit}>
                            <dt className="sr-only">{unit}</dt>
                            <dd className="font-mono text-base text-leaf-400">{numberFormat.format(count)}</dd>
                            <dd className="text-xs text-ink-400">{unit}</dd>
                        </div>
                    ))}
                </dl>
            </div>
        </article>
    );
};

export const BuiltWith: React.FC = () => {
    const { t } = useTranslation();

    return (
        <section id="built-with" className="py-14 md:py-28 border-t border-ink-800">
            <div className={PAGE}>
                <div data-rise className="max-w-3xl">
                    <p className={EYEBROW}>{t('builtWith.eyebrow')}</p>
                    <h2 className={`mt-4 ${SECTION_TITLE}`}>{t('builtWith.title').replace('{n}', String(TOTAL_BUILT_WITH))}</h2>
                    <p className={`mt-4 ${SECTION_LEAD}`}>{t('builtWith.subtitle')}</p>
                </div>

                <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {FLAGSHIPS.map((project) => (
                        <FlagshipCard key={project.url} project={project} />
                    ))}
                </div>

                <a
                    href="https://github.com/Stoupy51/StewBeet#-what-projects-use-stewbeet"
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`mt-8 inline-flex items-center gap-2 text-sm font-medium ${TEXT_ACCENT_HOVER}`}
                >
                    {t('builtWith.seeAll')}
                    <HiExternalLink aria-hidden="true" />
                </a>
            </div>
        </section>
    );
};
