import { motion, AnimatePresence } from 'framer-motion';
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
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface Feature {
    id: string;
    icon: React.ComponentType<{ className?: string }>;
    title: string;
    description: string;
    previewType: 'code' | 'image';
    previewContent: string;
    previewLang?: string;
}

const features: Feature[] = [
    {
        id: 'item_models',
        icon: HiTemplate,
        title: 'Auto Item Models',
        description: 'Automatically generates item and block models from texture patterns. Detects cube, cake, orientable patterns and more. Recognizes _on suffix to create powered/unpowered state models.',
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
        title: 'Datapack Loading',
        description: 'Sets up timing infrastructure with tick, second, minute functions. Includes version checking and LanternLoad compatibility.',
        previewType: 'code',
        previewLang: 'hs',
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
        title: 'Loot Tables & Give',
        description: 'Auto-generated loot tables for every defined item along with a convenient _give_all function for testing.',
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
        title: 'In-Game Manual',
        description: 'Automatically generated interactive manual with item documentation, crafting recipes, and clickable navigation.',
        previewType: 'image',
        previewContent: 'https://i.imgur.com/dtuAG99.gif'
    },
    {
        id: 'lang',
        icon: HiGlobe,
        title: 'Auto Lang Files',
        description: 'Automatically extracts text components from your code and generates en_us.json translation files.',
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
        title: 'Custom Blocks',
        description: 'Full custom block system with placement, destruction, ore drops (fortune/silk touch), and Smithed integration.',
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
            <SyntaxHighlighter
                language={lang || 'text'}
                style={vscDarkPlus}
                customStyle={{
                    margin: 0,
                    padding: '1rem',
                    background: 'transparent',
                    fontSize: '0.875rem',
                    lineHeight: '1.625'
                }}
                codeTagProps={{
                    style: {
                        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace'
                    }
                }}
            >
                {code}
            </SyntaxHighlighter>
        </div>
    );
};

export const Features: React.FC = () => {
    const [activeFeature, setActiveFeature] = useState<Feature>(features[0]);

    return (
        <section id="features" className="py-24 px-4 bg-[#0a0a0a] relative overflow-hidden">
            <div className="max-w-7xl mx-auto relative z-10">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">
                        Powerful <span className="text-indigo-400">Automation</span>
                    </h2>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                        StewBeet handles the repetitive parts of datapack creation so you can focus on the mechanics.
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
                                        ? 'bg-indigo-500/10 border-indigo-500/50 shadow-lg shadow-indigo-500/10'
                                        : 'bg-transparent border-transparent hover:bg-white/5'
                                        }`}
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`p-2 rounded-lg ${isActive ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                                            <Icon className="text-xl" />
                                        </div>
                                        <div>
                                            <h3 className={`font-bold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                                                {feature.title}
                                            </h3>
                                            <p className={`text-sm mt-1 ${isActive ? 'text-indigo-200' : 'text-slate-500'}`}>
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
                        <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden min-h-[500px] flex flex-col">
                            {/* Window Header */}
                            <div className="bg-[#2d2d2d] px-4 py-3 flex items-center justify-between border-b border-white/5">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                                    <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                                    <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                                </div>
                                <div className="text-xs text-slate-400 font-mono flex items-center gap-2">
                                    {activeFeature.previewType === 'code' && <HiCode className="text-indigo-400" />}
                                    {activeFeature.previewLang ? `preview.${activeFeature.previewLang}` : 'preview'}
                                </div>
                                <div className="w-16" /> {/* Spacer for centering */}
                            </div>

                            {/* Content */}
                            <div className="flex-1 overflow-hidden relative bg-[#1e1e1e]">
                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={activeFeature.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        transition={{ duration: 0.2 }}
                                        className="h-full w-full"
                                    >
                                        {activeFeature.previewType === 'code' ? (
                                            <div className="h-full overflow-auto custom-scrollbar">
                                                <CodeBlock
                                                    code={activeFeature.previewContent}
                                                    lang={activeFeature.previewLang}
                                                />
                                            </div>
                                        ) : (
                                            <div className="h-full w-full flex items-center justify-center bg-black/20">
                                                <img
                                                    src={activeFeature.previewContent}
                                                    alt={activeFeature.title}
                                                    className="max-w-full max-h-full object-contain"
                                                />
                                            </div>
                                        )}
                                    </motion.div>
                                </AnimatePresence>
                            </div>
                        </div>

                        {/* Integration Badges */}
                        <div className="mt-8">
                            <p className="text-sm text-slate-500 mb-4 font-mono uppercase tracking-wider">Integrations</p>
                            <div className="flex flex-wrap gap-3">
                                {[
                                    { name: 'Smithed Custom Blocks', url: 'https://wiki.smithed.dev/libraries/custom-block/' },
                                    { name: 'Smithed Crafter', url: 'https://wiki.smithed.dev/libraries/crafter/' },
                                    { name: 'Furnace NBT Recipes', url: 'https://github.com/Stoupy51/FurnaceNbtRecipes/' },
                                    { name: 'Smart Ore Generation', url: 'https://github.com/Stoupy51/SmartOreGeneration' },
                                    { name: 'Bookshelf', url: 'https://github.com/mcbookshelf/bookshelf' },
                                    { name: 'ItemIO', url: 'https://github.com/edayot/ItemIO' },
                                    { name: 'Common Signals', url: 'https://github.com/Stoupy51/CommonSignals' }
                                ].map((lib, idx) => (
                                    <a
                                        key={idx}
                                        href={lib.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="px-3 py-1.5 bg-slate-900 border border-white/10 rounded-md text-xs text-slate-400 font-mono hover:border-indigo-500/50 hover:text-indigo-400 transition-colors cursor-pointer"
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
