import { Link } from 'react-router-dom';
import { HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { useTranslation } from '../i18n/useTranslation';
import { BTN_PRIMARY } from '../theme';

export const NotFoundPage: React.FC = () => {
    const { t } = useTranslation();

    return (
        <div className="min-h-screen flex flex-col">
            <Navbar />

            <main className="frame flex-1 px-4 pt-[5.5rem] pb-16 lg:px-12 lg:pt-32">
                <p className="font-pixel text-[0.8125rem] text-generated">404</p>
                <h1 className="mt-3 text-[2.25rem] lg:text-[3.25rem] leading-[1.12] font-bold text-balance">{t('notFound.title')}</h1>
                <p className="mt-4 max-w-[40rem] text-text-muted text-pretty">{t('notFound.description')}</p>

                <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-3">
                    <Link to="/" className={`min-h-11 px-5 ${BTN_PRIMARY}`}>{t('notFound.backHome')}</Link>
                    <Link to="/docs" className="group inline-flex items-center gap-2 min-h-11 font-medium hover:text-link transition-colors">
                        {t('notFound.browseDocs')}
                        <HiArrowRight className="group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
                    </Link>
                </div>
            </main>

            <Footer />
        </div>
    );
};
