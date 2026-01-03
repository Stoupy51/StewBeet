import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { PluginsTable } from './PluginsTable';

export const Showcase: React.FC = () => {
    const containerRef = useRef<HTMLDivElement>(null);
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
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/10 rounded-full blur-[100px]" />
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-500/10 rounded-full blur-[100px]" />
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
                    <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-purple-200">
                        StewBeet Individual Plugins
                    </h2>
                    <p className="text-slate-400 text-lg max-w-3xl mx-auto mb-8">
                        Over 20 plugins to automate every aspect of your datapack.<br />
                        <span className="text-sm">Legend: <span className="text-red-400">🔴 Fully dependent</span> <span className="text-yellow-400 ml-2">🟡 Partly dependent</span> <span className="text-green-400 ml-2">🟢 Independent</span></span>
                    </p>
                </motion.div>

                <PluginsTable />
            </motion.div>
        </section>
    );
};
