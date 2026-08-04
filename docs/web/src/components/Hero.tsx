import { motion } from 'framer-motion';
import { HiArrowRight, HiArrowNarrowRight, HiClipboard, HiCheck } from 'react-icons/hi';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { FileTree } from './FileTree';
import { GENERATED_FILES } from './heroCode';
import heroCode from '../generated/heroCode.json';
import stats from '../generated/stats.json';
import {
    ACCENT_BORDER_HOVER,
    BRAND_DOT,
    BRAND_PILL,
    BTN_PRIMARY,
    GRADIENT_TEXT_BRIGHT,
    ICON_ACCENT,
    TEXT_ACCENT_HOVER,
} from '../theme';

const CopyInstall = () => {
    const [copied, setCopied] = useState(false);
    const { t } = useTranslation();

    const handleCopy = () => {
        navigator.clipboard.writeText('pip install stewbeet');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <button
            onClick={handleCopy}
            className={`group flex items-center gap-3 px-4 py-2.5 bg-slate-900/60 border border-slate-800 ${ACCENT_BORDER_HOVER} rounded-panel transition-colors duration-200`}
        >
            <span className="font-mono text-sm text-slate-300">
                <span className={ICON_ACCENT}>$</span> pip install stewbeet
            </span>
            {copied ? (
                <HiCheck className="text-mc-emerald" aria-hidden="true" />
            ) : (
                <HiClipboard className="text-slate-400 group-hover:text-slate-300 transition-colors" aria-hidden="true" />
            )}
            <span className="sr-only">{copied ? t('finalCta.copied') : t('finalCta.copyCommand')}</span>
        </button>
    );
};

/** `h-full` is what lets the two hero panels end at the same line under `items-stretch`. */
const Panel = ({ caption, accessory, children }: { caption: string; accessory?: React.ReactNode; children: React.ReactNode }) => (
    <div className="h-full flex flex-col bg-[#1e1e1e] rounded-panel border border-white/10 shadow-2xl overflow-hidden">
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

/** Markup comes from scripts/prehighlight.ts, so this paints coloured on the first frame. */
const CodePanel = ({ caption }: { caption: string }) => (
    <Panel caption={caption}>
        <div className="flex-1 p-4 overflow-x-auto custom-scrollbar">
            <div
                dangerouslySetInnerHTML={{ __html: heroCode.html }}
                style={{ fontSize: '0.75rem', lineHeight: '1.7' }}
                className="[&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-0"
            />
        </div>
    </Panel>
);

export const Hero: React.FC = () => {
    const { t, language } = useTranslation();
    const motionSafe = useMotionSafe();
    const gettingStarted = `/markdown?src=${encodeURIComponent(language === 'fr' ? '0_getting_started/fr.md' : '0_getting_started/en.md')}`;

    return (
        <section id="hero" className="relative min-h-screen flex items-center overflow-hidden pt-24 pb-16 bg-slate-950">
            {/* The one decorative glow left on the site, behind the technical grid. */}
            <div className="absolute inset-0 z-0 opacity-20">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
                <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-mc-emerald opacity-20 blur-[100px]" />
            </div>

            <div className="relative z-10 w-full max-w-7xl 2xl:max-w-[90rem] mx-auto px-4">
                {/* The pitch spans the section: at half width the headline broke over four lines */}
                <motion.div
                    {...motionSafe({
                        initial: { y: 20 },
                        animate: { y: 0 },
                        transition: { duration: 0.5 },
                    })}
                    className="max-w-3xl"
                >
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${BRAND_PILL} text-xs font-mono mb-5`}>
                        <span className={`w-2 h-2 rounded-full ${BRAND_DOT}`} />
                        v{stats.version} {t('hero.versionStable')}
                    </div>

                    <h1 className="text-4xl md:text-5xl xl:text-6xl font-bold text-white mb-4 tracking-tight leading-[1.1]">
                        {t('hero.titleLine1')} <br />
                        <span className={GRADIENT_TEXT_BRIGHT}>{t('hero.titleLine2')}</span>
                    </h1>

                    <p className="text-base xl:text-lg text-slate-300 mb-7 leading-relaxed">
                        {t('hero.description')}{' '}
                        <a href="https://github.com/mcbeet/beet" target="_blank" rel="noopener noreferrer" className={TEXT_ACCENT_HOVER}>
                            {t('hero.beet')}
                        </a>{' '}
                        {t('hero.descriptionContinued')}
                    </p>

                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                        <Link
                            to={gettingStarted}
                            className={`flex items-center gap-2 px-6 py-3 ${BTN_PRIMARY} rounded-panel font-semibold transition-colors duration-200`}
                        >
                            {t('hero.getStarted')}
                            <HiArrowRight aria-hidden="true" />
                        </Link>
                        <CopyInstall />
                    </div>
                </motion.div>

                {/* The definition and what it compiled into, read as one statement: same top,
                    same bottom, an arrow in between. The pair only goes side by side at xl —
                    below that each column is narrower than the 74-column snippet it has to hold. */}
                <div className="mt-10 grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] gap-5 xl:gap-4 items-stretch">
                    <motion.div
                        {...motionSafe({
                            initial: { y: 20 },
                            animate: { y: 0 },
                            transition: { duration: 0.6, delay: 0.15 },
                        })}
                        className="min-w-0"
                    >
                        <CodePanel caption={t('hero.codeCaption')} />
                    </motion.div>

                    <div className="flex items-center justify-center text-slate-400" aria-hidden="true">
                        <HiArrowNarrowRight className="text-2xl rotate-90 xl:rotate-0" />
                    </div>

                    <motion.div
                        {...motionSafe({
                            initial: { scale: 0.98 },
                            animate: { scale: 1 },
                            transition: { duration: 0.6, delay: 0.25 },
                        })}
                        className="relative min-w-0"
                    >
                        <Panel
                            caption={t('hero.outputCaption')}
                            accessory={<span className="text-xs font-mono text-mc-emerald">{t('hero.outputSummary')}</span>}
                        >
                            <div className="flex-1 flex flex-col p-4 overflow-x-auto custom-scrollbar">
                                <FileTree nodes={GENERATED_FILES} />
                                <p className="mt-4 pt-3 border-t border-white/5 text-xs text-slate-400 leading-relaxed">
                                    {t('hero.outputNote')}
                                </p>
                            </div>
                        </Panel>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};
