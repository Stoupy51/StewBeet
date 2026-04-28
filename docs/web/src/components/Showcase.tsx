import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { PluginsTable } from './PluginsTable';
import { useTranslation } from '../i18n/useTranslation';
import { GRADIENT_TEXT, GLOW_PRIMARY, GLOW_SECONDARY } from '../theme';

export const Showcase: React.FC = () => {
    const containerRef = useRef<HTMLDivElement>(null);
    const { t } = useTranslation();
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"]
    });

    const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
    const y = useTransform(scrollYProgress, [0, 0.2], [100, 0]);

    return (
        <section
            id="plugins"
            ref={containerRef}
            className="py-24 px-4 bg-gradient-to-b from-slate-950 to-slate-900 relative overflow-hidden"
        >
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden">
                <div className={`absolute -top-40 -right-40 w-80 h-80 ${GLOW_SECONDARY} rounded-full blur-[100px]`} />
                <div className={`absolute -bottom-40 -left-40 w-80 h-80 ${GLOW_PRIMARY} rounded-full blur-[100px]`} />
            </div>

            <motion.div
                style={{ opacity, y }}
                className="max-w-7xl mx-auto relative z-10"
            >
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className={`text-4xl md:text-5xl font-bold mb-4 ${GRADIENT_TEXT}`}>
                        {t('showcase.title')}
                    </h2>
                    <p className="text-slate-400 text-lg max-w-3xl mx-auto mb-8">
                        {t('showcase.subtitle')}<br />
                        <span className="text-sm">{t('showcase.legend')} <span className="text-red-400">🔴 {t('showcase.fullyDependent')}</span> <span className="text-yellow-400 ml-2">🟡 {t('showcase.partlyDependent')}</span> <span className="text-green-400 ml-2">🟢 {t('showcase.independent')}</span></span>
                    </p>
                </motion.div>

                <PluginsTable />
            </motion.div>
        </section>
    );
};
