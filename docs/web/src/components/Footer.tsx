import { memo } from 'react';
import { Link } from 'react-router-dom';
import { SiDiscord, SiGithub } from 'react-icons/si';
import { useTranslation } from '../i18n/useTranslation';
import { VscodeMark } from './VscodeMark';
import stats from '../generated/stats.json';
import { PAGE } from '../theme';

/** A footer link. Everything here leaves the site except where `internal` says otherwise. */
interface FooterLink {
    label: string;
    url: string;
    internal?: boolean;
}

export const Footer = memo(() => {
    const { t } = useTranslation();
    const columns: { title: string; links: FooterLink[] }[] = [
        {
            title: t('footer.product'),
            links: [
                { label: t('nav.documentation'), url: '/documentation', internal: true },
                { label: t('nav.playground'), url: '/playground', internal: true },
                { label: t('nav.tools'), url: '/tools', internal: true },
                { label: t('footer.vscode'), url: 'https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet' },
            ],
        },
        {
            title: t('footer.community'),
            links: [
                { label: 'GitHub', url: 'https://github.com/Stoupy51/StewBeet' },
                { label: 'Discord', url: 'https://discord.gg/anxzu6rA9F' },
                { label: 'YouTube', url: 'https://www.youtube.com/watch?v=zkcQn23DRaw' },
                { label: t('footer.reportBug'), url: 'https://github.com/Stoupy51/StewBeet/issues' },
            ],
        },
        {
            title: t('footer.resources'),
            links: [
                { label: 'PyPI', url: 'https://pypi.org/project/stewbeet/' },
                { label: 'PlanetMinecraft', url: 'https://www.planetminecraft.com/data-pack/python-datapack/' },
                { label: t('footer.credits'), url: '/credits', internal: true },
                { label: t('footer.telemetry'), url: '/telemetry', internal: true },
            ],
        },
    ];
    const linkClass = 'text-sm text-ink-400 hover:text-ink-50 transition-colors';

    return (
        <footer className="border-t border-ink-800 bg-ink-950">
            <div className={`${PAGE} py-14`}>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-10">
                    <div className="col-span-2">
                        <div className="flex items-center gap-2.5 font-semibold tracking-tight text-ink-50">
                            <img src="/stewbeet-logo.png" alt="" className="w-7 h-7" />
                            StewBeet
                        </div>
                        <p className="mt-4 max-w-xs text-sm text-ink-400 leading-relaxed">{t('footer.tagline')}</p>
                        <div className="mt-5 flex items-center gap-4 text-ink-400">
                            <a href="https://github.com/Stoupy51/StewBeet" target="_blank" rel="noopener noreferrer" aria-label="GitHub" className="hover:text-ink-50 transition-colors">
                                <SiGithub className="w-5 h-5" aria-hidden="true" />
                            </a>
                            <a href="https://discord.gg/anxzu6rA9F" target="_blank" rel="noopener noreferrer" aria-label="Discord" className="hover:text-ink-50 transition-colors">
                                <SiDiscord className="w-5 h-5" aria-hidden="true" />
                            </a>
                            <a href="https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet" target="_blank" rel="noopener noreferrer" aria-label="VS Code" className="hover:text-ink-50 transition-colors">
                                <VscodeMark className="w-5 h-5" aria-hidden="true" />
                            </a>
                        </div>
                    </div>

                    {columns.map((column) => (
                        <div key={column.title}>
                            <h3 className="font-mono text-xs uppercase tracking-wider text-ink-500">{column.title}</h3>
                            <ul className="mt-4 space-y-2.5">
                                {column.links.map((link) => (
                                    <li key={link.label}>
                                        {link.internal
                                            ? <Link to={link.url} className={linkClass}>{link.label}</Link>
                                            : <a href={link.url} target="_blank" rel="noopener noreferrer" className={linkClass}>{link.label}</a>}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="mt-12 pt-6 border-t border-ink-800 flex flex-col sm:flex-row justify-between gap-3 font-mono text-xs text-ink-500">
                    <p>
                        © {new Date().getFullYear()} StewBeet · {t('footer.by')}{' '}
                        <a href="https://github.com/Stoupy51" target="_blank" rel="noopener noreferrer" className="text-ink-300 hover:text-ink-50 transition-colors">Stoupy51</a>
                    </p>
                    <p>v{stats.version} · {t('footer.license')}</p>
                </div>
            </div>
        </footer>
    );
});
Footer.displayName = 'Footer';
