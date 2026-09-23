import { HiDownload, HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { CopyCommand } from './CopyCommand';
import { CARD, TEXT_ACCENT_HOVER } from '../theme';

interface TemplateCard {
    name: 'minimal' | 'basic' | 'extensive';
    recommended: boolean;
}

const REPO = 'https://github.com/Stoupy51/StewBeet';

/** Basic sits in the middle, larger and lit, so the default choice needs no reading. */
const TEMPLATES: TemplateCard[] = [
    { name: 'minimal', recommended: false },
    { name: 'basic', recommended: true },
    { name: 'extensive', recommended: false },
];

const Card = ({ template }: { template: TemplateCard }) => {
    const { t } = useTranslation();
    const { name, recommended } = template;
    const command = `stewbeet init ${name}`;

    return (
        <article
            className={`relative flex flex-col ${recommended ? 'order-first lg:order-none' : ''} ${recommended
                ? 'rounded-panel border border-beet-500/60 bg-ink-900 p-7 lg:py-10 shadow-[0_24px_64px_-24px_rgba(196,35,64,0.45)] bg-[radial-gradient(120%_60%_at_50%_0%,rgba(226,58,82,0.12),transparent)]'
                : `${CARD} p-6`}`}
        >
            {recommended && (
                <span className="absolute -top-3 left-7 rounded-control bg-beet-600 px-2.5 py-1 font-mono text-[0.6875rem] uppercase tracking-wider text-white">
                    {t('templates.recommended')}
                </span>
            )}

            <div className="flex items-baseline justify-between gap-3">
                <h4 className={`font-semibold tracking-tight text-ink-50 ${recommended ? 'text-2xl' : 'text-lg'}`}>{t(`templates.${name}`)}</h4>
                <a
                    href={`${REPO}/blob/main/templates/${name}/src/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 font-mono text-xs text-ink-400 hover:text-ink-100 transition-colors"
                >
                    {t('templates.source')}
                    <HiExternalLink aria-hidden="true" />
                </a>
            </div>
            <p className={`mt-1 font-mono text-xs ${recommended ? 'text-beet-300' : 'text-ink-400'}`}>{t(`templates.${name}BestFor`)}</p>
            <p className={`mt-4 leading-relaxed flex-grow ${recommended ? 'text-ink-200' : 'text-sm text-ink-400'}`}>{t(`templates.${name}Desc`)}</p>

            <div className="mt-6 flex flex-col gap-3">
                <CopyCommand command={command} variant={recommended ? 'primary' : 'default'} className="w-full justify-between" />
                <a
                    href={`${REPO}/raw/main/templates/${name}_template.zip`}
                    download
                    className={`inline-flex items-center gap-1.5 self-start text-xs ${TEXT_ACCENT_HOVER}`}
                >
                    <HiDownload aria-hidden="true" />
                    {t('templates.downloadZip')}
                </a>
            </div>
        </article>
    );
};

export const Templates: React.FC = () => {
    const { t } = useTranslation();

    return (
        <div id="templates" className="mt-20 scroll-mt-20">
            <div data-rise className="max-w-3xl">
                <h3 className="text-2xl md:text-[1.75rem] leading-tight font-semibold tracking-tight text-ink-50">{t('templates.title')}</h3>
                <p className="mt-3 text-ink-300">{t('templates.subtitle')}</p>
            </div>

            <div data-rise className="mt-10 grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)_minmax(0,1fr)] gap-4 lg:gap-5 items-center">
                {TEMPLATES.map((template) => <Card key={template.name} template={template} />)}
            </div>
        </div>
    );
};
