import { motion } from 'framer-motion';
import { HiDownload, HiClipboard, HiCheck } from 'react-icons/hi';
import { GiStoneBlock, GiChest, GiCrystalGrowth } from 'react-icons/gi';
import { useState } from 'react';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { ACCENT_BORDER_HOVER, CARD_HIGHLIGHT, HEADING, PANEL_ACCENT, PIXEL_RULE, TEXT_ACCENT, TEXT_ACCENT_SOFT } from '../theme';

export const Templates: React.FC = () => {
    const [copiedTemplate, setCopiedTemplate] = useState<string | null>(null);
    const { t } = useTranslation();
    const motionSafe = useMotionSafe();

    const handleCopy = (command: string, templateName: string) => {
        navigator.clipboard.writeText(command);
        setCopiedTemplate(templateName);
        setTimeout(() => setCopiedTemplate(null), 2000);
    };

    const templates = [
        {
            icon: GiStoneBlock,
            name: 'minimal',
            displayName: t('templates.minimal'),
            recommended: false,
            description: t('templates.minimalDesc'),
            bestFor: t('templates.minimalBestFor'),
            downloadUrl: 'https://github.com/Stoupy51/StewBeet/raw/main/templates/minimal_template.zip'
        },
        {
            icon: GiChest,
            name: 'basic',
            displayName: t('templates.basic'),
            recommended: true,
            description: t('templates.basicDesc'),
            bestFor: t('templates.basicBestFor'),
            downloadUrl: 'https://github.com/Stoupy51/StewBeet/raw/main/templates/basic_template.zip'
        },
        {
            icon: GiCrystalGrowth,
            name: 'extensive',
            displayName: t('templates.extensive'),
            recommended: false,
            description: t('templates.extensiveDesc'),
            bestFor: t('templates.extensiveBestFor'),
            downloadUrl: 'https://github.com/Stoupy51/StewBeet/raw/main/templates/extensive_template.zip'
        }
    ];

    return (
        <section id="templates" className="py-20 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            <div className="max-w-7xl mx-auto relative z-10">
                <motion.div
                    {...motionSafe({
                        initial: { y: 30 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.6 },
                    })}
                    className="text-center mb-8"
                >
                    <h2 className={`text-4xl md:text-5xl font-bold mb-4 ${HEADING}`}>
                        {t('templates.title')}
                    </h2>
                    <p className="text-slate-400 text-lg max-w-3xl mx-auto">
                        {t('templates.subtitle')} <span className={`${TEXT_ACCENT_SOFT} font-semibold`}>{t('templates.subtitleHighlight')}</span> {t('templates.subtitleEnd')}
                    </p>
                </motion.div>

                {/* Info Box */}
                <motion.div
                    {...motionSafe({
                        initial: { y: 30 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.5 },
                    })}
                    className={`mb-8 backdrop-blur-sm rounded-2xl p-6 ${PANEL_ACCENT}`}
                >
                    <div className="flex items-start gap-4">
                        <div className="w-10 h-10 bg-mc-emerald/20 rounded-lg flex items-center justify-center flex-shrink-0">
                            <span className="text-2xl">💡</span>
                        </div>
                        <div>
                            <h4 className="text-lg font-semibold text-slate-100 mb-2">
                                {t('templates.tipTitle')}
                            </h4>
                            <p className="text-slate-300 leading-relaxed">
                                {t('templates.tipBody')}
                            </p>
                        </div>
                    </div>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {templates.map((template, index) => {
                        const Icon = template.icon;
                        return (
                            <motion.div
                                key={index}
                                {...motionSafe({
                                    initial: { y: 20 },
                                    whileInView: { y: 0 },
                                    viewport: { once: true },
                                    transition: { duration: 0.4, delay: index * 0.1 },
                                })}
                                className="group relative"
                            >
                                <div className={`h-full bg-slate-900/80 backdrop-blur-sm rounded-lg p-6 border ${template.recommended ? CARD_HIGHLIGHT : 'border-white/5'
                                    } ${ACCENT_BORDER_HOVER} transition-all duration-300 flex flex-col`}>

                                    <a
                                        href={`https://github.com/Stoupy51/StewBeet/blob/main/templates/${template.name}/src/`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block"
                                    >
                                        <div className="flex items-start justify-between mb-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-panel bg-slate-800 flex items-center justify-center">
                                                    <Icon className="text-xl text-mc-emerald" aria-hidden="true" />
                                                </div>
                                                <div>
                                                    <h3 className="text-lg font-bold text-slate-100 group-hover:text-mc-diamond transition-colors">
                                                        {template.displayName}
                                                    </h3>
                                                    {template.recommended && (
                                                        <span className={`text-xs ${TEXT_ACCENT} font-medium`}>
                                                            {t('templates.recommended')}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        <p className="text-sm text-slate-400 mb-6 flex-grow leading-relaxed">
                                            {template.description}
                                        </p>
                                    </a>

                                    <div className="space-y-3">
                                        <div className="text-xs text-slate-400 font-mono bg-slate-950/50 p-2 rounded border border-white/5">
                                            {template.bestFor}
                                        </div>

                                        {/* Command to copy */}
                                        <div className="relative">
                                            <div className="flex items-center gap-2 bg-slate-950/70 rounded border border-white/10 p-3 font-mono text-xs">
                                                <span className="text-green-400">$</span>
                                                <span className="text-slate-400 flex-grow">stewbeet init {template.name}</span>
                                                <button
                                                    onClick={() => handleCopy(`stewbeet init ${template.name}`, template.name)}
                                                    className="text-slate-400 hover:text-mc-diamond transition-colors"
                                                    title="Copy command"
                                                >
                                                    {copiedTemplate === template.name ? (
                                                        <HiCheck className="text-green-400" />
                                                    ) : (
                                                        <HiClipboard />
                                                    )}
                                                </button>
                                            </div>
                                        </div>

                                        {/* Optional download */}
                                        <motion.a
                                            href={template.downloadUrl}
                                            download
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                            className="flex items-center justify-center gap-2 w-full py-2 rounded bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-300 border border-white/5 hover:border-white/10 transition-all text-xs"
                                        >
                                            <HiDownload className="text-xs" />
                                            {t('templates.downloadZip')}
                                        </motion.a>
                                    </div>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>

            </div>
        </section>
    );
};
