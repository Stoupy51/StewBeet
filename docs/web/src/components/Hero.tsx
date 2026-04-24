import { motion } from 'framer-motion';
import { HiTerminal, HiDocumentText, HiClipboard, HiCheck } from 'react-icons/hi';
import { useEffect, useState } from 'react';
import { useStewBeetVersion } from '../hooks/useStewBeetVersion';
import { useTranslation } from '../i18n/useTranslation';

const TerminalWindow = () => {
    const { version } = useStewBeetVersion();
    const [lines, setLines] = useState<Array<{ text: string; color?: string }>>([]);

    useEffect(() => {
        const fullLines: Array<{ text: string; color?: string }> = [
            { text: "> pip install stewbeet", color: "text-slate-300" },
            { text: "Installing stewbeet...", color: "text-slate-400" },
            { text: `Successfully installed stewbeet-${version}`, color: "text-green-400" },
            { text: "> stewbeet init basic", color: "text-slate-300" },
            { text: "[INFO] Template initialized successfully!", color: "text-green-400" },
            { text: "> stewbeet", color: "text-slate-300" },
            { text: "Building project...", color: "text-slate-400" },
            { text: "...", color: "text-slate-500" },
            { text: "[DEBUG] Total execution time: 0.79140s", color: "text-blue-400" },
            { text: "Done!", color: "text-green-400" },
        ];

        let currentLine = 0;
        let currentChar = 0;
        let timeout: ReturnType<typeof setTimeout>;

        const typeLine = () => {
            if (currentLine >= fullLines.length) {
                setTimeout(() => {
                    setLines([]);
                    currentLine = 0;
                    currentChar = 0;
                    typeLine();
                }, 3000);
                return;
            }

            const line = fullLines[currentLine];

            if (currentChar <= line.text.length) {
                setLines(prev => {
                    const newLines = [...prev];
                    newLines[currentLine] = {
                        text: line.text.substring(0, currentChar),
                        color: line.color
                    };
                    return newLines;
                });
                currentChar++;
                timeout = setTimeout(typeLine, 30 + Math.random() * 30);
            } else {
                currentLine++;
                currentChar = 0;
                timeout = setTimeout(typeLine, 500);
            }
        };

        typeLine();
        return () => clearTimeout(timeout);
    }, [version]);

    return (
        <div className="w-full max-w-lg mx-auto bg-[#1e1e1e] rounded-lg shadow-2xl overflow-hidden border border-white/10 font-mono text-sm">
            <div className="bg-[#2d2d2d] px-4 py-2 flex items-center gap-2 border-b border-white/5">
                <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                <div className="ml-2 text-xs text-gray-400">terminal — stewbeet</div>
            </div>
            <div className="p-4 h-[20rem] overflow-hidden text-gray-300">
                {lines.map((line, i) => (
                    <div key={i} className="mb-1">
                        <span className="text-green-400 mr-2">$</span>
                        <span className={line.color || 'text-gray-300'}>{line.text}</span>
                    </div>
                ))}
                <motion.span
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="inline-block w-2 h-4 bg-gray-400 align-middle ml-1"
                />
            </div>
        </div>
    );
};

const CopyButton = ({ text }: { text: string }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <button
            onClick={handleCopy}
            className="group relative flex items-center gap-3 px-6 py-3 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 hover:border-indigo-500/50 rounded-lg transition-all duration-200"
        >
            <div className="font-mono text-slate-300">
                <span className="text-indigo-400">$</span> pip install stewbeet
            </div>
            <div className="w-px h-4 bg-slate-700" />
            {copied ? (
                <HiCheck className="text-green-400 text-lg" />
            ) : (
                <HiClipboard className="text-slate-400 group-hover:text-white transition-colors text-lg" />
            )}
        </button>
    );
};

export const Hero: React.FC = () => {
    const { version } = useStewBeetVersion();
    const { t } = useTranslation();

    return (
        <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20 bg-[#0a0a0a]">
            {/* Technical Grid Background */}
            <div className="absolute inset-0 z-0 opacity-20">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
                <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-indigo-500 opacity-20 blur-[100px]" />
            </div>

            <div className="relative z-10 w-full max-w-7xl mx-auto px-4 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                {/* Left Column: Content */}
                <motion.div
                    className="text-left"
                >
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-mono mb-6"
                    >
                        <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                        v{version} {t('hero.versionStable')}
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight"
                    >
                        {t('hero.automateTitle')} <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                            {t('hero.minecraftDatapacks')}
                        </span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="text-lg text-slate-400 mb-8 max-w-xl leading-relaxed"
                    >
                        {t('hero.description')} <a href="https://github.com/mcbeet/beet" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 transition-colors">{t('hero.beet')}</a> {t('hero.descriptionContinued')}
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                        className="flex flex-col sm:flex-row gap-4"
                    >
                        <CopyButton text="pip install stewbeet" />

                        <a
                            href="/documentation"
                            className="flex items-center justify-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-lg text-slate-300 transition-all duration-200 font-medium"
                        >
                            <HiDocumentText className="text-lg" />
                            {t('hero.viewDocs')}
                        </a>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.8 }}
                        className="mt-12 flex items-center gap-6 text-sm text-slate-500 font-mono"
                    >
                        <div className="flex items-center gap-2">
                            <HiCheck className="text-indigo-400" />
                            <span>{t('hero.typeSafe')}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <HiCheck className="text-indigo-400" />
                            <span>{t('hero.autoGenerated')}</span>
                        </div>
                    </motion.div>
                </motion.div>

                {/* Right Column: Terminal */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="relative hidden lg:block"
                >
                    <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl blur opacity-20" />
                    <TerminalWindow />

                    {/* Floating Elements around terminal */}
                    <div className="animate-float-up absolute -top-8 -right-8 bg-[#1e1e1e] p-4 rounded-lg border border-white/10 shadow-xl">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-8 h-8 rounded bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                                <HiTerminal />
                            </div>
                            <div>
                                <div className="text-xs text-slate-400">{t('hero.buildTime')}</div>
                                <div className="text-sm font-bold text-white">{t('hero.fast')}</div>
                            </div>
                        </div>
                    </div>

                    <div className="animate-float-down absolute -bottom-8 -left-8 bg-[#1e1e1e] p-4 rounded-lg border border-white/10 shadow-xl">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded bg-green-500/20 flex items-center justify-center text-green-400">
                                <HiCheck />
                            </div>
                            <div>
                                <div className="text-xs text-slate-400">{t('hero.filesGenerated')}</div>
                                <div className="text-sm font-bold text-white">2,026+</div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
