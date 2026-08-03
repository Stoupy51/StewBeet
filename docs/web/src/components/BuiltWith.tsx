import { motion } from 'framer-motion';
import { HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { ACCENT_BORDER_HOVER, GRADIENT_TEXT, HOVER_CARD, TEXT_ACCENT_HOVER } from '../theme';

interface Project {
    name: string;
    owner: string;
    url: string;
}

interface Integration {
    name: string;
    url: string;
}

/** Public projects listed in the repository README as using the framework. */
const PROJECTS: Project[] = [
    { name: 'Switch',                    owner: 'Paralya',      url: 'https://github.com/Paralya/Switch' },
    { name: 'Crazy Adventure Datapack',  owner: 'VGreluchon',   url: 'https://github.com/VGreluchon/Crazy-Adventure-Datapack' },
    { name: 'Lucky Pillar',              owner: 'YuWan886',     url: 'https://github.com/YuWan886/Lucky-Pillar' },
    { name: 'Elemental Wands',           owner: 'PlanetMinecraft', url: 'https://www.planetminecraft.com/data-pack/elemental-wands/' },
    { name: 'SimplEnergy',               owner: 'Stoupy51',     url: 'https://github.com/Stoupy51/SimplEnergy' },
    { name: 'Stardust Fragment',         owner: 'Stoupy51',     url: 'https://github.com/Stoupy51/StardustFragment' },
    { name: 'MC Guns System',            owner: 'Stoupy51',     url: 'https://github.com/Stoupy51/MC_Guns_System' },
    { name: 'Imagine Your Craft',        owner: 'Stoupy51',     url: 'https://github.com/Stoupy51/ImagineYourCraftDatapack' },
];

/** Libraries and tools that are themselves built with the framework. */
const LIBRARIES: Project[] = [
    { name: 'Smart Ore Generation', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmartOreGeneration' },
    { name: 'Furnace NBT Recipes',  owner: 'Stoupy51', url: 'https://github.com/Stoupy51/FurnaceNbtRecipes' },
    { name: 'Common Signals',       owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CommonSignals' },
    { name: 'Realistic Explosion',  owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RealisticExplosion' },
    { name: 'Shopping Kart',        owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ShoppingKart' },
    { name: 'Golf Ball',            owner: 'Stoupy51', url: 'https://github.com/Stoupy51/GolfBall' },
];

/** Third-party libraries StewBeet detects and wires into the build. */
const INTEGRATIONS: Integration[] = [
    { name: 'Smithed Custom Blocks', url: 'https://wiki.smithed.dev/libraries/custom-block/' },
    { name: 'Smithed Crafter',       url: 'https://wiki.smithed.dev/libraries/crafter/' },
    { name: 'Bookshelf',             url: 'https://github.com/mcbookshelf/bookshelf' },
    { name: 'ItemIO',                url: 'https://github.com/edayot/ItemIO' },
    { name: 'Smithed Weld',          url: 'https://weld.smithed.dev/' },
    { name: 'LanternLoad',           url: 'https://github.com/LanternMC/load' },
];

const ProjectGrid = ({ label, projects }: { label: string; projects: Project[] }) => (
    <div>
        <p className="text-sm text-slate-500 mb-4 font-mono uppercase tracking-wider">{label}</p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {projects.map((project) => (
                <a
                    key={project.url}
                    href={project.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`group bg-slate-900/50 border border-white/5 rounded-lg p-4 ${HOVER_CARD} transition-all`}
                >
                    <div className="flex items-start justify-between gap-2">
                        <span className="font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors leading-tight">
                            {project.name}
                        </span>
                        <HiExternalLink className="text-slate-600 group-hover:text-indigo-400 transition-colors flex-shrink-0" />
                    </div>
                    <span className="text-xs text-slate-500 font-mono">{project.owner}</span>
                </a>
            ))}
        </div>
    </div>
);

export const BuiltWith: React.FC = () => {
    const { t } = useTranslation();

    return (
        <section id="built-with" className="py-20 px-4 bg-[#0a0a0a] relative overflow-hidden">
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
                    <ProjectGrid label={t('builtWith.projects')} projects={PROJECTS} />
                    <ProjectGrid label={t('builtWith.libraries')} projects={LIBRARIES} />

                    <div>
                        <p className="text-sm text-slate-500 mb-2 font-mono uppercase tracking-wider">{t('builtWith.integrations')}</p>
                        <p className="text-sm text-slate-500 mb-4">{t('builtWith.integrationsNote')}</p>
                        <div className="flex flex-wrap gap-3">
                            {INTEGRATIONS.map((integration) => (
                                <a
                                    key={integration.url}
                                    href={integration.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={`px-3 py-1.5 bg-slate-900 border border-white/10 rounded-md text-xs text-slate-400 font-mono ${ACCENT_BORDER_HOVER} hover:text-indigo-400 transition-colors`}
                                >
                                    {integration.name}
                                </a>
                            ))}
                        </div>
                    </div>

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
