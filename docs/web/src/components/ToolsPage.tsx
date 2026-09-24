import { Link } from 'react-router-dom';
import { HiArrowRight } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { PageHeader } from './PageHeader';
import { useTranslation } from '../i18n/useTranslation';
import { CARD, CARD_HOVER_ARROW, CARD_HOVER_TEXT, HOVER_CARD } from '../theme';

interface ToolItem {
    title: string;
    description: string;
    /** Where it runs, shown above the title. */
    where: string;
    /** An internal route, or an absolute URL for a tool that does not live on this site. */
    path: string;
}

/** A card: a route stays on the site, an absolute URL opens in its own tab. */
const ToolLink = ({ path, className, children }: { path: string; className: string; children: React.ReactNode }) => (
    path.startsWith('http')
        ? <a href={path} target="_blank" rel="noopener noreferrer" className={className}>{children}</a>
        : <Link to={path} className={className}>{children}</Link>
);

export const ToolsPage: React.FC = () => {
    const { t } = useTranslation();

    const tools: ToolItem[] = [
        { title: t('tools.playground'), description: t('tools.playgroundDesc'), where: t('tools.whereServer'), path: '/playground' },
        { title: t('tools.autoHeaders'), description: t('tools.autoHeadersDesc'), where: t('tools.whereServer'), path: '/auto_headers' },
        { title: t('tools.markdownToBBCode'), description: t('tools.markdownToBBCodeDesc'), where: t('tools.whereBrowser'), path: '/markdown_to_pmc_bbcode' },
        { title: t('tools.extension'), description: t('tools.extensionDesc'), where: t('tools.whereEditor'), path: 'https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet' },
    ];

    return (
        <div className="min-h-screen bg-ink-950 text-ink-200">
            <Navbar />
            <PageHeader title={t('tools.title')} lead={t('tools.subtitle')} width="max-w-5xl" />

            <div className="max-w-5xl mx-auto px-4 sm:px-6 pb-24 grid grid-cols-1 md:grid-cols-2 gap-4">
                {tools.map((tool, index) => (
                    <ToolLink
                        key={tool.path}
                        path={tool.path}
                        className={`group flex items-start justify-between gap-4 p-6 ${CARD} ${HOVER_CARD} ${index === 0 ? 'md:col-span-2 md:p-8' : ''}`}
                    >
                        <div>
                            <p className="font-mono text-xs uppercase tracking-wider text-ink-500">{tool.where}</p>
                            <h2 className={`mt-2 font-semibold tracking-tight text-ink-50 ${index === 0 ? 'text-2xl' : 'text-lg'} ${CARD_HOVER_TEXT}`}>{tool.title}</h2>
                            <p className="mt-2 text-sm text-ink-400 leading-relaxed max-w-2xl">{tool.description}</p>
                        </div>
                        <HiArrowRight className={CARD_HOVER_ARROW} aria-hidden="true" />
                    </ToolLink>
                ))}
            </div>

            <Footer />
        </div>
    );
};
