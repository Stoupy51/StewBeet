import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { ProjectIcon } from './ShowcaseStrip';
import { useTranslation } from '../i18n/useTranslation';
import { SHOWCASE, type ShowcaseProject } from './builtWithData';

const numberFormat = new Intl.NumberFormat('en-US');

const GROUPS: { key: string; projects: ShowcaseProject[] }[] = [
    { key: 'showcase.community', projects: SHOWCASE.filter((project) => project.community) },
    { key: 'showcase.packs', projects: SHOWCASE.filter((project) => !project.community && !project.library) },
    { key: 'showcase.libraries', projects: SHOWCASE.filter((project) => project.library) },
];

const ProjectCard = ({ project }: { project: ShowcaseProject }) => {
    const { t, language } = useTranslation();
    const { stats } = project;

    return (
        <li>
            <a href={project.url} target="_blank" rel="noopener noreferrer" className="group flex gap-4 h-full p-4 border border-border hover:border-ink-600 transition-colors">
                <ProjectIcon project={project} />
                <span className="min-w-0 flex flex-col">
                    <span className="font-bold group-hover:text-link transition-colors">{project.name}</span>
                    <span className="text-sm text-text-muted">{project.owner}</span>
                    {project.summary && <span className="mt-2 text-[0.9375rem] text-pretty">{project.summary[language]}</span>}
                    {stats && (
                        <span className="mt-2 text-[0.8125rem] text-text-muted">
                            {t('builtWith.filesFrom')
                                .replace('{files}', numberFormat.format(stats.functions + stats.jsonFiles + stats.textures))
                                .replace('{lines}', numberFormat.format(stats.sourceLines))}
                        </span>
                    )}
                </span>
            </a>
        </li>
    );
};

/** Every public project built with StewBeet, other people's first, each card opening its source. */
export const ShowcasePage = () => {
    const { t } = useTranslation();

    return (
        <div className="min-h-screen">
            <Navbar />
            <main className="pt-14 lg:pt-16">
                <header className="frame px-4 pt-8 pb-10 lg:px-12 lg:pt-16">
                    <h1 className="text-[2.25rem] lg:text-[3.25rem] leading-[1.12] font-bold text-balance">{t('builtWith.title').replace('{n}', String(SHOWCASE.length))}</h1>
                    <p className="mt-4 max-w-[40rem] text-text-muted text-pretty">{t('showcase.lead')}</p>
                </header>

                {GROUPS.map(({ key, projects }) => (
                    <section key={key} className="frame px-4 py-10 lg:px-12 border-t border-border grid gap-4 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-12">
                        <h2 className="self-start label lg:pt-3">{t(key)}</h2>
                        <ul className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
                            {projects.map((project) => <ProjectCard key={project.url} project={project} />)}
                        </ul>
                    </section>
                ))}

                <section className="frame px-4 py-10 lg:px-12 border-t border-border grid gap-4 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-12">
                    <h2 className="self-start label lg:pt-1">{t('showcase.addTitle')}</h2>
                    <p className="max-w-[40rem] text-pretty">
                        {t('showcase.addText')}{' '}
                        <a href="https://github.com/Stoupy51/StewBeet/issues/new" target="_blank" rel="noopener noreferrer" className="text-link underline underline-offset-2">{t('showcase.addLink')}</a>
                    </p>
                </section>
            </main>
            <Footer />
        </div>
    );
};
