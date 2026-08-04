import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { BTN_PRIMARY, HEADING, TEXT_ACCENT_HOVER } from '../theme';

export const NotFoundPage: React.FC = () => {
    const { t } = useTranslation();
    const motionSafe = useMotionSafe();

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
            <Navbar />

            <div className="relative z-10 flex-1 flex items-center justify-center px-4 py-32">
                <motion.div
                    {...motionSafe({
                        initial: { y: 20 },
                        animate: { y: 0 },
                    })}
                    className="max-w-2xl text-center"
                >
                    <p className={`text-7xl md:text-8xl font-bold mb-6 ${HEADING}`}>404</p>
                    <h1 className="text-3xl md:text-4xl font-bold mb-4">{t('notFound.title')}</h1>
                    <p className="text-lg text-slate-400 leading-relaxed mb-10">{t('notFound.description')}</p>

                    <div className="flex flex-wrap items-center justify-center gap-4">
                        <Link to="/" className={`px-6 py-3 rounded-xl font-medium transition-all ${BTN_PRIMARY}`}>
                            {t('notFound.backHome')}
                        </Link>
                        <Link to="/documentation" className={`flex items-center gap-2 px-6 py-3 font-medium group ${TEXT_ACCENT_HOVER}`}>
                            {t('notFound.browseDocs')}
                            <HiArrowRight className="group-hover:translate-x-1 transition-transform" />
                        </Link>
                    </div>
                </motion.div>
            </div>

            <Footer />
        </div>
    );
};
