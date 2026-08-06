import { motion } from 'framer-motion';
import { HiOutlineExclamationCircle } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { ALERT_ACCENT, HEADING, PIXEL_RULE } from '../theme';

/**
 * The page explained what the framework does and showed the output, but never what was
 * wrong with the alternative. So a visitor who has not personally suffered hand-written
 * mcfunction had no reason to care. This section is the only place on the site written in
 * the maintainer's voice, and it carries the honest limitations, which is the part readers
 * quote to other people.
 */

/** The files a datapacker touches by hand for one custom block, in the order they hit them. */
const BY_HAND: { path: string; role: string }[] = [
    { path: 'data/<ns>/function/place.mcfunction',      role: 'placement' },
    { path: 'data/<ns>/function/destroy.mcfunction',    role: 'destruction' },
    { path: 'data/<ns>/loot_table/block.json',          role: 'drops' },
    { path: 'data/<ns>/recipe/block.json',              role: 'vanilla recipe' },
    { path: 'data/<ns>/function/calls/crafter.mcfunction', role: 'NBT recipe' },
    { path: 'assets/<ns>/items/block.json',             role: 'item definition' },
    { path: 'assets/<ns>/models/item/block.json',       role: 'model' },
    { path: 'assets/minecraft/lang/en_us.json',         role: 'translation key' },
];

export const WhyStewBeet: React.FC = () => {
    const { t } = useTranslation();
    const motionSafe = useMotionSafe();

    const painPoints = [t('why.pain1'), t('why.pain2'), t('why.pain3')];

    return (
        <section id="why" className="py-20 px-4 relative bg-slate-950">
            <div className={`${PIXEL_RULE} absolute top-0 left-0`} />

            <div className="max-w-6xl mx-auto relative z-10">
                <motion.div
                    {...motionSafe({
                        initial: { y: 24 },
                        animate: { y: 0 },
                        viewport: { once: true },
                        transition: { duration: 0.5 },
                    })}
                    className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_auto] gap-x-12 gap-y-10 items-start"
                >
                    <div className="max-w-2xl">
                        <h2 className={`text-3xl md:text-4xl font-bold mb-6 ${HEADING}`}>{t('why.title')}</h2>

                        <p className="text-lg text-slate-300 leading-relaxed mb-6">{t('why.intro')}</p>

                        <ul className="space-y-3 mb-6">
                            {painPoints.map((point) => (
                                <li key={point} className="flex gap-3 text-slate-300 leading-relaxed">
                                    <span className="text-mc-copper font-mono flex-shrink-0" aria-hidden="true">-</span>
                                    <span>{point}</span>
                                </li>
                            ))}
                        </ul>

                        <p className="text-lg text-slate-300 leading-relaxed mb-4">{t('why.resolution')}</p>
                        <p className="text-slate-300 leading-relaxed">{t('why.noPython')}</p>
                    </div>

                    {/* The list the prose is describing, so the claim is visible rather than asserted. */}
                    <div className="lg:w-[24rem] rounded-panel border border-white/10 bg-slate-900/60 overflow-hidden">
                        <div className="px-4 py-2.5 border-b border-white/10 bg-slate-900">
                            <p className="text-xs font-mono uppercase tracking-wider text-mc-copper">{t('why.byHandTitle')}</p>
                        </div>
                        <ul className="p-4 space-y-2 font-mono text-[0.6875rem] leading-relaxed">
                            {BY_HAND.map(({ path, role }) => (
                                <li key={path} className="flex flex-col">
                                    <span className="text-slate-300 break-all">{path}</span>
                                    <span className="text-slate-400">{role}</span>
                                </li>
                            ))}
                        </ul>
                        <p className="px-4 pb-4 text-xs text-slate-400 leading-relaxed">{t('why.byHandNote')}</p>
                    </div>

                    <div className={`rounded-panel p-6 ${ALERT_ACCENT} lg:col-span-2 max-w-3xl`}>
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
