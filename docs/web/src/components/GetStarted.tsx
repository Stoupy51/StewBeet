import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { DOC_PAGES, docHref } from '../docsPages';
import { CopyCommand } from './CopyCommand';

const quickstart = DOC_PAGES.find((page) => page.slug === 'quickstart')!;
const TEMPLATES_URL = 'https://github.com/Stoupy51/StewBeet/tree/main/templates';

const STEPS = [
    { command: 'uvx stewbeet init', textKey: 'start.initText' },
    { command: 'uv run stewbeet build', textKey: 'start.buildText' },
];

/** The quickstart's commands, for a visitor who read the whole page and wants to try it now. */
export const GetStarted = () => {
    const { t, language } = useTranslation();

    return (
        <section id="installation" className="frame px-4 py-12 lg:px-12 lg:py-16 border-t border-border scroll-mt-14 grid gap-8 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] lg:gap-12">
            <div>
                <h2 className="text-[1.75rem] lg:text-[2.25rem] leading-tight font-bold text-balance">{t('start.title')}</h2>
                <p className="mt-4 text-text-muted text-pretty">
                    {t('start.needs')} <a href="https://docs.astral.sh/uv/" target="_blank" rel="noopener noreferrer" className="text-link underline underline-offset-2">uv</a>{t('start.needsEnd')}
                </p>
                <Link to={docHref(quickstart, language)} className="mt-6 flex lg:inline-flex items-center justify-center h-12 lg:px-[22px] bg-primary hover:bg-primary-hover text-on-primary font-semibold transition-colors active:scale-[0.98]">
                    {t('hero.readQuickstart')}
                </Link>
            </div>
            <div>
                <ol className="flex flex-col gap-5">
                    {STEPS.map(({ command, textKey }, index) => (
                        <li key={command} className="grid grid-cols-[30px_minmax(0,1fr)] gap-x-4 gap-y-2 items-center">
                            <span className="flex items-center justify-center w-[1.875rem] h-[1.875rem] border border-border font-mono text-[0.6875rem] font-semibold">{String(index + 1).padStart(2, '0')}</span>
                            <CopyCommand command={command} />
                            <p className="col-start-2 text-[0.9375rem] text-text-muted text-pretty">{t(textKey)}</p>
                        </li>
                    ))}
                </ol>
                <p className="mt-6 pt-5 border-t border-border text-[0.9375rem] text-text-muted text-pretty">
                    {t('start.templates')}{' '}
                    <a href={TEMPLATES_URL} target="_blank" rel="noopener noreferrer" className="text-link underline underline-offset-2">{t('start.templatesLink')}</a>
                </p>
            </div>
        </section>
    );
};
