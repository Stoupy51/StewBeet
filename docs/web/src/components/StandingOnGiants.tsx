import { Link } from 'react-router-dom';
import { HiArrowRight } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { EYEBROW, PAGE, SECTION_LEAD, TEXT_ACCENT_HOVER } from '../theme';
import { LibraryPills } from './LibraryPills';
import { AUTO_LIBRARIES, DEPENDENCIES_DOC, GIANTS, type Giant } from './giantsData';

/**
 * What the framework runs on: the upstream half of the story the built-with section tells from
 * downstream. One line per project; the paragraphs are on /credits.
 */

const GiantRow = ({ giant }: { giant: Giant }) => {
    const { t } = useTranslation();

    return (
        <a
            href={giant.links[0].url}
            target="_blank"
            rel="noopener noreferrer"
            className="group block py-4 border-t border-ink-800"
        >
            <div className="flex items-baseline gap-2">
                <span className="font-semibold text-ink-50 group-hover:text-beet-300 transition-colors">{giant.name}</span>
                <span className="font-mono text-xs text-ink-500">{giant.owner}</span>
            </div>
            <p className="mt-1 text-sm text-ink-400 leading-snug">{t(giant.roleKey)}</p>
        </a>
    );
};

export const StandingOnGiants: React.FC = () => {
    const { t, language } = useTranslation();

    return (
        <section id="standing-on-giants" className="py-14 md:py-28 border-t border-ink-800">
            <div className={`${PAGE} grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] gap-10 lg:gap-16`}>
                <div data-rise>
                    <p className={EYEBROW}>{t('giants.eyebrow')}</p>
                    <h2 className="mt-4 text-2xl md:text-[1.75rem] leading-tight font-semibold tracking-tight text-ink-50">{t('giants.title')}</h2>
                    <p className={`mt-4 ${SECTION_LEAD} md:text-base`}>{t('giants.subtitle')}</p>
                    <div className="mt-6 flex flex-col gap-2">
                        <Link to="/credits" className={`group inline-flex items-center gap-2 text-sm font-medium ${TEXT_ACCENT_HOVER}`}>
                            {t('giants.readCredits')}
                            <HiArrowRight className="group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
                        </Link>
                        <Link
                            to={`/markdown?src=${encodeURIComponent(DEPENDENCIES_DOC[language])}`}
                            className="text-sm text-ink-400 hover:text-ink-100 transition-colors"
                        >
                            {t('giants.readDocs')}
                        </Link>
                    </div>
                </div>

                <div data-rise>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8">
                        {GIANTS.map((giant) => <GiantRow key={giant.name} giant={giant} />)}
                    </div>
                    <div className="mt-6 pt-6 border-t border-ink-800">
                        <p className="text-sm text-ink-400 mb-4">{t('giants.autoNote')}</p>
                        <LibraryPills entries={AUTO_LIBRARIES} />
                    </div>
                </div>
            </div>
        </section>
    );
};
