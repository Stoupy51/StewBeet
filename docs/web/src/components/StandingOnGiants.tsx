import { Link } from 'react-router-dom';
import { DOC_PAGES, docHref } from '../docsPages';
import { useTranslation } from '../i18n/useTranslation';

const howItFits = DOC_PAGES.find((page) => page.slug === 'how_it_fits')!;

/** What StewBeet runs on, in one line: the explanation lives in the docs and the thanks on /credits. */
export const StandingOnGiants = () => {
    const { t, language } = useTranslation();

    return (
        <section id="standing-on-giants" className="frame px-4 py-8 lg:px-12 border-t border-border scroll-mt-14">
            <p className="text-text-muted text-pretty">{t('giants.line')}</p>
            <p className="mt-2 flex flex-wrap gap-x-6 gap-y-1">
                <Link to={docHref(howItFits, language)} className="inline-flex items-center min-h-6 text-link underline underline-offset-2">{t('giants.howItFits')}</Link>
                <Link to="/credits" className="inline-flex items-center min-h-6 text-link underline underline-offset-2">{t('giants.credits')}</Link>
            </p>
        </section>
    );
};
