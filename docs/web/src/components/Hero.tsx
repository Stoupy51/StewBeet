import { motion } from 'framer-motion';
import { HiArrowRight, HiClipboard, HiCheck, HiArrowSmRight } from 'react-icons/hi';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useStewBeetVersion } from '../hooks/useStewBeetVersion';
import { useTranslation } from '../i18n/useTranslation';
import { useShiki } from '../hooks/useShiki';
import { ACCENT_BORDER_HOVER, BRAND_DOT, BRAND_PILL, BTN_PRIMARY, GRADIENT_TEXT_BRIGHT, ICON_ACCENT, TERMINAL_GLOW, TEXT_ACCENT_HOVER } from '../theme';

/** Three lines from templates/extensive/src/definitions/ores.py, trimmed of its comments. */
const HERO_CODE = `from stewbeet import *

generate_everything_about_these_materials({
    "steel_ingot": EquipmentsConfig(equivalent_to=DefaultOre.IRON),
})`;

interface GeneratedGroup {
    count: string;
    label: string;
    detail: string;
}

/** Counted in templates/extensive/build — every generated file whose name contains "steel". */
const GENERATED_GROUPS: GeneratedGroup[] = [
    { count: '20', label: 'items', detail: 'ingot, nugget, block, raw ore, deepslate ore, 5 tools, 4 armour pieces…' },
    { count: '24', label: 'loot tables', detail: 'data/<ns>/loot_table/i/steel_pickaxe.json …' },
    { count: '18', label: 'item models', detail: 'assets/<ns>/items/ + models/item/' },
    { count: '13', label: 'furnace recipes', detail: 'smelting and blasting, NBT-aware' },
    { count: '19', label: 'recipe renders', detail: 'crafting grids drawn for the manual' },
    { count: '3', label: 'ore veins', detail: 'Smart Ore Generation placement functions' },
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

const CodePanel = ({ caption }: { caption: string }) => {
    const highlighted = useShiki(HERO_CODE, 'python', 'dark-plus');

    return (
        <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden">
            <div className="bg-[#2d2d2d] px-4 py-2.5 flex items-center gap-2 border-b border-white/5">
                <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                <span className="ml-2 text-xs text-slate-400 font-mono">{caption}</span>
            </div>
            <div className="p-4 overflow-x-auto custom-scrollbar">
                {highlighted ? (
                    <div
                        dangerouslySetInnerHTML={{ __html: highlighted }}
                        style={{ fontSize: '0.8125rem', lineHeight: '1.7' }}
                        className="[&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-0"
                    />
                ) : (
                    <pre className="m-0 text-[0.8125rem] leading-[1.7] text-slate-300 font-mono">
                        <code>{HERO_CODE}</code>
                    </pre>
                )}
            </div>
        </div>
    );
};

const OutputPanel = ({ caption, summary, note }: { caption: string; summary: string; note: string }) => (
    <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden">
        <div className="bg-[#2d2d2d] px-4 py-2.5 flex items-center justify-between gap-2 border-b border-white/5">
            <span className="text-xs text-slate-400 font-mono">{caption}</span>
            <span className="text-xs font-mono text-green-400">{summary}</span>
        </div>
        <div className="p-4 space-y-2">
            {GENERATED_GROUPS.map((group) => (
                <div key={group.label} className="flex items-baseline gap-3 font-mono text-[0.8125rem]">
                    <HiCheck className="text-green-400 flex-shrink-0 translate-y-0.5" />
                    <span className="text-white tabular-nums w-6 text-right">{group.count}</span>
                    <span className="text-slate-200 w-32 flex-shrink-0">{group.label}</span>
                    <span className="text-slate-500 truncate hidden xl:block">{group.detail}</span>
                </div>
            ))}
            <p className="pt-2 text-xs text-slate-500 leading-relaxed border-t border-white/5 mt-3">{note}</p>
        </div>
    </div>
);

export const Hero: React.FC = () => {
    const { version } = useStewBeetVersion();
    const { t, language } = useTranslation();
    const gettingStarted = `/markdown?src=${encodeURIComponent(language === 'fr' ? '0_getting_started/fr.md' : '0_getting_started/en.md')}`;

    return (
        <section id="hero" className="relative min-h-screen flex items-center overflow-hidden pt-24 pb-12 bg-[#0a0a0a]">
            {/* Technical Grid Background */}
            <div className="absolute inset-0 z-0 opacity-20">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
                <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-indigo-500 opacity-20 blur-[100px]" />
            </div>

            <div className="relative z-10 w-full max-w-7xl mx-auto px-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="max-w-3xl"
                >
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${BRAND_PILL} text-xs font-mono mb-6`}>
                        <span className={`w-2 h-2 rounded-full ${BRAND_DOT} animate-pulse`} />
                        v{version} {t('hero.versionStable')}
                    </div>

                    <h1 className="text-4xl md:text-6xl font-bold text-white mb-5 tracking-tight leading-[1.1]">
                        {t('hero.titleLine1')} <br />
                        <span className={GRADIENT_TEXT_BRIGHT}>{t('hero.titleLine2')}</span>
                    </h1>

                    <p className="text-lg text-slate-400 mb-8 leading-relaxed">
                        {t('hero.description')}{' '}
                        <a href="https://github.com/mcbeet/beet" target="_blank" rel="noopener noreferrer" className={TEXT_ACCENT_HOVER}>
                            {t('hero.beet')}
                        </a>{' '}
                        {t('hero.descriptionContinued')}
                    </p>

                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-14">
                        <Link
                            to={gettingStarted}
                            className={`flex items-center gap-2 px-6 py-3 ${BTN_PRIMARY} rounded-lg text-white font-semibold transition-all duration-200`}
                        >
                            {t('hero.getStarted')}
                            <HiArrowRight />
                        </Link>
                        <CopyInstall />
                        <a href="/documentation" className={`text-sm text-slate-400 ${TEXT_ACCENT_HOVER} underline-offset-4 hover:underline`}>
                            {t('hero.viewDocs')}
                        </a>
                    </div>
                </motion.div>

                {/* Input -> output, the whole pitch in one look */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="relative grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-10 items-start"
                >
                    <div className={`absolute -inset-2 ${TERMINAL_GLOW} rounded-2xl blur-[40px] opacity-10 pointer-events-none`} />

                    <div className="relative">
                        <CodePanel caption={t('hero.codeCaption')} />
                    </div>

                    <div className="relative">
                        <div className="hidden lg:flex absolute -left-8 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-slate-800 border border-white/10 items-center justify-center">
                            <HiArrowSmRight className={ICON_ACCENT} />
                        </div>
                        <OutputPanel
                            caption={t('hero.outputCaption')}
                            summary={t('hero.outputSummary')}
                            note={t('hero.outputNote')}
                        />
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
