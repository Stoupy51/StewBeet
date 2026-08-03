import { motion } from 'framer-motion';
import { HiArrowRight, HiClipboard, HiCheck } from 'react-icons/hi';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useStewBeetVersion } from '../hooks/useStewBeetVersion';
import { useTranslation } from '../i18n/useTranslation';
import { useShiki } from '../hooks/useShiki';
import { FileTree, type FileNode } from './FileTree';
import { ACCENT_BORDER_HOVER, BRAND_DOT, BRAND_PILL, BTN_PRIMARY, GRADIENT_TEXT_BRIGHT, ICON_ACCENT, TERMINAL_GLOW, TEXT_ACCENT_HOVER } from '../theme';

/**
 * Adapted from the life_crystal_block of Stardust Fragment, src/definitions/additions/equipments.py:
 * the EQUIPMENT constant is inlined, the long override_model is dropped, and a components block in
 * the shape that project uses on dragon_pearl is added. The file tree beside it is that block's real
 * build output — components change what those files contain, not how many there are.
 */
const HERO_CODE = `Block(
    id="life_crystal_block",
    vanilla_block=VanillaBlock(id="minecraft:glass", visual_facing="player"),
    manual_category="equipment",

    components={
        "item_name": {"text": "Life Crystal Block", "italic": False, "color": "light_purple"},
        "lore": [{"text": "Break it to get the crystal back", "italic": False, "color": "gray"}],
    },

    # Broken without Silk Touch, it hands the crystal back
    no_silk_touch_drop=NoSilkTouchDrop(id="life_crystal", count=1),

    recipes=[
        CraftingShapelessRecipe(
            category="equipment", result_count=1,
            ingredients=8 * [Ingr("minecraft:glass")] + [Ingr("life_crystal")],
        ),
    ],
)`;

/** Every file in the Stardust Fragment build that belongs to life_crystal_block. */
const GENERATED_FILES: FileNode[] = [
    {
        name: 'build/',
        children: [
            {
                name: 'datapack/',
                children: [
                    {
                        name: 'custom_blocks/life_crystal_block/',
                        children: [
                            { name: 'place_main.mcfunction' },
                            { name: 'place_secondary.mcfunction' },
                            { name: 'destroy.mcfunction' },
                            { name: 'replace_item.mcfunction', note: 'silk touch, else the crystal' },
                        ],
                    },
                    { name: 'calls/smithed_crafter/shapeless_recipes.mcfunction', note: 'the recipe, NBT-aware' },
                    { name: 'calls/smart_ore_generation/veins/life_crystal_block.mcfunction', note: 'world gen' },
                    { name: 'calls/smart_ore_generation/veins/retry/life_crystal_block.mcfunction' },
                    { name: 'tags/block/smart_ore_generation/life_crystal_block_provider.json' },
                    { name: 'loot_table/i/life_crystal_block.json' },
                ],
            },
            {
                name: 'resource_pack/',
                children: [
                    { name: 'items/life_crystal_block.json' },
                    { name: 'models/item/life_crystal_block.json' },
                    { name: 'textures/item/life_crystal_block.png' },
                    { name: 'textures/item/life_crystal_block.png.mcmeta' },
                    { name: 'textures/item/dialog_sprite/life_crystal_block.png' },
                    { name: 'textures/font/high_res/life_crystal_block.png' },
                    { name: 'textures/font/wiki_icons/life_crystal_block_crafting_shapeless.png', note: 'recipe drawn for the manual' },
                ],
            },
        ],
    },
];

const CopyInstall = () => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText('pip install stewbeet');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <button
            onClick={handleCopy}
            className={`group flex items-center gap-3 px-4 py-2.5 bg-slate-900/60 border border-slate-800 ${ACCENT_BORDER_HOVER} rounded-lg transition-colors duration-200`}
        >
            <span className="font-mono text-sm text-slate-300">
                <span className={ICON_ACCENT}>$</span> pip install stewbeet
            </span>
            {copied ? (
                <HiCheck className="text-green-400" />
            ) : (
                <HiClipboard className="text-slate-500 group-hover:text-slate-300 transition-colors" />
            )}
        </button>
    );
};

const Panel = ({ caption, accessory, children }: { caption: string; accessory?: React.ReactNode; children: React.ReactNode }) => (
    <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden">
        <div className="bg-[#2d2d2d] px-4 py-2.5 flex items-center justify-between gap-2 border-b border-white/5">
            <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                <span className="ml-2 text-xs text-slate-400 font-mono">{caption}</span>
            </div>
            {accessory}
        </div>
        {children}
    </div>
);

const CodePanel = ({ caption }: { caption: string }) => {
    const highlighted = useShiki(HERO_CODE, 'python', 'dark-plus');

    return (
        <Panel caption={caption}>
            <div className="p-4 overflow-x-auto custom-scrollbar">
                {highlighted ? (
                    <div
                        dangerouslySetInnerHTML={{ __html: highlighted }}
                        style={{ fontSize: '0.8125rem', lineHeight: '1.65' }}
                        className="[&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-0"
                    />
                ) : (
                    <pre className="m-0 text-[0.8125rem] leading-[1.65] text-slate-300 font-mono">
                        <code>{HERO_CODE}</code>
                    </pre>
                )}
            </div>
        </Panel>
    );
};

export const Hero: React.FC = () => {
    const { version } = useStewBeetVersion();
    const { t, language } = useTranslation();
    const gettingStarted = `/markdown?src=${encodeURIComponent(language === 'fr' ? '0_getting_started/fr.md' : '0_getting_started/en.md')}`;

    return (
        <section id="hero" className="relative min-h-screen flex items-center overflow-hidden pt-24 pb-16 bg-gradient-to-b from-[#0a0a0a] via-[#0a0a0a] to-slate-950">
            {/* Technical Grid Background */}
            <div className="absolute inset-0 z-0 opacity-20">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
                <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-indigo-500 opacity-20 blur-[100px]" />
            </div>

            <div className="relative z-10 w-full max-w-7xl mx-auto px-4 grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-12 items-center">
                {/* Left: the pitch and the definition that backs it */}
                <div>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${BRAND_PILL} text-xs font-mono mb-5`}>
                            <span className={`w-2 h-2 rounded-full ${BRAND_DOT} animate-pulse`} />
                            v{version} {t('hero.versionStable')}
                        </div>

                        <h1 className="text-4xl md:text-5xl xl:text-6xl font-bold text-white mb-4 tracking-tight leading-[1.1]">
                            {t('hero.titleLine1')} <br />
                            <span className={GRADIENT_TEXT_BRIGHT}>{t('hero.titleLine2')}</span>
                        </h1>

                        <p className="text-base xl:text-lg text-slate-400 mb-7 leading-relaxed">
                            {t('hero.description')}{' '}
                            <a href="https://github.com/mcbeet/beet" target="_blank" rel="noopener noreferrer" className={TEXT_ACCENT_HOVER}>
                                {t('hero.beet')}
                            </a>{' '}
                            {t('hero.descriptionContinued')}
                        </p>

                        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-8">
                            <Link
                                to={gettingStarted}
                                className={`flex items-center gap-2 px-6 py-3 ${BTN_PRIMARY} rounded-lg text-white font-semibold transition-all duration-200`}
                            >
                                {t('hero.getStarted')}
                                <HiArrowRight />
                            </Link>
                            <CopyInstall />
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.15 }}
                    >
                        <CodePanel caption={t('hero.codeCaption')} />
                    </motion.div>
                </div>

                {/* Right: what that definition compiled into */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6, delay: 0.25 }}
                    className="relative"
                >
                    <div className={`absolute -inset-3 ${TERMINAL_GLOW} rounded-2xl blur-[48px] opacity-10 pointer-events-none`} />
                    <div className="relative">
                        <Panel
                            caption={t('hero.outputCaption')}
                            accessory={<span className="text-xs font-mono text-green-400">{t('hero.outputSummary')}</span>}
                        >
                            <div className="p-4">
                                <FileTree nodes={GENERATED_FILES} />
                                <p className="mt-4 pt-3 border-t border-white/5 text-xs text-slate-500 leading-relaxed">
                                    {t('hero.outputNote')}
                                </p>
                            </div>
                        </Panel>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
