import { motion } from 'framer-motion';
import { HiChevronRight, HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { HEADING, PIXEL_RULE, TEXT_ACCENT_HOVER } from '../theme';
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

/**
 * Four lists of near-identical pills in one column read as a wall. Each group now carries
 * its own accent so the eye can tell "written by other people" from "also by the author"
 * without reading the label again, and the two long author-owned lists start collapsed so
 * the section leads with the parts a visitor actually weighs.
 */
interface GroupStyle {
    label: string;
    pill: string;
    owner: string;
}

const COMMUNITY_STYLE: GroupStyle = {
    label: 'text-mc-emerald',
    pill: 'bg-mc-emerald/10 border-mc-emerald/30 text-slate-100 hover:bg-mc-emerald/20 hover:border-mc-emerald/60',
    owner: 'text-mc-emerald/80',
};

const AUTHOR_STYLE: GroupStyle = {
    label: 'text-slate-300',
    pill: 'bg-slate-900/60 border-white/10 text-slate-200 hover:border-white/25 hover:text-white',
    owner: 'text-slate-400',
};

const LIBRARY_STYLE: GroupStyle = {
    label: 'text-mc-diamond',
    pill: 'bg-mc-diamond/10 border-mc-diamond/25 text-slate-100 hover:bg-mc-diamond/20 hover:border-mc-diamond/60',
    owner: 'text-mc-diamond/80',
};

const INTEGRATION_STYLE: GroupStyle = {
    label: 'text-mc-copper',
    pill: 'bg-mc-copper/10 border-mc-copper/30 text-slate-100 hover:bg-mc-copper/20 hover:border-mc-copper/60',
    owner: 'text-mc-copper/90',
};

/** One flagship pack: what it costs to write, beside what it produces. */
const FlagshipCard = ({ project }: { project: Flagship }) => {
    const { t } = useTranslation();
    const outputs: [number, string][] = [
        [project.functions, t('builtWith.unitFunctions')],
        [project.jsonFiles, t('builtWith.unitJson')],
        [project.textures, t('builtWith.unitTextures')],
    ];

    // The card is not one big anchor any more: the pack itself points at Modrinth, where a
    // player installs it, and a separate link keeps the source reachable for a reader.
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

const Pills = ({ entries, style }: { entries: Entry[]; style: GroupStyle }) => (
    <div className="flex flex-wrap gap-2">
        {entries.map((entry) => (
            <a
                key={entry.url}
                href={entry.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`group inline-flex items-baseline gap-2 px-3 py-1.5 rounded-panel border text-sm transition-colors ${style.pill}`}
            >
                <span className="font-medium">{entry.name}</span>
                <span className={`text-[0.6875rem] font-mono ${style.owner}`}>{entry.owner}</span>
                <HiExternalLink className="opacity-0 group-hover:opacity-70 transition-opacity self-center" />
            </a>
        ))}
    </div>
);

const GroupHeading = ({ label, note, style }: { label: string; note?: string; style: GroupStyle }) => (
    <div className="flex items-baseline gap-3 mb-4">
        <p className={`text-sm font-mono uppercase tracking-wider ${style.label}`}>{label}</p>
        {note && <p className="text-xs text-slate-400">{note}</p>}
    </div>
);

/**
 * The author's own lists fold away: present as evidence, but not competing for attention.
 * The summary is styled as a control rather than a heading — bordered, hoverable, with a
 * chevron that turns — because a bare label with a small caret did not read as clickable.
 */
const CollapsedGroup = ({ label, entries, style }: { label: string; entries: Entry[]; style: GroupStyle }) => {
    const { t } = useTranslation();

    return (
        <details className="group/details">
            <summary className="cursor-pointer list-none flex items-center gap-3 px-4 py-3 rounded-panel border border-white/10 bg-slate-900/60 hover:border-white/25 hover:bg-slate-900 transition-colors">
                <HiChevronRight
                    className="text-slate-400 flex-shrink-0 transition-transform group-open/details:rotate-90"
                    aria-hidden="true"
                />
                <span className={`text-sm font-mono uppercase tracking-wider ${style.label}`}>{label}</span>
                <span className="ml-auto text-xs text-slate-400 flex-shrink-0">
                    <span className="group-open/details:hidden">{t('builtWith.showCount').replace('{n}', String(entries.length))}</span>
                    <span className="hidden group-open/details:inline">{t('builtWith.hide')}</span>
                </span>
            </summary>
            <div className="pt-4">
                <Pills entries={entries} style={style} />
            </div>
        </details>
    );
};

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
                    <div>
                        <GroupHeading label={t('builtWith.atScale')} note={t('builtWith.atScaleNote')} style={AUTHOR_STYLE} />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {FLAGSHIPS.map((project) => (
                                <FlagshipCard key={project.url} project={project} />
                            ))}
                        </div>
                    </div>

                    <div>
                        <GroupHeading label={t('builtWith.community')} note={t('builtWith.communityNote')} style={COMMUNITY_STYLE} />
                        <Pills entries={COMMUNITY_PROJECTS} style={COMMUNITY_STYLE} />
                    </div>

                    <div>
                        <GroupHeading label={t('builtWith.integrations')} note={t('builtWith.integrationsNote')} style={INTEGRATION_STYLE} />
                        <Pills entries={INTEGRATIONS} style={INTEGRATION_STYLE} />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-2 border-t border-white/10">
                        <CollapsedGroup label={t('builtWith.maintainerPacks')} entries={MAINTAINER_PROJECTS} style={AUTHOR_STYLE} />
                        <CollapsedGroup label={t('builtWith.libraries')} entries={LIBRARIES} style={LIBRARY_STYLE} />
                    </div>

                    <div>
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
