import { motion } from 'framer-motion';
import { HiOutlineExclamationCircle } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { ALERT_ACCENT, HEADING, PIXEL_RULE } from '../theme';

/**
 * The page explained what the framework does and showed the output, but never what was
 * wrong with the alternative, so a visitor who has not personally suffered hand-written
 * mcfunction had no reason to care.
 *
 * The cost used to be three paragraphs of prose. A reader who is deciding in seconds does
 * not read three paragraphs, so it is now two stacks of files side by side: eight against
 * one. This section still carries the honest limitations, which is the part readers quote.
 */

interface HandFile {
    path: string;
    role: string;
    /** Which pack the file lands in, which is what makes the count feel like work. */
    pack: 'data' | 'assets';
}

/** The files a datapacker touches by hand for one custom block, in the order they hit them. */
const BY_HAND: HandFile[] = [
    { path: 'function/place.mcfunction',           role: 'placement',       pack: 'data' },
    { path: 'function/destroy.mcfunction',         role: 'destruction',     pack: 'data' },
    { path: 'loot_table/block.json',               role: 'drops',           pack: 'data' },
    { path: 'recipe/block.json',                   role: 'vanilla recipe',  pack: 'data' },
    { path: 'function/calls/crafter.mcfunction',   role: 'NBT recipe',      pack: 'data' },
    { path: 'items/block.json',                    role: 'item definition', pack: 'assets' },
    { path: 'models/item/block.json',              role: 'model',           pack: 'assets' },
    { path: 'lang/en_us.json',                     role: 'translation key', pack: 'assets' },
];

const PACK_COLOR: Record<HandFile['pack'], string> = {
    data: 'text-mc-copper/70',
    assets: 'text-mc-copper/40',
};

const Tally = ({ count, unit, tone }: { count: string; unit: string; tone: string }) => (
    <div className="flex items-baseline gap-3">
        <span className={`font-mono text-5xl leading-none ${tone}`}>{count}</span>
        <span className="text-sm text-slate-400 leading-tight">{unit}</span>
    </div>
);

export const WhyStewBeet: React.FC = () => {
    const { t } = useTranslation();
    const motionSafe = useMotionSafe();

    return (
        <section id="why" className="py-20 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            <div className="max-w-6xl mx-auto relative z-10">
                <motion.div
                    {...motionSafe({
                        initial: { y: 24 },
                        whileInView: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.5 },
                    })}
                >
                    <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${HEADING}`}>{t('why.title')}</h2>
                    <p className="text-lg text-slate-300 leading-relaxed max-w-2xl mb-10">{t('why.intro')}</p>

                    {/* The count is the argument, so it is shown rather than described */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch mb-8">
                        <div className="rounded-panel border border-mc-copper/25 bg-slate-900/60 p-6">
                            <p className="text-xs font-mono uppercase tracking-wider text-mc-copper mb-4">{t('why.byHandTitle')}</p>
                            <Tally count="8" unit={t('why.byHandUnit')} tone="text-mc-copper" />
                            <ul className="mt-6 space-y-1.5 font-mono text-xs">
                                {BY_HAND.map(({ path, role, pack }) => (
                                    <li key={path} className="flex items-baseline justify-between gap-4">
                                        <span className={`${PACK_COLOR[pack]} truncate`}>{path}</span>
                                        <span className="text-slate-500 flex-shrink-0">{role}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="rounded-panel border border-mc-emerald/30 bg-slate-900/60 p-6 flex flex-col">
                            <p className="text-xs font-mono uppercase tracking-wider text-mc-emerald mb-4">{t('why.withTitle')}</p>
                            <Tally count="1" unit={t('why.withUnit')} tone="text-mc-emerald" />
                            <ul className="mt-6 font-mono text-xs">
                                <li className="text-mc-emerald/80">{t('why.withFile')}</li>
                            </ul>
                            <p className="mt-auto pt-6 text-sm text-slate-300 leading-relaxed">{t('why.withNote')}</p>
                        </div>
                    </div>

                    <p className="text-slate-300 leading-relaxed max-w-2xl mb-8">{t('why.noPython')}</p>

                    <div className={`rounded-panel p-6 ${ALERT_ACCENT} max-w-3xl`}>
                        <div className="flex items-start gap-3">
                            <HiOutlineExclamationCircle className="text-mc-copper text-xl flex-shrink-0 mt-0.5" aria-hidden="true" />
                            <div>
                                <h3 className="font-semibold text-slate-100 mb-2">{t('why.limitsTitle')}</h3>
                                <p className="text-slate-300 text-sm leading-relaxed">{t('why.limitsBody')}</p>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
