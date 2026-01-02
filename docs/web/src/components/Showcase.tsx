import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    HiCog,
    HiCheckCircle,
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
    HiX
} from 'react-icons/hi';

interface Plugin {
    id: number;
    name: string;
    category: string;
    description: string;
    color: string;
    icon: React.ComponentType<{ className?: string }>;
    dependency: '🔴' | '🟡' | '🟢';
    delay: number;
    link: string;
    image: string;
}

const plugins: Plugin[] = [
    // Core
    { id: 1, name: 'initialize', category: 'Core', description: 'Initializes the framework and sets up project metadata', color: 'from-red-500 to-orange-500', icon: HiCog, dependency: '🔴', delay: 0, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/initialize.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/initialize.source_lore.jpg' },
    { id: 2, name: 'verify_definitions', category: 'Core', description: 'Validates the structure of definitions and checks consistency', color: 'from-green-500 to-emerald-500', icon: HiCheckCircle, dependency: '🔴', delay: 0.05, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/verify_definitions.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/verify_definitions.json_dump.jpg' },

    // Resource Pack
    { id: 3, name: 'resource_pack.sounds', category: 'Resource Pack', description: 'Processes sound files and generates sounds.json automatically', color: 'from-purple-500 to-pink-500', icon: HiVolumeUp, dependency: '🟡', delay: 0.1, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/resource_pack.sounds.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.sounds.result.jpg' },
    { id: 4, name: 'resource_pack.item_models', category: 'Resource Pack', description: 'Automatically generates item and block models', color: 'from-blue-500 to-cyan-500', icon: HiColorSwatch, dependency: '🟡', delay: 0.15, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/resource_pack.item_models.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.item_models.pattern_detection.jpg' },
    { id: 5, name: 'resource_pack.check_power_of_2', category: 'Resource Pack', description: 'Validates that textures use power-of-2 resolutions', color: 'from-indigo-500 to-purple-500', icon: HiPhotograph, dependency: '🟢', delay: 0.2, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/resource_pack.check_power_of_2.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/resource_pack.check_power_of_2.warning.jpg' },

    // Recipes & Custom Content
    { id: 6, name: 'custom_recipes', category: 'Recipes', description: 'Generates vanilla, smithed, furnace, and pulverizer recipes', color: 'from-orange-500 to-red-500', icon: HiBeaker, dependency: '🔴', delay: 0.25, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/custom_recipes.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/custom_recipes.smithed_recipe.jpg' },
    { id: 7, name: 'custom_paintings', category: 'Custom Content', description: 'Creates custom painting variants', color: 'from-pink-500 to-rose-500', icon: HiPhotograph, dependency: '🔴', delay: 0.3, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/custom_paintings.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/custom_paintings.placed_painting.jpg' },

    // Documentation
    { id: 8, name: 'ingame_manual', category: 'Documentation', description: 'Generates an interactive in-game manual with documentation', color: 'from-amber-500 to-yellow-500', icon: HiBookOpen, dependency: '🔴', delay: 0.35, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/ingame_manual.md', image: 'https://i.imgur.com/dtuAG99.gif' },

    // Datapack
    { id: 9, name: 'datapack.loading', category: 'Datapack', description: 'Sets up the loading system with versioning', color: 'from-cyan-500 to-blue-500', icon: HiLightningBolt, dependency: '🟡', delay: 0.4, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.loading.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loading.load_messages.jpg' },
    { id: 10, name: 'datapack.custom_blocks', category: 'Datapack', description: 'Implements placement, destruction, and interaction for custom blocks', color: 'from-teal-500 to-emerald-500', icon: HiCube, dependency: '🔴', delay: 0.45, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.custom_blocks.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.custom_blocks.stats.jpg' },
    { id: 11, name: 'datapack.loot_tables', category: 'Datapack', description: 'Generates loot tables and give-all functionality', color: 'from-green-500 to-lime-500', icon: HiGift, dependency: '🔴', delay: 0.5, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.loot_tables.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.loot_tables.give_all.jpg' },
    { id: 12, name: 'datapack.sorters', category: 'Datapack', description: 'Generates sorting functions for NBT lists', color: 'from-violet-500 to-purple-500', icon: HiSortAscending, dependency: '🟢', delay: 0.55, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/datapack.sorters.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/datapack.sorters.registry.jpg' },

    // Finalization
    { id: 13, name: 'finalyze.custom_blocks_ticking', category: 'Finalization', description: 'Configures the ticking system for custom blocks', color: 'from-rose-500 to-pink-500', icon: HiClock, dependency: '🔴', delay: 0.6, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.custom_blocks_ticking.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.custom_blocks_ticking.timers.jpg' },
    { id: 14, name: 'finalyze.basic_datapack_structure', category: 'Finalization', description: 'Creates the timing structure (tick, second, minute)', color: 'from-slate-500 to-gray-500', icon: HiCollection, dependency: '🟡', delay: 0.65, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.basic_datapack_structure.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.basic_datapack_structure.timers.jpg' },
    { id: 15, name: 'finalyze.dependencies', category: 'Finalization', description: 'Manages external library dependencies', color: 'from-blue-500 to-indigo-500', icon: HiClipboardList, dependency: '🔴', delay: 0.7, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.dependencies.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.dependencies.ingame_errors.jpg' },
    { id: 16, name: 'finalyze.check_unused_textures', category: 'Finalization', description: 'Identifies unused textures in the resource pack', color: 'from-yellow-500 to-orange-500', icon: HiEye, dependency: '🟢', delay: 0.75, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/finalyze.check_unused_textures.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/finalyze.check_unused_textures.warnings.jpg' },

    // Automation
    { id: 17, name: 'auto.lang_file', category: 'Automation', description: 'Automatically generates language files', color: 'from-emerald-500 to-teal-500', icon: HiGlobe, dependency: '🟢', delay: 0.8, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/auto.lang_file.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.lang_file.en_us_example.jpg' },
    { id: 18, name: 'auto.headers', category: 'Automation', description: 'Adds automatic headers to mcfunction files', color: 'from-purple-500 to-indigo-500', icon: HiCode, dependency: '🟢', delay: 0.85, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/auto.headers.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.headers.macro_example.jpg' },

    // Build
    { id: 19, name: 'archive', category: 'Build', description: 'Creates zip archives of datapacks and resource packs', color: 'from-gray-500 to-slate-500', icon: HiArchive, dependency: '🟢', delay: 0.9, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/archive.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/archive.output_directory.jpg' },
    { id: 20, name: 'merge_smithed_weld', category: 'Build', description: 'Merges datapacks and resource packs with libraries', color: 'from-indigo-500 to-blue-500', icon: HiLink, dependency: '🟢', delay: 0.95, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/merge_smithed_weld.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/merged_smithed_weld.output_directory.jpg' },
    { id: 21, name: 'copy_to_destination', category: 'Build', description: 'Copies generated packs to destination folders', color: 'from-cyan-500 to-teal-500', icon: HiFolderOpen, dependency: '🟢', delay: 1.0, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/copy_to_destination.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/copy_to_destination.datapack_destination.jpg' },
    { id: 22, name: 'compute_sha1', category: 'Build', description: 'Computes SHA1 hashes for all zip files', color: 'from-green-500 to-emerald-500', icon: HiShieldCheck, dependency: '🟢', delay: 1.05, link: 'https://github.com/Stoupy51/StewBeet/blob/main/docs/plugins/compute_sha1.md', image: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/compute_sha1.example.jpg' },
];

const dependencyLabels = {
    '🔴': 'Fully dependent',
    '🟡': 'Partly dependent',
    '🟢': 'Independent'
};

export const Showcase: React.FC = () => {
    const containerRef = useRef<HTMLDivElement>(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"]
    });

    const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
    const y = useTransform(scrollYProgress, [0, 0.2], [100, 0]);
    
    const [selectedImage, setSelectedImage] = useState<{ src: string; alt: string } | null>(null);

    return (
        <section
            id="plugins"
            ref={containerRef}
            className="py-24 px-4 bg-gradient-to-b from-slate-950 to-slate-900 relative overflow-hidden"
        >
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/10 rounded-full blur-[100px]" />
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-500/10 rounded-full blur-[100px]" />
            </div>

            <motion.div
                style={{ opacity, y }}
                className="max-w-7xl mx-auto relative z-10"
            >
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-purple-200">
                        StewBeet Plugins
                    </h2>
                    <p className="text-slate-400 text-lg max-w-3xl mx-auto mb-8">
                        Over 20 plugins to automate every aspect of your datapack.<br />
                        <span className="text-sm">Legend: <span className="text-red-400">🔴 Fully dependent</span> <span className="text-yellow-400 ml-2">🟡 Partly dependent</span> <span className="text-green-400 ml-2">🟢 Independent</span></span>
                    </p>
                </motion.div>

                {/* Table Layout */}
                <div className="overflow-x-auto rounded-xl border border-white/10 bg-slate-900/50 backdrop-blur-sm">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-white/10 bg-white/5">
                                <th className="p-4 text-slate-300 font-semibold w-32">Category</th>
                                <th className="p-4 text-slate-300 font-semibold">Plugin</th>
                                <th className="p-4 text-slate-300 font-semibold">Description</th>
                                <th className="p-4 text-slate-300 font-semibold">Image</th>
                                <th className="p-4 text-slate-300 font-semibold w-40">Dependency</th>
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
                                                className="text-indigo-400 hover:text-indigo-300 font-semibold hover:underline underline-offset-4"
                                            >
                                                {plugin.name}
                                            </Link>
                                        </td>
                                        <td className="p-4 max-w-xs">
                                            <Link
                                                to={`/markdown?src=plugins/${plugin.name}.md`}
                                                className="text-slate-400 hover:text-slate-300 text-sm block transition-colors"
                                            >
                                                {plugin.description}
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
            </motion.div>

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
        </section>
    );
};
