import { motion } from 'framer-motion';
import { HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { HEADING, PIXEL_RULE, TEXT_ACCENT_HOVER } from '../theme';
import { FLAGSHIPS, INTEGRATIONS, TOTAL_BUILT_WITH, type Entry, type Flagship } from './builtWithData';

const numberFormat = new Intl.NumberFormat('en-US');

/**
 * This was four lists of near-identical pills, dozens of links of slightly different sizes
 * competing for the same attention, and it read as clutter rather than as evidence.
 *
 * A visitor weighs one question here: does anyone actually use this? The count answers it in
 * the heading, two packs show what the framework handles at scale, and the roster of every
 * project lives on GitHub, where a reader who wants it will look anyway.
 */

const INTEGRATION_PILL =
    'bg-mc-copper/10 border-mc-copper/30 text-slate-100 hover:bg-mc-copper/20 hover:border-mc-copper/60';

/** One flagship pack: what it costs to write, beside what it produces. */
const FlagshipCard = ({ project }: { project: Flagship }) => {
    const { t } = useTranslation();
    const outputs: [number, string][] = [
        [project.functions, t('builtWith.unitFunctions')],
        [project.jsonFiles, t('builtWith.unitJson')],
        [project.textures, t('builtWith.unitTextures')],
    ];

    // The card is not one big anchor: the pack itself points at Modrinth, where a player
    // installs it, and a separate link keeps the source reachable for a reader.
    return (
        <div className="group rounded-panel border border-white/10 hover:border-mc-emerald/50 bg-slate-900/60 overflow-hidden transition-colors">
            <a href={project.modrinth} target="_blank" rel="noopener noreferrer" className="block">
                <img
                    src={project.image}
                    alt={t('builtWith.itemsAlt').replace('{project}', project.name)}
                    loading="lazy"
                    decoding="async"
                    className="w-full h-56 object-cover object-top border-b border-white/10"
                />
            </a>

            <div className="p-6">
                <div className="flex items-baseline justify-between gap-3 mb-2">
                    <a
                        href={project.modrinth}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-baseline gap-2 text-lg font-semibold text-slate-50 hover:text-mc-emerald transition-colors"
                    >
                        {project.name}
                        <HiExternalLink className="self-center flex-shrink-0" aria-hidden="true" />
                    </a>
                    <a
                        href={project.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-mono text-slate-400 hover:text-mc-diamond transition-colors flex-shrink-0"
                    >
                        {t('builtWith.sourceLink')}
                    </a>
                </div>

                <p className="text-sm text-slate-400 leading-relaxed mb-5">{t(project.descriptionKey)}</p>

                <div className="flex items-baseline gap-2 mb-4 font-mono text-sm">
                    <span className="text-slate-200">{numberFormat.format(project.sourceLines)}</span>
                    <span className="text-slate-400">{t('builtWith.unitSourceLines')}</span>
                </div>

                <div className="border-t border-white/10 pt-4 grid grid-cols-3 gap-2">
                    {outputs.map(([count, unit]) => (
                        <div key={unit}>
                            <p className="font-mono text-base text-mc-emerald">{numberFormat.format(count)}</p>
                            <p className="text-xs text-slate-400 leading-tight">{unit}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const IntegrationPills = ({ entries }: { entries: Entry[] }) => (
    <div className="flex flex-wrap gap-2">
        {entries.map((entry) => (
            <a
                key={entry.url}
                href={entry.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`inline-flex items-baseline gap-2 px-3 py-1.5 rounded-panel border text-sm transition-colors ${INTEGRATION_PILL}`}
            >
                <span className="font-medium">{entry.name}</span>
                <span className="text-[0.6875rem] font-mono text-mc-copper/90">{entry.owner}</span>
            </a>
        ))}
    </div>
);

export const BuiltWith: React.FC = () => {
    const { t } = useTranslation();
    const motionSafe = useMotionSafe();

    return (
        <section id="built-with" className="py-20 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            <div className="max-w-6xl mx-auto relative z-10">
                <motion.div
                    {...motionSafe({
                        initial: { y: 30 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.6 },
                    })}
                    className="mb-10 max-w-2xl"
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${HEADING}`}>
                        {t('builtWith.title').replace('{n}', String(TOTAL_BUILT_WITH))}
                    </h2>
                    <p className="text-slate-300 text-lg">{t('builtWith.subtitle')}</p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {FLAGSHIPS.map((project) => (
                        <FlagshipCard key={project.url} project={project} />
                    ))}
                </div>

                <a
                    href="https://github.com/Stoupy51/StewBeet#-what-projects-use-stewbeet"
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`mt-8 inline-flex items-center gap-2 text-sm ${TEXT_ACCENT_HOVER} underline-offset-4 hover:underline`}
                >
                    {t('builtWith.seeAll')}
                    <HiExternalLink aria-hidden="true" />
                </a>

                <div className="mt-12 pt-8 border-t border-white/10">
                    <p className="text-sm font-mono uppercase tracking-wider text-mc-copper mb-2">{t('builtWith.integrations')}</p>
                    <p className="text-sm text-slate-400 mb-4">{t('builtWith.integrationsNote')}</p>
                    <IntegrationPills entries={INTEGRATIONS} />
                </div>
            </div>
        </section>
    );
};
