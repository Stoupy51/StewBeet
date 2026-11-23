import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { API_REFERENCE, DOC_PAGES, PLUGIN_GROUPS, PLUGIN_INDEX, SECTIONS, docHref, type DocPage, type PluginGroup, type Section } from '../docsPages';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { DependencyMark, PluginsTable } from './PluginsTable';
import { useTranslation } from '../i18n/useTranslation';

/** The translation key of the one-line description of each page that has one. */
const DESCRIPTIONS: Record<string, string> = {
    quickstart: 'documentation.quickstartDesc',
    tutorial: 'documentation.gettingStartedDesc',
    migrate: 'documentation.migrationDesc',
    editor: 'documentation.editorSupportDesc',
    items_and_blocks: 'documentation.itemsAndBlocksDesc',
    writing_files: 'documentation.writingToFilesDesc',
    cookbook: 'documentation.cookbookDesc',
    libraries: 'documentation.dependenciesDesc',
    manual: 'documentation.ingameManualDesc',
    publishing: 'documentation.continuousDeliveryDesc',
    performance: 'documentation.performanceDesc',
    testing: 'documentation.testingDesc',
    post_effects: 'documentation.postEffectsDesc',
    'contrib/simplenergy': 'documentation.simplenergyDesc',
    definitions: 'documentation.definitionsSetupDesc',
    'reference/helpers': 'documentation.helperReferenceDesc',
    'reference/beet_yml': 'documentation.beetConfigDesc',
    'reference/equations': 'documentation.equationsDesc',
    how_it_fits: 'documentation.howItFitsDesc',
};

const SectionTitle = ({ section }: { section: Section }) => {
    const { language } = useTranslation();
    return (
        <h2 className={`self-start flex items-center gap-2.5 lg:pt-3 label ${SECTIONS[section].text}`}>
            <span className={`w-2 h-2 ${SECTIONS[section].bg}`} aria-hidden="true" />
            {SECTIONS[section].title[language]}
        </h2>
    );
};

const PageLink = ({ page }: { page: DocPage }) => {
    const { t, language } = useTranslation();
    return (
        <li>
            <Link to={docHref(page, language)} className="group block py-3 border-b border-border">
                <span className="font-semibold group-hover:text-link transition-colors">{page.title[language]}</span>
                {DESCRIPTIONS[page.slug] && <span className="block mt-0.5 text-[0.9375rem] text-text-muted text-pretty">{t(DESCRIPTIONS[page.slug])}</span>}
            </Link>
        </li>
    );
};

/** Every docs page by section, in the order and colours of the page list, then the plugins table. */
export const DocumentationPage = () => {
    const { t, language } = useTranslation();
    const location = useLocation();

    // /#plugins of the home page redirects to the plugins table here
    useEffect(() => {
        if (!location.hash) return;
        const element = document.querySelector(location.hash);
        if (element) setTimeout(() => element.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }, [location]);

    const sections = Object.keys(SECTIONS) as Section[];
    const pagesOf = (section: Section) => DOC_PAGES.filter((page) => page.section === section);

    return (
        <div className="min-h-screen">
            <Navbar />
            <main className="pt-14 lg:pt-16">
                <header className="frame px-4 pt-8 pb-10 lg:px-12 lg:pt-16">
                    <h1 className="text-[2.25rem] lg:text-[3.25rem] leading-[1.12] font-bold">{t('documentation.title')}</h1>
                    <p className="mt-4 max-w-[40rem] text-text-muted text-pretty">{t('documentation.subtitle')}</p>
                </header>

                {sections.map((section) => (
                    <section key={section} className="frame px-4 py-10 lg:px-12 border-t border-border grid gap-4 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-12">
                        <SectionTitle section={section} />
                        {section === 'plugins' ? (
                            <div className="grid gap-x-10 gap-y-6 sm:grid-cols-2">
                                <p className="sm:col-span-2 text-[0.9375rem] text-text-muted">
                                    {t('showcase.subtitle')}{' '}
                                    <Link to={docHref(PLUGIN_INDEX, language)} className="text-link underline underline-offset-2">{t('documentation.allPlugins')}</Link>
                                </p>
                                {(Object.keys(PLUGIN_GROUPS) as PluginGroup[]).map((group) => (
                                    <div key={group}>
                                        <h3 className="font-semibold">{PLUGIN_GROUPS[group][language]}</h3>
                                        <ul className="mt-1.5">
                                            {pagesOf('plugins').filter((page) => page.group === group).map((page) => (
                                                <li key={page.slug}>
                                                    <Link to={docHref(page, language)} className="inline-flex items-center min-h-8 text-[0.9375rem] text-text-muted hover:text-link transition-colors">{page.title[language]}</Link>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <ul className="grid gap-x-10 sm:grid-cols-2 border-t border-border sm:border-t-0">
                                {pagesOf(section).map((page) => <PageLink key={page.slug} page={page} />)}
                                {section === 'reference' && (
                                    <li>
                                        <a href={API_REFERENCE.href} target="_blank" rel="noopener noreferrer" className="group block py-3 border-b border-border">
                                            <span className="font-semibold group-hover:text-link transition-colors">{API_REFERENCE.title[language]}</span>
                                            <span className="block mt-0.5 text-[0.9375rem] text-text-muted">{t('documentation.apiDesc')}</span>
                                        </a>
                                    </li>
                                )}
                            </ul>
                        )}
                    </section>
                ))}

                <section id="plugins" className="frame px-4 py-12 lg:px-12 lg:py-16 border-t border-border scroll-mt-14">
                    <h2 className="text-[1.75rem] lg:text-[2.25rem] leading-tight font-bold">{t('documentation.plugins')}</h2>
                    <p className="mt-4 flex flex-wrap gap-x-5 gap-y-1 text-sm text-text-muted">
                        <span>{t('showcase.legend')}</span>
                        <DependencyMark level="full" />
                        <DependencyMark level="partial" />
                        <DependencyMark level="none" />
                    </p>
                    <div className="mt-8"><PluginsTable /></div>
                </section>
            </main>
            <Footer />
        </div>
    );
};
