import { motion } from 'framer-motion';
import { useState, useEffect, useRef, useSyncExternalStore } from 'react';
import { HiDownload, HiTerminal, HiFolder, HiPlay } from 'react-icons/hi';
import { useStewBeetVersion } from '../hooks/useStewBeetVersion';
import { useTranslation } from '../i18n/useTranslation';
import { TEXT_ACCENT, STEP_ACTIVE, ICON_ACTIVE } from '../theme';

interface Step {
    id: number;
    title: string;
    description: string;
    command: string;
    output: Array<{ text: string; color?: string }>;
    icon: React.ComponentType<{ className?: string }>;
}

/** Milliseconds per typed character, then the reading time that follows the output. */
const TYPING_SPEED = 45;
const READ_TIME_PER_LINE = 260;
const MIN_READ_TIME = 2600;
const MAX_READ_TIME = 9000;

/** False while server-rendering and on the hydration pass, true once the client owns the DOM. */
const subscribeNever = () => () => {};
const useIsHydrated = () => useSyncExternalStore(subscribeNever, () => true, () => false);

function stepDurations(step: Step): { typing: number; total: number } {
    const typing = step.command.length * TYPING_SPEED;
    const read = Math.min(MAX_READ_TIME, Math.max(MIN_READ_TIME, step.output.length * READ_TIME_PER_LINE));
    return { typing, total: typing + read };
}

export const Installation: React.FC = () => {
    const { version } = useStewBeetVersion();
    const { t } = useTranslation();

    const steps: Step[] = [
        {
            id: 1,
            title: t('installation.step1'),
            description: t('installation.step1Desc'),
            command: 'python --version',
            output: [{ text: 'Python 3.14.3' }],
            icon: HiDownload
        },
        {
            id: 2,
            title: t('installation.step2'),
            description: t('installation.step2Desc'),
            command: 'pip install stewbeet',
            output: [
                { text: 'Collecting stewbeet' },
                { text: `Downloading stewbeet-${version}-py3-none-any.whl (45 kB)` },
                { text: 'Installing collected packages: stewbeet' },
                { text: `Successfully installed stewbeet-${version}`, color: 'text-blue-400' }
            ],
            icon: HiTerminal
        },
        {
            id: 3,
            title: t('installation.step3'),
            description: t('installation.step3Desc'),
            command: 'stewbeet init',
            output: [
                { text: '[INFO] Available templates:', color: 'text-green-400' },
                { text: '  - "minimal":   🔹 A very minimal template using only one `stewbeet` plugin.' },
                { text: '  - "basic":     ⭐ (Recommended) Complete configuration with all plugins but WITHOUT coded examples.' },
                { text: '  - "extensive": 🌟 Complete template with ALL features and coded examples (ruby ore, tools, etc.).' },
                { text: '' },
                { text: 'Please choose a template from the list above: basic', color: 'text-yellow-400' },
                { text: '[INFO] Template initialized successfully!', color: 'text-green-400' }
            ],
            icon: HiFolder
        },
        {
            id: 4,
            title: t('installation.step4'),
            description: t('installation.step4Desc'),
            command: 'stewbeet',
            output: [
                { text: 'Building project...', color: 'text-red-400' },
                { text: '' },
                { text: '[PROGRESS] resource_pack.sounds: 44.76ms', color: 'text-purple-400' },
                { text: '[PROGRESS] resource_pack.item_models: 3.60ms', color: 'text-purple-400' },
                { text: '[PROGRESS] custom_recipes: 6.55ms', color: 'text-purple-400' },
                { text: 'Creating manual pages: 100%|████████████| 28/28 [69.36it/s]', color: 'text-purple-400' },
                { text: '[PROGRESS] ingame_manual: 0.66s', color: 'text-purple-400' },
                { text: '[PROGRESS] datapack.loading: 1.42ms', color: 'text-purple-400' },
                { text: '[PROGRESS] datapack.custom_blocks: 3.10ms', color: 'text-purple-400' },
                { text: '[PROGRESS] datapack.loot_tables: 3.13ms', color: 'text-purple-400' },
                { text: '[INFO] Summary of the official supported libraries used in the datapack: Common Signals, Smithed Custom Block, Smithed Crafter, Furnace NBT Recipes, SmartOreGeneration, Bookshelf Math', color: 'text-green-400' },
                { text: 'Generating lang file: 100%|██████████| 198/198 [4731.85it/s]', color: 'text-blue-400' },
                { text: '[PROGRESS] auto.lang_file: 0.16s', color: 'text-purple-400' },
                { text: '[PROGRESS] merge_smithed_weld: 0.58s', color: 'text-purple-400' },
                { text: '' },
                { text: '[DEBUG] Total execution time: 4.96s', color: 'text-cyan-400' },
                { text: 'Done!', color: 'text-green-400' }
            ],
            icon: HiPlay
        }
    ];

    const [activeIndex, setActiveIndex] = useState(0);
    const [progress, setProgress] = useState(0);
    // Before hydration the whole step is shown at once, so crawlers get the text
    const mounted = useIsHydrated();
    const pausedRef = useRef(false);

    const activeStep = steps[activeIndex];
    const { typing, total } = stepDurations(activeStep);

    useEffect(() => {
        if (!mounted) return;

        let frame = 0;
        let start = performance.now();
        let lastTick = start;

        const tick = (now: number) => {
            // Hovering the terminal freezes the clock rather than resetting it
            if (pausedRef.current) {
                start += now - lastTick;
            }
            lastTick = now;

            const elapsed = now - start;
            if (elapsed >= total) {
                setProgress(0);
                setActiveIndex((index) => (index + 1) % steps.length);
                return;
            }
            setProgress(elapsed / total);
            frame = requestAnimationFrame(tick);
        };

        frame = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(frame);
    }, [activeIndex, mounted, total, steps.length]);

    const typedLength = mounted ? Math.round(Math.min(1, progress / (typing / total)) * activeStep.command.length) : activeStep.command.length;
    const typedCommand = activeStep.command.slice(0, typedLength);
    const showOutput = !mounted || progress >= typing / total;

    return (
        <section id="installation" className="py-20 px-4 relative overflow-hidden bg-gradient-to-b from-slate-900/60 via-[#0a0a0a] to-[#0a0a0a]">
            <div className="max-w-5xl mx-auto relative z-10">
                <div className="text-center mb-10">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">
                        {t('installation.title')} <span className={TEXT_ACCENT}>{t('installation.titleHighlight')}</span>
                    </h2>
                </div>

                <div className="flex flex-col md:flex-row gap-8">
                    {/* Steps Navigation — each one fills as its turn plays */}
                    <div className="md:w-1/3 space-y-2">
                        {steps.map((step, index) => {
                            const Icon = step.icon;
                            const isActive = index === activeIndex;
                            return (
                                <button
                                    key={step.id}
                                    onClick={() => { setActiveIndex(index); setProgress(0); }}
                                    className={`relative w-full flex items-center gap-4 p-4 rounded-xl transition-all duration-200 border text-left group overflow-hidden ${isActive
                                        ? STEP_ACTIVE
                                        : 'bg-transparent border-transparent hover:bg-white/5 text-slate-400 hover:text-slate-200'
                                        }`}
                                >
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors flex-shrink-0 ${isActive ? ICON_ACTIVE : 'bg-slate-800 text-slate-500 group-hover:text-slate-300'}`}>
                                        <Icon />
                                    </div>
                                    <div className="min-w-0">
                                        <div className="font-bold text-sm">{step.title}</div>
                                        <div className="text-xs opacity-60">{step.description}</div>
                                    </div>
                                    {isActive && (
                                        <span
                                            className="absolute bottom-0 left-0 h-0.5 bg-indigo-400"
                                            style={{ width: `${progress * 100}%` }}
                                        />
                                    )}
                                </button>
                            );
                        })}
                    </div>

                    {/* Terminal Window */}
                    <div className="md:w-2/3">
                        <div
                            onMouseEnter={() => { pausedRef.current = true; }}
                            onMouseLeave={() => { pausedRef.current = false; }}
                            className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden h-[26rem] flex flex-col font-mono text-sm"
                        >
                            {/* Terminal Header */}
                            <div className="bg-[#2d2d2d] px-4 py-3 flex items-center gap-2 border-b border-white/5 flex-shrink-0">
                                <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                                <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                                <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                                <div className="ml-2 text-xs text-gray-400">terminal — bash</div>
                                <div className="ml-auto text-[0.6875rem] text-slate-500">{activeIndex + 1} / {steps.length}</div>
                            </div>

                            {/* Progress across the terminal width */}
                            <div className="h-0.5 bg-white/5 flex-shrink-0">
                                <div
                                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                                    style={{ width: `${progress * 100}%` }}
                                />
                            </div>

                            {/* Terminal Content */}
                            <div className="p-6 text-slate-300 flex-1 overflow-auto custom-scrollbar">
                                <div className="flex items-baseline gap-2 mb-2">
                                    <span className="text-green-400 flex-shrink-0">user@stewbeet:~$</span>
                                    <span className="break-all">{typedCommand}</span>
                                    <motion.span
                                        animate={{ opacity: [0, 1, 0] }}
                                        transition={{ duration: 0.8, repeat: Infinity }}
                                        className="w-2 h-4 bg-slate-400 inline-block self-center"
                                    />
                                </div>

                                {showOutput && (
                                    <motion.div
                                        key={activeStep.id}
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="space-y-1 text-slate-400"
                                    >
                                        {activeStep.output.map((line, i) => (
                                            line.text === '' ? (
                                                <div key={i} className="h-4" />
                                            ) : (
                                                <div key={i} className={line.color || ''}>
                                                    {line.text}
                                                </div>
                                            )
                                        ))}
                                        <div className="pt-3 text-green-400">user@stewbeet:~$</div>
                                    </motion.div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
