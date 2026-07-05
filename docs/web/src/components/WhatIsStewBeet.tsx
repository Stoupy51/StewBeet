import { motion } from 'framer-motion';
import { HiCode, HiLightningBolt, HiCube } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { GRADIENT_TEXT, GLOW_PRIMARY, GLOW_SECONDARY } from '../theme';
import { useShiki } from '../hooks/useShiki';

const CODE_EXAMPLE = `# Simply define your items...
Block(
    id="super_stone",
    vanilla_block=VanillaBlock(id="minecraft:cobblestone"),
    recipes=[
        # Examples of crafting recipes (shaped and shapeless), no need to specify result -> will default to the Item id
        CraftingShapedRecipe(category="building", shape=["XXX","XXX","XXX"], ingredients={"X": Ingr("minecraft:stone")}),
        CraftingShapelessRecipe(category="building", ingredients=9*[Ingr("minecraft:deepslate")]),

        # Example of recipe with vanilla result (not custom item)
        SmeltingRecipe(experience=0.1, cookingtime=200, category="building", ingredient=Ingr("super_stone"), result=Ingr("minecraft:diamond")),
        BlastingRecipe(experience=0.1, cookingtime=100, category="building", ingredient=Ingr("super_stone"), result=Ingr("minecraft:diamond")),
    ],
)

# StewBeet automatically generates:
# ✅ Models JSON
# ✅ Textures management
# ✅ Loot tables
# ✅ Custom item data
# ✅ In-game manual entries
# ✅ Lang files
# ...and much more!`;

export const WhatIsStewBeet: React.FC = () => {
    const { t } = useTranslation();
    const highlighted = useShiki(CODE_EXAMPLE, 'python', 'dark-plus');
    
    const features = [
        {
            icon: HiCode,
            title: t('whatIs.problem'),
            description: t('whatIs.problemDesc'),
            color: 'from-red-500 to-orange-500'
        },
        {
            icon: HiLightningBolt,
            title: t('whatIs.solution'),
            description: t('whatIs.solutionDesc'),
            color: 'from-indigo-500 to-purple-500'
        },
        {
            icon: HiCube,
            title: t('whatIs.result'),
            description: t('whatIs.resultDesc'),
            color: 'from-emerald-500 to-teal-500'
        }
    ];

    return (
        <section id="what-is" className="py-12 px-4 bg-slate-900/50 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden">
                <div className={`absolute top-1/2 -left-40 w-80 h-80 ${GLOW_PRIMARY} rounded-full blur-[100px]`} />
                <div className={`absolute top-1/2 -right-40 w-80 h-80 ${GLOW_SECONDARY} rounded-full blur-[100px]`} />
            </div>

            <div className="max-w-6xl mx-auto relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-4"
                >
                    <h2 className={`text-4xl md:text-5xl font-bold mb-4 ${GRADIENT_TEXT}`}>
                        {t('whatIs.title')}
                    </h2>
                    <p className="text-slate-400 text-lg max-w-3xl mx-auto">
                        {t('whatIs.description')}
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {features.map((feature, index) => {
                        const Icon = feature.icon;
                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 50 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="group"
                            >
                                <div className="h-full bg-slate-950/50 backdrop-blur-sm rounded-2xl p-8 border border-white/5 hover:border-white/10 transition-all duration-300">
                                    <motion.div
                                        className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-xl mb-6 flex items-center justify-center shadow-lg`}
                                        whileHover={{ scale: 1.1, rotate: [0, -10, 10, 0] }}
                                        transition={{ duration: 0.5 }}
                                    >
                                        <Icon className="text-3xl text-white" />
                                    </motion.div>

                                    <h3 className="text-2xl font-bold text-slate-100 mb-4">
                                        {feature.title}
                                    </h3>
                                    <p className="text-slate-400 leading-relaxed">
                                        {feature.description}
                                    </p>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Code Example */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="mt-4 bg-slate-950/80 backdrop-blur-sm rounded-2xl p-8 border border-indigo-500/20"
                >
                    <div className="flex items-center gap-2 mb-4">
                        <div className="flex gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500" />
                            <div className="w-3 h-3 rounded-full bg-green-500" />
                        </div>
                        <span className="text-slate-400 text-sm ml-2">setup_definitions.py</span>
                    </div>
                    <div
                        dangerouslySetInnerHTML={{ __html: highlighted }}
                        style={{
                            background: 'transparent',
                            fontSize: '0.875rem'
                        }}
                        className="[&>pre]:!bg-transparent [&>pre]:!p-0 [&>pre]:!m-0"
                    />
                </motion.div>
            </div>
        </section>
    );
};
