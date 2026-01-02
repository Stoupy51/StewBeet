import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { HiDownload, HiTerminal, HiFolder, HiPlay, HiChevronRight } from 'react-icons/hi';
import { useStewBeetVersion } from '../hooks/useStewBeetVersion';

interface Step {
    id: number;
    title: string;
    description: string;
    command: string;
    output: Array<{ text: string; color?: string }>;
    icon: React.ComponentType<{ className?: string }>;
}

export const Installation: React.FC = () => {
    const { version } = useStewBeetVersion();
    
    const steps: Step[] = [
        {
            id: 1,
            title: 'Install Python',
            description: 'Ensure Python 3.14+ is installed',
            command: 'python --version',
            output: [{ text: 'Python 3.14.2' }],
            icon: HiDownload
        },
        {
            id: 2,
            title: 'Install StewBeet',
            description: 'Get the package via pip',
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
            title: 'Initialize Project',
            description: 'Choose a template to start',
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
            title: 'Build',
            description: 'Generate your datapack',
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
    
    const [activeStep, setActiveStep] = useState<Step>(steps[0]);
    const [typedCommand, setTypedCommand] = useState('');
    const [showOutput, setShowOutput] = useState(false);

    useEffect(() => {
        setTypedCommand('');
        setShowOutput(false);

        let charIndex = 0;
        const command = activeStep.command;

        const typeInterval = setInterval(() => {
            if (charIndex <= command.length) {
                setTypedCommand(command.substring(0, charIndex));
                charIndex++;
            } else {
                clearInterval(typeInterval);
                setTimeout(() => setShowOutput(true), 300);
            }
        }, 50);

        return () => clearInterval(typeInterval);
    }, [activeStep]);

    return (
        <section id="installation" className="py-24 px-4 bg-[#0a0a0a] relative overflow-hidden">
            <div className="max-w-5xl mx-auto relative z-10">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">
                        Get Started in <span className="text-indigo-400">Seconds</span>
                    </h2>
                </div>

                <div className="flex flex-col md:flex-row gap-8">
                    {/* Steps Navigation */}
                    <div className="md:w-1/3 space-y-2">
                        {steps.map((step) => {
                            const Icon = step.icon;
                            const isActive = activeStep.id === step.id;
                            return (
                                <button
                                    key={step.id}
                                    onClick={() => setActiveStep(step)}
                                    className={`w-full flex items-center gap-4 p-4 rounded-xl transition-all duration-200 border text-left group ${isActive
                                            ? 'bg-indigo-500/10 border-indigo-500/50 text-white'
                                            : 'bg-transparent border-transparent hover:bg-white/5 text-slate-400 hover:text-slate-200'
                                        }`}
                                >
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${isActive ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-500 group-hover:text-slate-300'}`}>
                                        <Icon />
                                    </div>
                                    <div>
                                        <div className="font-bold text-sm">{step.title}</div>
                                        <div className="text-xs opacity-60">{step.description}</div>
                                    </div>
                                    {isActive && <HiChevronRight className="ml-auto text-indigo-400" />}
                                </button>
                            );
                        })}
                    </div>

                    {/* Terminal Window */}
                    <div className="md:w-2/3">
                        <div className="bg-[#1e1e1e] rounded-xl border border-white/10 shadow-2xl overflow-hidden h-[400px] flex flex-col font-mono text-sm">
                            {/* Terminal Header */}
                            <div className="bg-[#2d2d2d] px-4 py-3 flex items-center gap-2 border-b border-white/5">
                                <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                                <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                                <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                                <div className="ml-2 text-xs text-gray-400">terminal — bash</div>
                            </div>

                            {/* Terminal Content */}
                            <div className="p-6 text-slate-300 flex-1 overflow-auto">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-green-400">user@stewbeet:~$</span>
                                    <span>{typedCommand}</span>
                                    <motion.span
                                        animate={{ opacity: [0, 1, 0] }}
                                        transition={{ duration: 0.8, repeat: Infinity }}
                                        className="w-2 h-4 bg-slate-400 inline-block align-middle"
                                    />
                                </div>

                                <AnimatePresence>
                                    {showOutput && (
                                        <motion.div
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
                                            <div className="mt-4 text-green-400">user@stewbeet:~$</div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
