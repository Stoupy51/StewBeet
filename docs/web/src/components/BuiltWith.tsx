import { motion } from 'framer-motion';
import { HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { GRADIENT_TEXT, TEXT_ACCENT_HOVER } from '../theme';

interface Entry {
    name: string;
    owner: string;
    url: string;
}

/** Palette per group, so projects, libraries and integrations read apart at a glance. */
interface GroupStyle {
    pill: string;
    owner: string;
    label: string;
}

const PROJECT_STYLE: GroupStyle = {
    pill: 'bg-indigo-500/10 border-indigo-500/25 text-indigo-100 hover:bg-indigo-500/20 hover:border-indigo-400/60',
    owner: 'text-indigo-400/70',
    label: 'text-indigo-300',
};

const LIBRARY_STYLE: GroupStyle = {
    pill: 'bg-emerald-500/10 border-emerald-500/25 text-emerald-100 hover:bg-emerald-500/20 hover:border-emerald-400/60',
    owner: 'text-emerald-400/70',
    label: 'text-emerald-300',
};

const INTEGRATION_STYLE: GroupStyle = {
    pill: 'bg-amber-500/10 border-amber-500/25 text-amber-100 hover:bg-amber-500/20 hover:border-amber-400/60',
    owner: 'text-amber-400/70',
    label: 'text-amber-300',
};

/** Public projects listed in the repository README as using the framework. */
const PROJECTS: Entry[] = [
    { name: 'Switch',                   owner: 'Paralya',         url: 'https://github.com/Paralya/Switch' },
    { name: 'Crazy Adventure',          owner: 'VGreluchon',      url: 'https://github.com/VGreluchon/Crazy-Adventure-Datapack' },
    { name: 'Lucky Pillar',             owner: 'YuWan886',        url: 'https://github.com/YuWan886/Lucky-Pillar' },
    { name: 'Elemental Wands',          owner: 'PlanetMinecraft', url: 'https://www.planetminecraft.com/data-pack/elemental-wands/' },
    { name: 'SimplEnergy',              owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/SimplEnergy' },
    { name: 'Stardust Fragment',        owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/StardustFragment' },
    { name: 'MC Guns System',           owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/MC_Guns_System' },
    { name: 'LifeSteal',                owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/LifeSteal' },
    { name: 'Imagine Your Craft',       owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/ImagineYourCraftDatapack' },
    { name: 'Survisland',               owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/Survisland' },
    { name: 'Cauldron Concrete Powder', owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/CauldronConcretePowder' },
    { name: 'More Apples',              owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/MoreApples' },
    { name: 'Random Mob Sizes',         owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/RandomMobSizes' },
    { name: 'Smithed Summit 2026',      owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/SmithedSummit2026' },
    { name: 'Smithed Summit 2024',      owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/SmithedSummit2024' },
    { name: 'Smithed Direct',           owner: 'Stoupy51',        url: 'https://github.com/Stoupy51/SmithedDirect' },
];

/** Libraries and tools that are themselves built with the framework. */
const LIBRARIES: Entry[] = [
    { name: 'Smart Ore Generation', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmartOreGeneration' },
    { name: 'Furnace NBT Recipes',  owner: 'Stoupy51', url: 'https://github.com/Stoupy51/FurnaceNbtRecipes' },
    { name: 'Common Signals',       owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CommonSignals' },
    { name: 'Realistic Explosion',  owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RealisticExplosion' },
    { name: 'Shopping Kart',        owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ShoppingKart' },
    { name: 'Sheep Wars',           owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SheepWars' },
    { name: 'Golf Ball',            owner: 'Stoupy51', url: 'https://github.com/Stoupy51/GolfBall' },
];

/** Third-party libraries StewBeet detects in your code and wires into the build. */
const INTEGRATIONS: Entry[] = [
    { name: 'Smithed Custom Blocks', owner: 'smithed.dev',  url: 'https://wiki.smithed.dev/libraries/custom-block/' },
    { name: 'Smithed Crafter',       owner: 'smithed.dev',  url: 'https://wiki.smithed.dev/libraries/crafter/' },
    { name: 'Smithed Weld',          owner: 'smithed.dev',  url: 'https://weld.smithed.dev/' },
    { name: 'Bookshelf',             owner: 'mcbookshelf',  url: 'https://github.com/mcbookshelf/bookshelf' },
    { name: 'ItemIO',                owner: 'edayot',       url: 'https://github.com/edayot/ItemIO' },
    { name: 'LanternLoad',           owner: 'LanternMC',    url: 'https://github.com/LanternMC/load' },
    { name: 'NeoEnchant',            owner: 'Modrinth',     url: 'https://modrinth.com/datapack/neoenchant' },
    { name: 'SimpleDrawer',          owner: 'edayot',       url: 'https://edayot.github.io/SimpleDrawer/material.html' },
];

const PillGroup = ({ label, note, entries, style }: { label: string; note?: string; entries: Entry[]; style: GroupStyle }) => (
    <div>
        <div className="flex items-baseline gap-3 mb-4">
            <p className={`text-sm font-mono uppercase tracking-wider ${style.label}`}>{label}</p>
            {note && <p className="text-xs text-slate-500">{note}</p>}
        </div>
        <div className="flex flex-wrap gap-2">
            {entries.map((entry, index) => (
                <motion.a
                    key={entry.url}
                    href={entry.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    initial={{ opacity: 0, y: 8 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.25, delay: Math.min(index * 0.02, 0.3) }}
                    className={`group inline-flex items-baseline gap-2 px-3 py-1.5 rounded-full border text-sm transition-all duration-200 ${style.pill}`}
                >
                    <span className="font-medium">{entry.name}</span>
                    <span className={`text-[0.6875rem] font-mono ${style.owner}`}>{entry.owner}</span>
                    <HiExternalLink className="opacity-0 group-hover:opacity-70 transition-opacity self-center" />
                </motion.a>
            ))}
        </div>
    </div>
);

export const BuiltWith: React.FC = () => {
    const { t } = useTranslation();

    return (
        <section id="built-with" className="py-20 px-4 relative overflow-hidden bg-gradient-to-b from-[#0a0a0a] via-slate-900/60 to-slate-900/60">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px]" />
            </div>

            <div className="max-w-6xl mx-auto relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-12"
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${GRADIENT_TEXT}`}>{t('builtWith.title')}</h2>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">{t('builtWith.subtitle')}</p>
                </motion.div>

                <div className="space-y-10">
                    <PillGroup label={t('builtWith.projects')} entries={PROJECTS} style={PROJECT_STYLE} />
                    <PillGroup label={t('builtWith.libraries')} entries={LIBRARIES} style={LIBRARY_STYLE} />
                    <PillGroup
                        label={t('builtWith.integrations')}
                        note={t('builtWith.integrationsNote')}
                        entries={INTEGRATIONS}
                        style={INTEGRATION_STYLE}
                    />

                    <div className="text-center pt-2">
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
