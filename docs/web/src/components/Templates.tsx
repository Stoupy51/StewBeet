import { motion } from 'framer-motion';
import { HiStar, HiSparkles, HiLightningBolt, HiDownload, HiClipboard, HiCheck } from 'react-icons/hi';
import { useState } from 'react';
import { useTranslation } from '../i18n/useTranslation';
import { ACCENT_BORDER_HOVER, CARD_HIGHLIGHT, GLOW_PRIMARY, GLOW_SECONDARY, GRADIENT_TEXT, PANEL_ACCENT, TEXT_ACCENT, TEXT_ACCENT_SOFT } from '../theme';

export const Templates: React.FC = () => {
    const [copiedTemplate, setCopiedTemplate] = useState<string | null>(null);
    const { t } = useTranslation();

    const handleCopy = (command: string, templateName: string) => {
        navigator.clipboard.writeText(command);
        setCopiedTemplate(templateName);
        setTimeout(() => setCopiedTemplate(null), 2000);
    };

    const templates = [
        {
            icon: HiLightningBolt,
            name: 'minimal',
            displayName: t('templates.minimal'),
            emoji: '🔹',
            recommended: false,
            description: t('templates.minimalDesc'),
            bestFor: t('templates.minimalBestFor'),
            downloadUrl: 'https://github.com/Stoupy51/StewBeet/raw/main/templates/minimal_template.zip'
        },
        {
            icon: HiStar,
            name: 'basic',
            displayName: t('templates.basic'),
            emoji: '⭐',
            recommended: true,
            description: t('templates.basicDesc'),
            bestFor: t('templates.basicBestFor'),
            downloadUrl: 'https://github.com/Stoupy51/StewBeet/raw/main/templates/basic_template.zip'
        },
        {
            icon: HiSparkles,
            name: 'extensive',
            displayName: t('templates.extensive'),
            emoji: '🌟',
            recommended: false,
            description: t('templates.extensiveDesc'),
            bestFor: t('templates.extensiveBestFor'),
            downloadUrl: 'https://github.com/Stoupy51/StewBeet/raw/main/templates/extensive_template.zip'
        }
    ];

    return (
        <section id="templates" className="py-12 px-4 bg-slate-950/50 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden">
                <div className={`absolute -top-40 right-1/4 w-80 h-80 ${GLOW_SECONDARY} rounded-full blur-[100px]`} />
                <div className={`absolute -bottom-40 left-1/4 w-80 h-80 ${GLOW_PRIMARY} rounded-full blur-[100px]`} />
            </div>

            <div className="max-w-7xl mx-auto relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-8"
                >
                    <h2 className={`text-4xl md:text-5xl font-bold mb-4 ${GRADIENT_TEXT}`}>
                        {t('templates.title')}
                    </h2>
                    <p className="text-slate-400 text-lg max-w-3xl mx-auto">
                        {t('templates.subtitle')} <span className={`${TEXT_ACCENT_SOFT} font-semibold`}>{t('templates.subtitleHighlight')}</span> {t('templates.subtitleEnd')}
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {templates.map((template, index) => {
                        const Icon = template.icon;
                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.4, delay: index * 0.1 }}
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
                                                <div className={`w-10 h-10 rounded bg-slate-800 flex items-center justify-center text-2xl`}>
                                                    {template.emoji}
                                                </div>
                                                <div>
                                                    <h3 className="text-lg font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                                                        {template.displayName}
                                                    </h3>
                                                    {template.recommended && (
                                                        <span className={`text-xs ${TEXT_ACCENT} font-medium`}>
                                                            {t('templates.recommended')}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                            <Icon className="text-slate-500 text-xl" />
                                        </div>

                                        <p className="text-sm text-slate-400 mb-6 flex-grow leading-relaxed">
                                            {template.description}
                                        </p>
                                    </a>

                                    <div className="space-y-3">
                                        <div className="text-xs text-slate-500 font-mono bg-slate-950/50 p-2 rounded border border-white/5">
                                            {template.bestFor}
                                        </div>

                                        {/* Command to copy */}
                                        <div className="relative">
                                            <div className="flex items-center gap-2 bg-slate-950/70 rounded border border-white/10 p-3 font-mono text-xs">
                                                <span className="text-green-400">$</span>
                                                <span className="text-slate-400 flex-grow">stewbeet init {template.name}</span>
                                                <button
                                                    onClick={() => handleCopy(`stewbeet init ${template.name}`, template.name)}
                                                    className="text-slate-400 hover:text-indigo-300 transition-colors"
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

                {/* Info Box */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className={`mt-12 backdrop-blur-sm rounded-2xl p-6 ${PANEL_ACCENT}`}
                >
                    <div className="flex items-start gap-4">
                        <div className="w-10 h-10 bg-indigo-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
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
            </div>
        </section>
    );
};
