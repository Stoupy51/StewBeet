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
    HiShieldCheck,
    HiHashtag,
    HiX
} from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { TEXT_ACCENT_HOVER } from '../theme';

interface Plugin {
    id: number;
    name: string;
    category: string;
    descriptionKey: string;
    color: string;
    icon: React.ComponentType<{ className?: string }>;
    dependency: '🔴' | '🟡' | '🟢';
    delay: number;
    link: string;
    image: string;
}

const getPlugins = (t: (key: string) => string): Plugin[] => [
    // Core
    { id: 1, name: 'initialize', category: t('pluginsTable.categoryCore'), descriptionKey: 'pluginsTable.initializeDesc', color: 'from-red-500 to-orange-500', icon: HiCog, dependency: '🔴', delay: 0, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/initialize.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/initialize.source_lore.jpg' },

    // Resource Pack
    { id: 2, name: 'resource_pack.sounds', category: t('pluginsTable.categoryResourcePack'), descriptionKey: 'pluginsTable.soundsDesc', color: 'from-purple-500 to-pink-500', icon: HiVolumeUp, dependency: '🟡', delay: 0.1, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/resource_pack.sounds.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.sounds.result.jpg' },
    { id: 3, name: 'resource_pack.item_models', category: t('pluginsTable.categoryResourcePack'), descriptionKey: 'pluginsTable.itemModelsDesc', color: 'from-blue-500 to-cyan-500', icon: HiColorSwatch, dependency: '🟡', delay: 0.15, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/resource_pack.item_models.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.item_models.pattern_detection.jpg' },
    { id: 4, name: 'resource_pack.check_power_of_2', category: t('pluginsTable.categoryResourcePack'), descriptionKey: 'pluginsTable.checkPowerOf2Desc', color: 'from-indigo-500 to-purple-500', icon: HiPhotograph, dependency: '🟢', delay: 0.2, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/resource_pack.check_power_of_2.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.check_power_of_2.warning.jpg' },

    // Recipes & Custom Content
    { id: 5, name: 'custom_recipes', category: t('pluginsTable.categoryRecipes'), descriptionKey: 'pluginsTable.customRecipesDesc', color: 'from-orange-500 to-red-500', icon: HiBeaker, dependency: '🔴', delay: 0.25, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/custom_recipes.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/custom_recipes.smithed_recipe.jpg' },
    { id: 6, name: 'custom_paintings', category: t('pluginsTable.categoryCustomContent'), descriptionKey: 'pluginsTable.customPaintingsDesc', color: 'from-pink-500 to-rose-500', icon: HiPhotograph, dependency: '🔴', delay: 0.3, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/custom_paintings.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/custom_paintings.placed_painting.jpg' },

    // Documentation
    { id: 7, name: 'ingame_manual', category: t('pluginsTable.categoryDocumentation'), descriptionKey: 'pluginsTable.ingameManualDesc', color: 'from-amber-500 to-yellow-500', icon: HiBookOpen, dependency: '🔴', delay: 0.35, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/ingame_manual.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/docs/plugins/img/ingame_manual.gif' },

    // Datapack
    { id: 8, name: 'datapack.loading', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.loadingDesc', color: 'from-cyan-500 to-blue-500', icon: HiLightningBolt, dependency: '🟡', delay: 0.4, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.loading.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loading.load_messages.jpg' },
    { id: 9, name: 'datapack.custom_blocks', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.customBlocksDesc', color: 'from-teal-500 to-emerald-500', icon: HiCube, dependency: '🔴', delay: 0.45, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.custom_blocks.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.custom_blocks.stats.jpg' },
    { id: 10, name: 'datapack.loot_tables', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.lootTablesDesc', color: 'from-green-500 to-lime-500', icon: HiGift, dependency: '🔴', delay: 0.5, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.loot_tables.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loot_tables.give_all.jpg' },
    { id: 11, name: 'datapack.sorters', category: t('pluginsTable.categoryDatapack'), descriptionKey: 'pluginsTable.sortersDesc', color: 'from-violet-500 to-purple-500', icon: HiSortAscending, dependency: '🟢', delay: 0.55, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.sorters.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.sorters.registry.jpg' },

    // Compatibility
    { id: 23, name: 'compatibilities.simpledrawer', category: t('pluginsTable.categoryCompatibility'), descriptionKey: 'pluginsTable.simpledrawerDesc', color: 'from-amber-500 to-yellow-500', icon: HiCollection, dependency: '🔴', delay: 0.575, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/compatibilities.simpledrawer.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/compatibilities.simpledrawer.complete_file_tree.jpg' },
    { id: 24, name: 'compatibilities.neo_enchant', category: t('pluginsTable.categoryCompatibility'), descriptionKey: 'pluginsTable.neoEnchantDesc', color: 'from-purple-500 to-violet-500', icon: HiLightningBolt, dependency: '🔴', delay: 0.5875, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/compatibilities.neo_enchant.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/compatibilities.neo_enchant.veinminer.jpg' },

    // Finalization
    { id: 12, name: 'finalyze.custom_blocks_ticking', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.customBlocksTickingDesc', color: 'from-rose-500 to-pink-500', icon: HiClock, dependency: '🔴', delay: 0.6, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.custom_blocks_ticking.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.custom_blocks_ticking.timers.jpg' },
    { id: 13, name: 'finalyze.basic_datapack_structure', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.basicDatapackStructureDesc', color: 'from-slate-500 to-gray-500', icon: HiCollection, dependency: '🟡', delay: 0.65, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.basic_datapack_structure.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.basic_datapack_structure.timers.jpg' },
    { id: 14, name: 'finalyze.dependencies', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.dependenciesDesc', color: 'from-blue-500 to-indigo-500', icon: HiClipboardList, dependency: '🔴', delay: 0.7, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.dependencies.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.dependencies.ingame_errors.jpg' },
    { id: 15, name: 'finalyze.check_unused_textures', category: t('pluginsTable.categoryFinalization'), descriptionKey: 'pluginsTable.checkUnusedTexturesDesc', color: 'from-yellow-500 to-orange-500', icon: HiEye, dependency: '🟢', delay: 0.75, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.check_unused_textures.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.check_unused_textures.warnings.jpg' },

    // Automation
    { id: 16, name: 'auto.lang_file', category: t('pluginsTable.categoryAutomation'), descriptionKey: 'pluginsTable.langFileDesc', color: 'from-emerald-500 to-teal-500', icon: HiGlobe, dependency: '🟢', delay: 0.8, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/auto.lang_file.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.lang_file.en_us_example.jpg' },
    { id: 17, name: 'auto.headers', category: t('pluginsTable.categoryAutomation'), descriptionKey: 'pluginsTable.headersDesc', color: 'from-purple-500 to-indigo-500', icon: HiCode, dependency: '🟢', delay: 0.85, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/auto.headers.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.headers.macro_example.jpg' },
    { id: 22, name: 'auto.scoreboard_constants', category: t('pluginsTable.categoryAutomation'), descriptionKey: 'pluginsTable.scoreboardConstantsDesc', color: 'from-orange-500 to-amber-500', icon: HiHashtag, dependency: '🟢', delay: 0.875, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/auto.scoreboard_constants.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.scoreboard_constants.example.jpg' },

    // Build
    { id: 18, name: 'archive', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.archiveDesc', color: 'from-gray-500 to-slate-500', icon: HiArchive, dependency: '🟢', delay: 0.9, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/archive.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/archive.output_directory.jpg' },
    { id: 19, name: 'merge_smithed_weld', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.mergeSmithedWeldDesc', color: 'from-indigo-500 to-blue-500', icon: HiLink, dependency: '🟢', delay: 0.95, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/merge_smithed_weld.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/merged_smithed_weld.output_directory.jpg' },
    { id: 20, name: 'copy_to_destination', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.copyToDestinationDesc', color: 'from-cyan-500 to-teal-500', icon: HiFolderOpen, dependency: '🟢', delay: 1.0, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/copy_to_destination.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/copy_to_destination.datapack_destination.jpg' },
    { id: 21, name: 'compute_sha1', category: t('pluginsTable.categoryBuild'), descriptionKey: 'pluginsTable.computeSha1Desc', color: 'from-green-500 to-emerald-500', icon: HiShieldCheck, dependency: '🟢', delay: 1.05, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/compute_sha1.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/compute_sha1.example.jpg' },
];

export const PluginsTable: React.FC = () => {
    const { t } = useTranslation();
    const plugins = getPlugins(t);
    const [selectedImage, setSelectedImage] = useState<{ src: string; alt: string } | null>(null);

    const dependencyLabels = {
        '🔴': t('showcase.fullyDependent'),
        '🟡': t('showcase.partlyDependent'),
        '🟢': t('showcase.independent')
    };

    return (
        <>
            {/* Table Layout */}
            <div className="overflow-x-auto rounded-xl border border-white/10 bg-slate-900/50 backdrop-blur-sm">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/10 bg-white/5">
                            <th className="p-4 text-slate-300 font-semibold w-32">{t('pluginsTable.category')}</th>
                            <th className="p-4 text-slate-300 font-semibold">{t('pluginsTable.plugin')}</th>
                            <th className="p-4 text-slate-300 font-semibold">{t('pluginsTable.description')}</th>
                            <th className="p-4 text-slate-300 font-semibold">{t('pluginsTable.image')}</th>
                            <th className="p-4 text-slate-300 font-semibold w-40">{t('pluginsTable.dependency')}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {plugins.map((plugin, index) => {
                            const Icon = plugin.icon;
                            return (
                                <motion.tr
                                    key={plugin.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: index * 0.02 }}
                                    className="hover:bg-white/5 transition-colors group"
                                >
                                    <td className="p-4">
                                        <div className="flex items-center gap-2">
                                            <Icon className={`text-lg bg-gradient-to-br ${plugin.color} bg-clip-text text-transparent`} />
                                            <span className="font-medium text-slate-300 text-sm">{plugin.category}</span>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Link
                                            to={`/markdown?src=plugins/${plugin.name}.md`}
                                            className={`${TEXT_ACCENT_HOVER} font-semibold hover:underline underline-offset-4`}
                                        >
                                            {plugin.name}
                                        </Link>
                                    </td>
                                    <td className="p-4 max-w-xs">
                                        <Link
                                            to={`/markdown?src=plugins/${plugin.name}.md`}
                                            className="text-slate-400 hover:text-slate-300 text-sm block transition-colors"
                                        >
                                            {t(plugin.descriptionKey)}
                                        </Link>
                                    </td>
                                    <td className="p-4">
                                        <button
                                            onClick={() => setSelectedImage({ src: plugin.image, alt: plugin.name })}
                                            className="block w-64 h-36 rounded-lg overflow-hidden border border-white/10 bg-slate-950 relative group-hover:border-indigo-500/30 transition-colors cursor-pointer"
                                        >
                                            <img
                                                src={plugin.image}
                                                alt={plugin.name}
                                                className="w-full h-full object-cover hover:scale-110 transition-transform duration-500"
                                            />
                                        </button>
                                    </td>
                                    <td className="p-4">
                                        <div className="flex items-center gap-2">
                                            <span className="text-lg">{plugin.dependency}</span>
                                            <span className="text-xs text-slate-400">{dependencyLabels[plugin.dependency]}</span>
                                        </div>
                                    </td>
                                </motion.tr>
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
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
                    >
                        {/* Close button */}
                        <button
                            onClick={() => setSelectedImage(null)}
                            className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors z-10"
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
                                className="w-full h-full object-contain rounded-lg shadow-2xl"
                            />
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
};
