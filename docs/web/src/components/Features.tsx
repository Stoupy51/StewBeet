import { motion } from 'framer-motion';
import { useState } from 'react';
import {
    HiCube,
    HiTemplate,
    HiClock,
    HiBookOpen,
    HiGlobe,
    HiBeaker,
    HiClipboard,
    HiCheck,
    HiCode
} from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useShiki } from '../hooks/useShiki';
import { ACCENT_BORDER_HOVER, ICON_ACCENT, TEXT_ACCENT, STEP_ACTIVE, ICON_ACTIVE, TEXT_ACTIVE_SUBTLE } from '../theme';

interface Feature {
    id: string;
    icon: React.ComponentType<{ className?: string }>;
    title: string;
    description: string;
    previewType: 'code' | 'image';
    previewContent: string;
    previewLang?: string;
}

const getFeatures = (t: (key: string) => string): Feature[] => [
    {
        id: 'item_models',
        icon: HiTemplate,
        title: t('features.itemModelsTitle'),
        description: t('features.itemModelsDesc'),
            previewType: 'code',
            previewLang: 'json',
        previewContent: `{
  "parent": "block/orientable",
  "textures": {
    "front": "simplenergy:item/electric_furnace_front_on",
    "side": "simplenergy:item/electric_furnace_side",
    "top": "simplenergy:item/electric_furnace_top"
  }
}`
    },
    {
        id: 'loading',
        icon: HiClock,
        title: t('features.loadingTitle'),
        description: t('features.loadingDesc'),
        previewType: 'code',
        previewLang: 'mcfunction',
        previewContent: `#> stardust:v4.0.0/tick
#
# @within	stardust:v4.0.0/load/tick_verification
#

# Timers
scoreboard players add #tick_2 stardust.data 1
scoreboard players add #second stardust.data 1
scoreboard players add #second_5 stardust.data 1
scoreboard players add #minute stardust.data 1
execute if score #tick_2 stardust.data matches 3.. run function stardust:v4.0.0/tick_2
execute if score #second stardust.data matches 20.. run function stardust:v4.0.0/second
execute if score #second_5 stardust.data matches 90 run function stardust:v4.0.0/second_5
execute if score #minute stardust.data matches 1200.. run function stardust:v4.0.0/minute`
    },
    {
        id: 'loot_tables',
        icon: HiCube,
        title: t('features.lootTablesTitle'),
        description: t('features.lootTablesDesc'),
        previewType: 'code',
        previewLang: 'json',
        previewContent: `{
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:furnace",
          "functions": [
            {
              "function": "minecraft:set_components",
              "components": {
                "minecraft:custom_data": {
                  "energy": {"usage": 20, "max_storage": 1600},
                  "simplenergy": {"electric_furnace": true},
                  "smithed": {"ignore": {"functionality": true,"crafting": true}}
                },
                "minecraft:lore": [
                  {"translate": "simplenergy.power_usage_20_kw", "italic": false, "color": "gray"},
                  {"translate": "simplenergy.energy_buffer_1600_kj", "italic": false, "color": "gray"},
                  ["",{"text": "I","color": "white","italic": false,"font": "simplenergy:icons"},{"translate": "simplenergy","italic": true,"color": "blue"}]
                ],
                "minecraft:item_model": "simplenergy:electric_furnace",
                "minecraft:item_name": {"translate": "simplenergy.electric_furnace"},
                "minecraft:container": [{"slot": 0,"item": {"id": "minecraft:stone","count": 1,"components": {"minecraft:custom_data": {"smithed": {"block": {"id": "simplenergy:electric_furnace","from": "simplenergy"}}}}}}],
                "minecraft:tooltip_display": {"hidden_components": ["minecraft:container"]}
              }
            }
]}]}]}
`    },
    {
        id: 'manual',
        icon: HiBookOpen,
        title: t('features.manualTitle'),
        description: t('features.manualDesc'),
        previewType: 'image',
        previewContent: 'https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/docs/plugins/img/ingame_manual.gif'
    },
    {
        id: 'lang',
        icon: HiGlobe,
        title: t('features.langTitle'),
        description: t('features.langDesc'),
        previewType: 'code',
        previewLang: 'json',
        previewContent: `{
	"simplenergy": " SimplEnergy",
	"simplenergy.0_kw_at_y50_2_kw_at_y60_20_kw_at_y150": "\\n(0 kW at y=50, 2 kW at y=60, ..., 20 kW at y=150)",
	"simplenergy.a_better_furnace": "A Better Furnace",
	"simplenergy.a_diagnostic_tool_for_energy_systems": "A diagnostic tool for energy systems.",
	"simplenergy.a_simple_energy_storage": "A Simple Energy Storage",
	"simplenergy.a_very_fast_smelter": "A Very Fast Smelter",
	"simplenergy.advanced_battery": "Advanced Battery",
	"simplenergy.advanced_cable": "Advanced Cable",
	"simplenergy.advanced_electric_smelting_station": "Advanced electric smelting station.",
	"simplenergy.advanced_energy_storage_device": "Advanced energy storage device.",
	"simplenergy.advanced_generator_powered_by_redstone_dust_and_blocks": "\\nAdvanced generator powered by redstone dust and blocks",
	"simplenergy.allows_you_to_analyse_machines": "Allows you to analyse machines",
	"simplenergy.allows_you_to_switch_batteries_states": "Allows you to switch batteries states",
	"simplenergy.also_named_the_coal_generator": "Also named the Coal Generator",
	"simplenergy.balances_energy_storage_with_adjacent_advanced_batteries": "\\nBalances energy storage with adjacent advanced batteries",
	"simplenergy.balances_energy_storage_with_adjacent_cauldron_generators": "\\nBalances energy storage with adjacent cauldron generators",
}`
    },
    {
        id: 'custom_blocks',
        icon: HiBeaker,
        title: t('features.customBlocksTitle'),
        description: t('features.customBlocksDesc'),
        previewType: 'code',
        previewLang: 'python',
        previewContent: `Block(
    id="stardust_ore",
    vanilla_block=VanillaBlockForOres,
    # Mining drops 2-8 fragments (fortune/silk touch handled automatically)
    no_silk_touch_drop=NoSilkTouchDrop(
        id="stardust_fragment",
        count={"min": 2, "max": 8}
    ),
    # Smelting and blasting recipes for ore to 4x fragments
    recipes=[
        SmeltingRecipe(
            result_count=4, experience=0.1, cookingtime=200, category="blocks",
            ingredient=Ingr("stardust_ore"), result=Ingr("stardust_fragment")
        ),
        BlastingRecipe(
            result_count=4, experience=0.1, cookingtime=100, category="blocks",
            ingredient=Ingr("stardust_ore"), result=Ingr("stardust_fragment")
        ),
    ],
)`
    }
];

const CodeBlock = ({ code, lang }: { code: string; lang?: string }) => {
    const [copied, setCopied] = useState(false);
    const highlighted = useShiki(code, lang || 'text', 'dark-plus');

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
                    style={{
                        fontSize: '0.875rem',
                        lineHeight: '1.625',
                    }}
                    className="[&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-4 [&>pre]:!font-mono"
                />
            ) : (
                <pre className="m-0 p-4 bg-transparent text-slate-300 text-sm leading-relaxed font-mono overflow-auto">
                    <code>{code}</code>
                </pre>
            )}
        </div>
    );
};

export const Features: React.FC = () => {
    const { t } = useTranslation();
    const features = getFeatures(t);
    const [activeFeature, setActiveFeature] = useState<Feature>(features[0]);

    return (
        <section id="features" className="py-12 px-4 bg-[#0a0a0a] relative overflow-hidden">
            <div className="max-w-7xl mx-auto relative z-10">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">
                        {t('features.title')} <span className={TEXT_ACCENT}>{t('features.titleHighlight')}</span>
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
                                <motion.button
                                    key={feature.id}
                                    onClick={() => setActiveFeature(feature)}
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
                                            <p className={`text-sm mt-1 ${isActive ? TEXT_ACTIVE_SUBTLE : 'text-slate-500'}`}>
                                                {feature.description}
                                            </p>
                                        </div>
                                    </div>
                                </motion.button>
                            );
                        })}
                    </div>

                    {/* Preview Window */}
                    <div className="lg:col-span-7 sticky top-24">
                        <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden min-h-[350px] flex flex-col">
                            {/* Window Header */}
                            <div className="bg-[#2d2d2d] px-4 py-3 flex items-center justify-between border-b border-white/5">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                                    <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                                    <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                                </div>
                                <div className="text-xs text-slate-400 font-mono flex items-center gap-2">
                                    {activeFeature.previewType === 'code' && <HiCode className={ICON_ACCENT} />}
                                    {activeFeature.previewLang ? `preview.${activeFeature.previewLang}` : 'preview'}
                                </div>
                                <div className="w-16" /> {/* Spacer for centering */}
                            </div>

                            {/* Content — all tabs rendered in HTML for crawlers, active one shown via CSS */}
                            <div className="flex-1 overflow-hidden relative bg-[#1e1e1e]">
                                {features.map((feature) => {
                                    const isActive = activeFeature.id === feature.id;
                                    return (
                                        <motion.div
                                            key={feature.id}
                                            initial={false}
                                            animate={{ opacity: isActive ? 1 : 0, y: isActive ? 0 : 10 }}
                                            transition={{ duration: 0.2 }}
                                            className="h-full w-full"
                                            style={{ display: isActive ? 'block' : 'none' }}
                                            aria-hidden={!isActive}
                                        >
                                            {feature.previewType === 'code' ? (
                                                <div className="overflow-auto custom-scrollbar" style={{ maxHeight: '500px' }}>
                                                    <CodeBlock
                                                        code={feature.previewContent}
                                                        lang={feature.previewLang}
                                                    />
                                                </div>
                                            ) : (
                                                <div className="h-full w-full flex items-center justify-center bg-black/20">
                                                    <img
                                                        src={feature.previewContent}
                                                        alt={feature.title}
                                                        className="max-w-full object-contain"
                                                        style={{ maxHeight: '500px' }}
                                                    />
                                                </div>
                                            )}
                                        </motion.div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Integration Badges */}
                        <div className="mt-8">
                            <p className="text-sm text-slate-500 mb-4 font-mono uppercase tracking-wider">{t('features.integrations')}</p>
                            <div className="flex flex-wrap gap-3">
                                {[
                                    { name: 'Smithed Custom Blocks', url: 'https://wiki.smithed.dev/libraries/custom-block/' },
                                    { name: 'Smithed Crafter', url: 'https://wiki.smithed.dev/libraries/crafter/' },
                                    { name: 'Furnace NBT Recipes', url: 'https://github.com/Stoupy51/FurnaceNbtRecipes/' },
                                    { name: 'Smart Ore Generation', url: 'https://github.com/Stoupy51/SmartOreGeneration' },
                                    { name: 'Bookshelf', url: 'https://github.com/mcbookshelf/bookshelf' },
                                    { name: 'ItemIO', url: 'https://github.com/edayot/ItemIO' },
                                    { name: 'Common Signals', url: 'https://github.com/Stoupy51/CommonSignals' },
                                    { name: '...', url: '' }
                                ].map((lib, idx) => (
                                    <a
                                        key={idx}
                                        href={lib.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className={`px-3 py-1.5 bg-slate-900 border border-white/10 rounded-md text-xs text-slate-400 font-mono ${ACCENT_BORDER_HOVER} hover:text-indigo-400 transition-colors cursor-pointer`}
                                    >
                                        {lib.name}
                                    </a>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
