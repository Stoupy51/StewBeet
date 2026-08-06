import { motion } from 'framer-motion';
import { useState } from 'react';
import { HiClipboard, HiCheck } from 'react-icons/hi';
// Feature marks name the thing they stand for: an anvil for recipes, a chest for loot
// instead of the interchangeable cube/sparkle/bolt set every framework site draws from.
import {
    GiMineralPearls,
    GiStoneBlock,
    GiAnvil,
    GiChest,
    GiOpenBook,
    GiLinkedRings,
} from 'react-icons/gi';
import { useTranslation } from '../i18n/useTranslation';
import { useShiki } from '../hooks/useShiki';
import { FileTree, type FileNode } from './FileTree';
import { ICON_ACTIVE, STEP_ACTIVE, TEXT_ACTIVE_SUBTLE } from '../theme';

const PLUGIN_IMG = '/img';

/** A labelled code sample inside a preview. The label sits above it as a caption. */
interface Snippet {
    lang: string;
    code: string;
    label?: string;
}

interface Preview {
    /** Filename or context shown in the window's title bar. */
    caption: string;
    /** Screenshot or generated artefact, rendered above everything else. */
    image?: { src: string; alt: string };
    /** Files the author drops in, rendered above the snippets. */
    nodes?: FileNode[];
    snippets?: Snippet[];
}

interface Feature {
    id: string;
    icon: React.ComponentType<{ className?: string }>;
    title: string;
    description: string;
    preview: Preview;
}

/** Textures a datapack author drops in, and the model StewBeet infers from their names. */
const TEXTURE_FILES: FileNode[] = [
    {
        name: 'assets/textures/',
        children: [
            { name: 'electric_furnace_top.png', note: 'top face' },
            { name: 'electric_furnace_side.png', note: 'sides' },
            { name: 'electric_furnace_front.png', note: 'front face' },
            { name: 'electric_furnace_front_on.png', note: 'powered state' },
        ],
    },
];

const getFeatures = (t: (key: string) => string): Feature[] => [
    {
        id: 'materials',
        icon: GiMineralPearls,
        title: t('features.materialsTitle'),
        description: t('features.materialsDesc'),
        preview: {
            caption: 'definitions/ores.py',
            image: { src: `${PLUGIN_IMG}/material_tier.png`, alt: t('features.materialsImageAlt') },
            snippets: [{
                lang: 'python',
                label: t('features.materialsSnippetLabel'),
                code: `DIAMOND_PICKAXE = VanillaEquipments.PICKAXE.value[DefaultOre.DIAMOND]

ORES_CONFIGS: dict[str, EquipmentsConfig | None] = {
    "solarium_ingot": EquipmentsConfig(
        # Solarium behaves like diamond,
        equivalent_to=DefaultOre.DIAMOND,
        # but the pickaxe lasts three times longer,
        pickaxe_durability=3 * DIAMOND_PICKAXE["durability"],
        # and it hits harder, protects more, mines faster
        attributes={"attack_damage": 1, "armor": 0.5},
    ),
}
generate_everything_about_these_materials(ORES_CONFIGS)`,
            }],
        },
    },
    {
        id: 'item_models',
        icon: GiStoneBlock,
        title: t('features.itemModelsTitle'),
        description: t('features.itemModelsDesc'),
        preview: {
            caption: 'models/item/electric_furnace{,_on}.json',
            nodes: TEXTURE_FILES,
            snippets: [
                {
                    lang: 'json',
                    label: 'electric_furnace.json',
                    code: `{
  "parent": "block/orientable",
  "textures": {
    "front": "simplenergy:item/electric_furnace_front",
    "side": "simplenergy:item/electric_furnace_side",
    "top": "simplenergy:item/electric_furnace_top"
  }
}`,
                },
                {
                    lang: 'json',
                    label: t('features.itemModelsOnLabel'),
                    code: `{
  "parent": "block/orientable",
  "textures": {
    "front": "simplenergy:item/electric_furnace_front_on",
    "side": "simplenergy:item/electric_furnace_side",
    "top": "simplenergy:item/electric_furnace_top"
  }
}`,
                },
            ],
        },
    },
    {
        id: 'recipes',
        icon: GiAnvil,
        title: t('features.recipesTitle'),
        description: t('features.recipesDesc'),
        preview: {
            caption: 'calls/smithed_crafter/shapeless_recipes.mcfunction',
            snippets: [{
                lang: 'mcfunction',
                label: t('features.recipesSnippetLabel'),
                code: `#> stardust:calls/smithed_crafter/shapeless_recipes
#
# @within	#smithed.crafter:event/shapeless_recipes
#

# The backslashes are ours so it fits: the real file is one line per recipe.
execute \\
  if score @s smithed.data matches 0 \\
  store result score @s smithed.data \\
  if score count smithed.data matches 2 \\
  if data storage smithed.crafter:input {"recipe": [ \\
    {"id": "minecraft:iron_ingot", "count": 1}, \\
    {"components": {"minecraft:custom_data": \\
      {"stardust": {"stardust_fragment": true}}}, "count": 8} \\
  ]} \\
  run function stardust:calls/smithed_crafter/apply_recipe \\
  {"command":"loot replace block ~ ~ ~ container.16 loot
   stardust:i/stardust_ingot"}`,
            }],
        },
    },
    {
        id: 'loot_tables',
        icon: GiChest,
        title: t('features.lootTablesTitle'),
        description: t('features.lootTablesDesc'),
        preview: {
            caption: 'function ...:_give_all',
            image: { src: `${PLUGIN_IMG}/datapack.loot_tables.give_all.jpg`, alt: t('features.lootTablesTitle') },
        },
    },
    {
        id: 'lang',
        icon: GiOpenBook,
        title: t('features.langTitle'),
        description: t('features.langDesc'),
        preview: {
            caption: 'lang/en_us.json',
            snippets: [
                {
                    lang: 'mcfunction',
                    label: t('features.langBeforeLabel'),
                    code: `tellraw @s [{text:"\\n[Datapack Energy Stats]",color:"yellow"}]
tellraw @s ["",{text:"Entities: ",color:"gray"}, \\
    {score:{name:"#entities",objective:"simplenergy.data"},color:"gold"}]`,
                },
                {
                    lang: 'mcfunction',
                    label: t('features.langAfterLabel'),
                    code: `tellraw @s [{"translate":"simplenergy.datapack_energy_stats",color:"yellow"}]
tellraw @s ["",{"translate":"simplenergy.entities",color:"gray"}, \\
    {score:{name:"#entities",objective:"simplenergy.data"},color:"gold"}]`,
                },
                {
                    lang: 'json',
                    label: t('features.langFileLabel'),
                    code: `{
  "simplenergy.datapack_energy_stats": "[Datapack Energy Stats]",
  "simplenergy.entities": "Entities: ",
  "simplenergy.electric_furnace": "Electric Furnace",
  "simplenergy.energy_buffer_1600_kj": "Energy buffer: 1600 kJ"
}`,
                },
            ],
        },
    },
    {
        id: 'dependencies',
        icon: GiLinkedRings,
        title: t('features.dependenciesTitle'),
        description: t('features.dependenciesDesc'),
        preview: {
            caption: 'in-game',
            image: { src: `${PLUGIN_IMG}/finalyze.dependencies.ingame_errors.jpg`, alt: t('features.dependenciesTitle') },
        },
    },
];

const CodeBlock = ({ code, lang }: { code: string; lang: string }) => {
    const [copied, setCopied] = useState(false);
    const highlighted = useShiki(code, lang, 'dark-plus');

    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group">
            <button
                onClick={handleCopy}
                className="absolute top-2 right-2 p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all opacity-0 group-hover:opacity-100 z-10"
                title="Copy code"
            >
                {copied ? <HiCheck className="text-green-400" /> : <HiClipboard />}
            </button>
            {highlighted ? (
                <div
                    dangerouslySetInnerHTML={{ __html: highlighted }}
                    style={{ fontSize: '0.8125rem', lineHeight: '1.6' }}
                    className="[&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-4 [&>pre]:!font-mono [&>pre]:!overflow-x-auto"
                />
            ) : (
                <pre className="m-0 p-4 bg-transparent text-slate-300 text-[0.8125rem] leading-[1.6] font-mono overflow-x-auto">
                    <code>{code}</code>
                </pre>
            )}
        </div>
    );
};

const PreviewBody = ({ preview }: { preview: Preview }) => {
    // A screenshot that is the whole preview should fill the panel; one sharing the panel
    // with code has to leave room for it. Capping both shrank the screenshot-only previews.
    const imageOnly = !preview.nodes && !preview.snippets?.length;

    return (
        <div className={`h-full custom-scrollbar ${imageOnly ? 'flex' : 'overflow-y-auto'}`}>
            {preview.image && (
                <div className={`flex items-center justify-center bg-black/30 p-3 ${imageOnly ? 'flex-1 min-h-0' : ''}`}>
                    <img
                        src={preview.image.src}
                        alt={preview.image.alt}
                        loading="lazy"
                        decoding="async"
                        className={`max-w-full object-contain rounded-panel ${imageOnly ? 'max-h-full' : 'max-h-52'}`}
                    />
                </div>
            )}

            {preview.nodes && (
                <div className="p-4 border-b border-white/5 bg-black/20">
                    <FileTree nodes={preview.nodes} />
                </div>
            )}

            {preview.snippets?.map((snippet, index) => (
                <div key={snippet.label ?? index} className={index > 0 ? 'border-t border-white/5' : undefined}>
                    {snippet.label && (
                        <p className="px-4 pt-3 text-xs font-mono text-slate-400">{snippet.label}</p>
                    )}
                    <CodeBlock code={snippet.code} lang={snippet.lang} />
                </div>
            ))}
        </div>
    );
};

export const Features: React.FC = () => {
    const { t } = useTranslation();
    const features = getFeatures(t);
    const [activeFeature, setActiveFeature] = useState<Feature>(features[0]);
    // Track which tabs have been activated so previews only mount when first visited
    const [rendered, setRendered] = useState<Set<string>>(() => new Set([features[0].id]));

    const handleFeatureSelect = (feature: Feature) => {
        setActiveFeature(feature);
        setRendered(prev => {
            if (prev.has(feature.id)) return prev;
            const next = new Set(prev);
            next.add(feature.id);
            return next;
        });
    };

    return (
        <section id="features" className="py-20 px-4 relative overflow-hidden bg-gradient-to-b from-slate-900 via-[#0a0a0a] to-[#0a0a0a]">
            <div className="max-w-7xl mx-auto relative z-10">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">
                        {t('features.title')}
                    </h2>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                        {t('features.subtitle')}
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                    {/* Feature List */}
                    <div className="lg:col-span-5 space-y-2">
                        {features.map((feature) => {
                            const Icon = feature.icon;
                            const isActive = activeFeature.id === feature.id;
                            return (
                                <button
                                    key={feature.id}
                                    onClick={() => handleFeatureSelect(feature)}
                                    className={`w-full text-left select-text p-4 rounded-panel transition-all duration-200 border ${isActive
                                        ? STEP_ACTIVE
                                        : 'bg-transparent border-transparent hover:bg-white/5'
                                        }`}
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`p-2 rounded-lg ${isActive ? ICON_ACTIVE : 'bg-slate-800 text-slate-400'}`}>
                                            <Icon className="text-xl" />
                                        </div>
                                        <div>
                                            <h3 className={`font-bold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                                                {feature.title}
                                            </h3>
                                            <p className={`text-sm mt-1 ${isActive ? TEXT_ACTIVE_SUBTLE : 'text-slate-400'}`}>
                                                {feature.description}
                                            </p>
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    {/* Preview Window */}
                    <div className="lg:col-span-7 lg:sticky lg:top-24">
                        <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden flex flex-col h-[34rem]">
                            {/* Window Header */}
                            <div className="bg-[#2d2d2d] px-4 py-3 flex items-center justify-between border-b border-white/5 flex-shrink-0">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                                    <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                                    <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                                </div>
                                <div className="text-xs text-slate-400 font-mono truncate ml-4">
                                    {activeFeature.preview.caption}
                                </div>
                            </div>

                            {/* Content: a tab's preview mounts the first time it is opened, then stays */}
                            <div className="flex-1 min-h-0 relative bg-[#1e1e1e]">
                                {features.map((feature) => {
                                    const isActive = activeFeature.id === feature.id;
                                    return (
                                        <motion.div
                                            key={feature.id}
                                            initial={false}
                                            animate={{ opacity: isActive ? 1 : 0 }}
                                            transition={{ duration: 0.2 }}
                                            className="h-full w-full"
                                            style={{ display: isActive ? 'block' : 'none' }}
                                            aria-hidden={!isActive}
                                        >
                                            {rendered.has(feature.id) && (
                                                <PreviewBody preview={feature.preview} />
                                            )}
                                        </motion.div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
