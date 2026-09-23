import { HiArrowRight } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { CopyCommand } from './CopyCommand';
import { BTN_PRIMARY, PAGE } from '../theme';

/** The safety net for a visitor who read the whole page: one line, one action, the install command. */
export const FinalCTA: React.FC = () => {
    const { t, language } = useTranslation();
    const gettingStarted = `/markdown?src=${encodeURIComponent(language === 'fr' ? '0_getting_started/fr.md' : '0_getting_started/en.md')}`;

    return (
        <section className="border-t border-ink-800 bg-ink-900">
            <div data-rise className={`${PAGE} py-20 md:py-24 grid grid-cols-1 md:grid-cols-[auto_minmax(0,1fr)] gap-10 md:gap-14 items-center`}>
                {/* 256px source, 32 art pixels: 128px is an exact 4x, so nearest-neighbour stays crisp. */}
                <img src="/stewbeet-logo.png" alt="" width={128} height={128} className="pixelated w-24 h-24 md:w-32 md:h-32" />

                <div>
                    <h2 className="text-[1.75rem] md:text-[2.25rem] leading-tight font-semibold tracking-tight text-ink-50 text-balance">
                        {t('finalCta.title')}
                    </h2>
                    <p className="mt-3 max-w-xl text-ink-300 leading-relaxed">{t('finalCta.subtitle')}</p>
                    <div className="mt-8 flex flex-col sm:flex-row sm:items-center gap-3">
                        <Link to={gettingStarted} className={`${BTN_PRIMARY} h-11 px-5`}>
                            {t('finalCta.action')}
                            <HiArrowRight aria-hidden="true" />
                        </Link>
                        <CopyCommand command="pip install stewbeet" />
                    </div>
                    <p className="mt-4 font-mono text-xs text-ink-400">{t('finalCta.microcopy')}</p>
                </div>
            </div>
        </section>
    );
};
