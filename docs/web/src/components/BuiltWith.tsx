import { motion } from 'framer-motion';
import { HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { ACCENT_BORDER_HOVER, HEADING, PIXEL_RULE, TEXT_ACCENT, TEXT_ACCENT_HOVER } from '../theme';
import {
    COMMUNITY_PROJECTS,
    FLAGSHIPS,
    INTEGRATIONS,
    LIBRARIES,
    MAINTAINER_PROJECTS,
    type Entry,
    type Flagship,
} from './builtWithData';

const numberFormat = new Intl.NumberFormat('en-US');

/** One flagship pack, shown as what it costs to write against what it produces. */
const FlagshipCard = ({ project }: { project: Flagship }) => {
    const { t } = useTranslation();
    const outputs: [number, string][] = [
        [project.functions, t('builtWith.unitFunctions')],
        [project.jsonFiles, t('builtWith.unitJson')],
        [project.textures, t('builtWith.unitTextures')],
    ];

    return (
        <a
            href={project.url}
            target="_blank"
            rel="noopener noreferrer"
            className={`group block rounded-panel border border-white/10 ${ACCENT_BORDER_HOVER} bg-slate-900/60 p-6 transition-colors`}
        >
            <div className="flex items-baseline justify-between gap-3 mb-3">
                <h4 className="text-lg font-semibold text-slate-50">{project.name}</h4>
                <HiExternalLink className="text-slate-400 group-hover:text-mc-emerald transition-colors flex-shrink-0" />
            </div>

            <p className="text-sm text-slate-400 leading-relaxed mb-5">{t(project.descriptionKey)}</p>

            <div className="flex items-baseline gap-2 mb-4 font-mono text-sm">
                <span className="text-slate-200">{numberFormat.format(project.sourceLines)}</span>
                <span className="text-slate-400">{t('builtWith.unitSourceLines')}</span>
            </div>

            <div className="border-t border-white/10 pt-4 grid grid-cols-3 gap-2">
                {outputs.map(([count, unit]) => (
                    <div key={unit}>
                        <p className={`font-mono text-base ${TEXT_ACCENT}`}>{numberFormat.format(count)}</p>
                        <p className="text-xs text-slate-400 leading-tight">{unit}</p>
                    </div>
                ))}
            </div>
        </a>
    );
};

const PillGroup = ({ label, note, entries }: { label: string; note?: string; entries: Entry[] }) => (
    <div>
        <div className="flex items-baseline gap-3 mb-4">
            <p className="text-sm font-mono uppercase tracking-wider text-slate-200">{label}</p>
            {note && <p className="text-xs text-slate-400">{note}</p>}
        </div>
        <div className="flex flex-wrap gap-2">
            {entries.map((entry) => (
                <a
                    key={entry.url}
                    href={entry.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`group inline-flex items-baseline gap-2 px-3 py-1.5 rounded-panel border border-white/10 ${ACCENT_BORDER_HOVER} bg-slate-900/60 text-sm text-slate-200 hover:text-white transition-colors`}
                >
                    <span className="font-medium">{entry.name}</span>
                    <span className="text-[0.6875rem] font-mono text-slate-400">{entry.owner}</span>
                    <HiExternalLink className="opacity-0 group-hover:opacity-70 transition-opacity self-center" />
                </a>
            ))}
        </div>
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
                    className="mb-12 max-w-2xl"
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${HEADING}`}>{t('builtWith.title')}</h2>
                    <p className="text-slate-300 text-lg">{t('builtWith.subtitle')}</p>
                </motion.div>

                <div className="space-y-12">
                    <PillGroup label={t('builtWith.community')} note={t('builtWith.communityNote')} entries={COMMUNITY_PROJECTS} />

                    <div>
                        <div className="flex items-baseline gap-3 mb-4">
                            <p className="text-sm font-mono uppercase tracking-wider text-slate-200">{t('builtWith.atScale')}</p>
                            <p className="text-xs text-slate-400">{t('builtWith.atScaleNote')}</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                            {FLAGSHIPS.map((project) => (
                                <FlagshipCard key={project.url} project={project} />
                            ))}
                        </div>
                    </div>

                    <PillGroup label={t('builtWith.maintainerPacks')} entries={MAINTAINER_PROJECTS} />
                    <PillGroup label={t('builtWith.libraries')} entries={LIBRARIES} />
                    <PillGroup label={t('builtWith.integrations')} note={t('builtWith.integrationsNote')} entries={INTEGRATIONS} />

                    <div className="pt-2">
                        <a
                            href="https://github.com/Stoupy51/StewBeet#-what-projects-use-stewbeet"
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`text-sm ${TEXT_ACCENT_HOVER} underline-offset-4 hover:underline`}
                        >
                            {t('builtWith.seeAll')}
                        </a>
                    </div>
                </div>
            </div>
        </section>
    );
};
