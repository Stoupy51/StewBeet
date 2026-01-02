import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiDocumentText, HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';

interface DocItem {
    title: string;
    description: string;
    path: string;
    icon?: string;
}

export const DocumentationPage: React.FC = () => {
    const docs: DocItem[] = [
        {
            title: '🚀 Getting Started',
            description: 'Complete guide for beginners - installation, setup, and creating your first datapack',
            path: '0_getting_started/README.md',
        },
        {
            title: '📚 Definitions Setup',
            description: 'Learn how to define custom items, blocks, and equipment configurations',
            path: '1_definitions_setup/README.md',
        },
        {
            title: '📝 Writing to Files',
            description: 'Master file writing with static loading, native beet API, and StewBeet helper functions',
            path: '2_writing_to_files/README.md',
        },
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100">
            <Navbar />

            {/* Background decoration */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-20 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px]" />
            </div>

            {/* Hero Section */}
            <div className="relative z-10 pt-32 pb-16 px-4">
                <div className="max-w-7xl mx-auto text-center">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-indigo-200 via-purple-200 to-pink-200 bg-clip-text text-transparent"
                    >
                        📖 Documentation
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-slate-300 max-w-3xl mx-auto"
                    >
                        Comprehensive guides and references for StewBeet framework
                    </motion.p>
                </div>
            </div>

            {/* Documentation List */}
            <div className="relative z-10 pb-20 px-4">
                <div className="max-w-4xl mx-auto">
                    <div className="space-y-4">
                        {docs.map((doc, index) => (
                            <motion.div
                                key={doc.path}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 + index * 0.1 }}
                            >
                                <Link
                                    to={`/markdown?src=${encodeURIComponent(doc.path)}`}
                                    className="block group"
                                >
                                    <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-indigo-500/50 transition-all hover:bg-slate-900/50 hover:shadow-lg hover:shadow-indigo-500/10">
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <HiDocumentText className="text-2xl text-indigo-400" />
                                                    <h2 className="text-2xl font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                                                        {doc.title}
                                                    </h2>
                                                </div>
                                                <p className="text-slate-400 leading-relaxed">
                                                    {doc.description}
                                                </p>
                                            </div>
                                            <HiArrowRight className="text-2xl text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
                                        </div>
                                    </div>
                                </Link>
                            </motion.div>
                        ))}
                    </div>

                    {/* Coming Soon Section */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="mt-12 text-center"
                    >
                        <p className="text-slate-500 text-sm">
                            More documentation pages coming soon...
                        </p>
                    </motion.div>
                </div>
            </div>

            <Footer />
        </div>
    );
};
