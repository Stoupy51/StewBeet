import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    HiCog,
    HiVolumeUp,
    HiColorSwatch,
    HiPhotograph,
    HiBeaker,
    HiBookOpen,
    HiLightningBolt,
    HiCube,
    HiGift,
    HiSortAscending,
    HiClock,
    HiCollection,
    HiClipboardList,
    HiEye,
    HiGlobe,
    HiCode,
    HiArchive,
    HiLink,
    HiFolderOpen,
    HiRefresh,
    HiShieldCheck,
    HiHashtag,
    HiX
} from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { TEXT_ACCENT_HOVER } from '../theme';

type Dependency = 'full' | 'partial' | 'none';

const DEPENDENCY_COLOR: Record<Dependency, string> = {
    full: 'bg-beet-500',
    partial: 'bg-mc-gold',
    none: 'bg-leaf-400',
};

const DEPENDENCY_LABEL: Record<Dependency, string> = {
    full: 'showcase.fullyDependent',
    partial: 'showcase.partlyDependent',
    none: 'showcase.independent',
};

/** A coloured square and its label, shared by the table rows and the legend above it. */
export const DependencyMark = ({ level }: { level: Dependency }) => {
    const { t } = useTranslation();
    return (
        <span className="inline-flex items-center gap-2 text-xs text-ink-400">
            <span className={`w-2 h-2 flex-shrink-0 ${DEPENDENCY_COLOR[level]}`} aria-hidden="true" />
            {t(DEPENDENCY_LABEL[level])}
        </span>
    );
};

interface Plugin {
    id: number;
    name: string;
    category: string;
    descriptionKey: string;
    icon: React.ComponentType<{ className?: string }>;
    /** How much of the StewBeet pipeline the plugin needs to run. */
    dependency: Dependency;
    image: string;
    /** Markdown page for this row, `{lang}` substituted at render time. Defaults to `plugins/<name>.md`. */
    docSrc?: string;
}

const getPlugins = (t: (key: string) => string): Plugin[] => [
    // Core
    { id: 1, name: 'initialize', category: t('pluginsTable.categoryCore'), descriptionKey: 'pluginsTable.initializeDesc', icon: HiCog, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/initialize.source_lore.jpg' },

    // Resource Pack
    { id: 2, name: 'resource_pack.sounds', category: t('pluginsTable.categoryResourcePack'), descriptionKey: 'pluginsTable.soundsDesc', icon: HiVolumeUp, dependency: 'partial', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.sounds.result.jpg' },
    { id: 3, name: 'resource_pack.item_models', category: t('pluginsTable.categoryResourcePack'), descriptionKey: 'pluginsTable.itemModelsDesc', icon: HiColorSwatch, dependency: 'partial', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.item_models.pattern_detection.jpg' },
    { id: 4, name: 'resource_pack.check_power_of_2', category: t('pluginsTable.categoryResourcePack'), descriptionKey: 'pluginsTable.checkPowerOf2Desc', icon: HiPhotograph, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.check_power_of_2.warning.jpg' },

    // Recipes & Custom Content
    { id: 5, name: 'custom_recipes', category: t('pluginsTable.categoryRecipes'), descriptionKey: 'pluginsTable.customRecipesDesc', icon: HiBeaker, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/custom_recipes.smithed_recipe.jpg' },
    { id: 6, name: 'custom_paintings', category: t('pluginsTable.categoryCustomContent'), descriptionKey: 'pluginsTable.customPaintingsDesc', icon: HiPhotograph, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/custom_paintings.placed_painting.jpg' },

    // Documentation
    { id: 7, name: 'ingame_manual', category: t('pluginsTable.categoryDocumentation'), descriptionKey: 'pluginsTable.ingameManualDesc', icon: HiBookOpen, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/docs/plugins/img/ingame_manual.gif', docSrc: '7_ingame_manual/{lang}.md' },

    // Datapack
    { id: 8, name: 'datapack.loading', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.loadingDesc', icon: HiLightningBolt, dependency: 'partial', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loading.load_messages.jpg' },
    { id: 9, name: 'datapack.custom_blocks', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.customBlocksDesc', icon: HiCube, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.custom_blocks.stats.jpg' },
    { id: 10, name: 'datapack.loot_tables', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.lootTablesDesc', icon: HiGift, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loot_tables.give_all.jpg' },
    { id: 11, name: 'datapack.sorters', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.sortersDesc', icon: HiSortAscending, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.sorters.registry.jpg' },

    // Compatibility
    { id: 23, name: 'compatibilities.simpledrawer', category: t('pluginsTable.categoryCompatibility'), descriptionKey: 'pluginsTable.simpledrawerDesc', icon: HiCollection, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/compatibilities.simpledrawer.complete_file_tree.jpg' },
    { id: 24, name: 'compatibilities.neo_enchant', category: t('pluginsTable.categoryCompatibility'), descriptionKey: 'pluginsTable.neoEnchantDesc', icon: HiLightningBolt, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/compatibilities.neo_enchant.veinminer.jpg' },

    // Finalization
    { id: 12, name: 'finalyze.custom_blocks_ticking', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.customBlocksTickingDesc', icon: HiClock, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.custom_blocks_ticking.timers.jpg' },
    { id: 13, name: 'finalyze.basic_datapack_structure', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.basicDatapackStructureDesc', icon: HiCollection, dependency: 'partial', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.basic_datapack_structure.timers.jpg' },
    { id: 14, name: 'finalyze.dependencies', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.dependenciesDesc', icon: HiClipboardList, dependency: 'full', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.dependencies.ingame_errors.jpg' },
    { id: 15, name: 'finalyze.check_unused_textures', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.checkUnusedTexturesDesc', icon: HiEye, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.check_unused_textures.warnings.jpg' },

    // Automation
    { id: 16, name: 'auto.lang_file', category: t('pluginsTable.categoryAutomation'), descriptionKey: 'pluginsTable.langFileDesc', icon: HiGlobe, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.lang_file.en_us_example.jpg' },
    { id: 26, name: 'auto.text_renders', category: t('pluginsTable.categoryAutomation'), descriptionKey: 'pluginsTable.textRendersDesc', icon: HiPhotograph, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.text_renders.example_ingame.jpg' },
    { id: 17, name: 'auto.headers', category: t('pluginsTable.categoryAutomation'), descriptionKey: 'pluginsTable.headersDesc', icon: HiCode, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.headers.macro_example.jpg' },
    { id: 22, name: 'auto.scoreboard_constants', category: t('pluginsTable.categoryAutomation'), descriptionKey: 'pluginsTable.scoreboardConstantsDesc', icon: HiHashtag, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.scoreboard_constants.example.jpg' },

    // Build
    { id: 18, name: 'archive', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.archiveDesc', icon: HiArchive, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/archive.output_directory.jpg' },
    { id: 19, name: 'merge_smithed_weld', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.mergeSmithedWeldDesc', icon: HiLink, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/merged_smithed_weld.output_directory.jpg' },
    { id: 20, name: 'copy_to_destination', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.copyToDestinationDesc', icon: HiFolderOpen, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/copy_to_destination.datapack_destination.jpg' },
    { id: 25, name: 'livereload', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.livereloadDesc', icon: HiRefresh, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/copy_to_destination.datapack_destination.jpg' },
    { id: 27, name: 'sniffer', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.snifferDesc', icon: HiCode, dependency: 'partial', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/sniffer.source_map.jpg' },
    { id: 21, name: 'compute_sha1', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.computeSha1Desc', icon: HiShieldCheck, dependency: 'none', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/compute_sha1.example.jpg' },
];

export const PluginsTable: React.FC = () => {
    const { t, language } = useTranslation();
    const plugins = getPlugins(t);
    const docLink = (plugin: Plugin) =>
        `/markdown?src=${encodeURIComponent(plugin.docSrc?.replace('{lang}', language) ?? `plugins/${plugin.name}.md`)}`;
    const [selectedImage, setSelectedImage] = useState<{ src: string; alt: string } | null>(null);

    return (
        <>
            {/* Table Layout */}
            <div className="overflow-x-auto rounded-panel border border-ink-800 bg-ink-900">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-ink-800 bg-ink-950/40">
                            <th className="p-4 font-mono text-xs uppercase tracking-wider text-ink-400 font-normal w-32">{t('pluginsTable.category')}</th>
                            <th className="p-4 font-mono text-xs uppercase tracking-wider text-ink-400 font-normal">{t('pluginsTable.plugin')}</th>
                            <th className="p-4 font-mono text-xs uppercase tracking-wider text-ink-400 font-normal">{t('pluginsTable.description')}</th>
                            <th className="p-4 font-mono text-xs uppercase tracking-wider text-ink-400 font-normal">{t('pluginsTable.image')}</th>
                            <th className="p-4 font-mono text-xs uppercase tracking-wider text-ink-400 font-normal w-40">{t('pluginsTable.dependency')}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-ink-800">
                        {plugins.map((plugin) => {
                            const Icon = plugin.icon;
                            return (
                                <tr key={plugin.id} className="hover:bg-ink-850 transition-colors group">
                                    <td className="p-4">
                                        <div className="flex items-center gap-2">
                                            <Icon className="text-lg text-ink-500" />
                                            <span className="font-medium text-ink-300 text-sm">{plugin.category}</span>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Link
                                            to={docLink(plugin)}
                                            className={`${TEXT_ACCENT_HOVER} font-semibold hover:underline underline-offset-4`}
                                        >
                                            {plugin.name}
                                        </Link>
                                    </td>
                                    <td className="p-4 max-w-xs">
                                        <Link
                                            to={docLink(plugin)}
                                            className="text-ink-400 hover:text-ink-300 text-sm block transition-colors"
                                        >
                                            {t(plugin.descriptionKey)}
                                        </Link>
                                    </td>
                                    <td className="p-4">
                                        <button
                                            onClick={() => setSelectedImage({ src: plugin.image, alt: plugin.name })}
                                            className="block w-56 h-32 rounded-control overflow-hidden border border-ink-800 bg-ink-950 hover:border-ink-600 transition-colors cursor-zoom-in"
                                        >
                                            <img
                                                src={plugin.image}
                                                alt={plugin.name}
                                                loading="lazy"
                                                decoding="async"
                                                referrerPolicy="no-referrer"
                                                className="w-full h-full object-cover"
                                            />
                                        </button>
                                    </td>
                                    <td className="p-4">
                                        <DependencyMark level={plugin.dependency} />
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Image Modal */}
            <AnimatePresence mode="wait">
                {selectedImage && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.1 }}
                        onClick={() => setSelectedImage(null)}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4"
                    >
                        {/* Close button */}
                        <button
                            onClick={() => setSelectedImage(null)}
                            className="absolute top-4 right-4 p-2 rounded-control bg-ink-900 border border-ink-700 hover:border-ink-500 text-ink-100 transition-colors z-10"
                            aria-label="Close"
                        >
                            <HiX className="text-2xl" />
                        </button>

                        {/* Image */}
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            transition={{ duration: 0.15, ease: "easeOut" }}
                            onClick={(e) => e.stopPropagation()}
                            className="relative max-w-7xl max-h-[90vh] w-full"
                        >
                            <img
                                src={selectedImage.src}
                                alt={selectedImage.alt}
                                className="w-full h-full object-contain rounded-panel"
                            />
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
};
