import { motion } from 'framer-motion';
import { useState } from 'react';
import { HiClipboard, HiCheck } from 'react-icons/hi';
// Feature marks name the thing they stand for — an anvil for recipes, a chest for loot —
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

type Preview =
    | { kind: 'code'; code: string; lang: string; caption: string }
    | { kind: 'image'; src: string; caption: string }
    | { kind: 'files'; nodes: FileNode[]; code: string; lang: string; caption: string };

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
            kind: 'code',
            lang: 'python',
            caption: 'definitions/ores.py',
            code: `ORES_CONFIGS: dict[str, EquipmentsConfig | None] = {
    "steel_ingot": EquipmentsConfig(

        # Steel behaves like iron,
        equivalent_to=DefaultOre.IRON,

        # but the pickaxe lasts three times longer,
        pickaxe_durability=3 * VanillaEquipments.PICKAXE.value[DefaultOre.IRON]["durability"],

        # and it hits harder, protects more, and mines faster
        attributes={"attack_damage": 1, "armor": 0.5, "mining_efficiency": 2},
    ),
}

# Registers steel_pickaxe, steel_sword, steel_helmet, steel_block, steel_ore,
# raw_steel, steel_nugget… — 158 files in the extensive template's build
generate_everything_about_these_materials(ORES_CONFIGS)`,
        },
    },
    {
        id: 'item_models',
        icon: GiStoneBlock,
        title: t('features.itemModelsTitle'),
        description: t('features.itemModelsDesc'),
        preview: {
            kind: 'files',
            nodes: TEXTURE_FILES,
            lang: 'json',
            caption: 'models/item/electric_furnace.json',
            code: `{
  "parent": "block/orientable",
  "textures": {
    "front": "simplenergy:item/electric_furnace_front_on",
    "side": "simplenergy:item/electric_furnace_side",
    "top": "simplenergy:item/electric_furnace_top"
  }
}`,
        },
    },
    {
        id: 'recipes',
        icon: GiAnvil,
        title: t('features.recipesTitle'),
        description: t('features.recipesDesc'),
        preview: { kind: 'image', src: `${PLUGIN_IMG}/custom_recipes.smithed_recipe.jpg`, caption: 'in-game' },
    },
    {
        id: 'loot_tables',
        icon: GiChest,
        title: t('features.lootTablesTitle'),
        description: t('features.lootTablesDesc'),
        preview: { kind: 'image', src: `${PLUGIN_IMG}/datapack.loot_tables.give_all.jpg`, caption: 'function …:_give_all' },
    },
    {
        id: 'lang',
        icon: GiOpenBook,
        title: t('features.langTitle'),
        description: t('features.langDesc'),
        preview: {
            kind: 'code',
            lang: 'json',
            caption: 'lang/en_us.json',
            code: `{
  "simplenergy": " SimplEnergy",
  "simplenergy.a_better_furnace": "A Better Furnace",
  "simplenergy.a_simple_energy_storage": "A Simple Energy Storage",
  "simplenergy.a_very_fast_smelter": "A Very Fast Smelter",
  "simplenergy.advanced_battery": "Advanced Battery",
  "simplenergy.advanced_cable": "Advanced Cable",
  "simplenergy.allows_you_to_analyse_machines": "Allows you to analyse machines",
  "simplenergy.also_named_the_coal_generator": "Also named the Coal Generator",
  "simplenergy.electric_furnace": "Electric Furnace",
  "simplenergy.energy_buffer_1600_kj": "Energy buffer: 1600 kJ",
  "simplenergy.power_usage_20_kw": "Power usage: 20 kW"
}`,
        },
    },
    {
        id: 'dependencies',
        icon: GiLinkedRings,
        title: t('features.dependenciesTitle'),
        description: t('features.dependenciesDesc'),
        preview: { kind: 'image', src: `${PLUGIN_IMG}/finalyze.dependencies.ingame_errors.jpg`, caption: 'in-game' },
    }
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

const PreviewBody = ({ preview, alt }: { preview: Preview; alt: string }) => {
    if (preview.kind === 'image') {
        return (
            <div className="h-full w-full flex items-center justify-center bg-black/30 p-3">
                <img src={preview.src} alt={alt} loading="lazy" decoding="async" className="max-h-full max-w-full object-contain rounded" />
            </div>
        );
    }

    if (preview.kind === 'files') {
        return (
            <div className="h-full flex flex-col">
                <div className="p-4 border-b border-white/5 bg-black/20 flex-shrink-0">
                    <FileTree nodes={preview.nodes} />
                </div>
                <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
                    <CodeBlock code={preview.code} lang={preview.lang} />
                </div>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto custom-scrollbar">
            <CodeBlock code={preview.code} lang={preview.lang} />
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
                                    className={`w-full text-left p-4 rounded-xl transition-all duration-200 border ${isActive
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
                        <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden flex flex-col h-[30rem]">
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

                            {/* Content — a tab's preview mounts the first time it is opened, then stays */}
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
                                                <PreviewBody preview={feature.preview} alt={feature.title} />
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
