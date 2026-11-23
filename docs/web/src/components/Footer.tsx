import { memo } from 'react';
import { Link } from 'react-router-dom';
import { SiDiscord, SiGithub } from 'react-icons/si';
import { useTranslation } from '../i18n/useTranslation';
import { VscodeMark } from './VscodeMark';
import stats from '../generated/stats.json';

/** A footer link. Everything here leaves the site except where `internal` says otherwise. */
interface FooterLink {
    label: string;
    url: string;
    internal?: boolean;
}

/** `wide` matches the docs' wider frame, so its borders run on from the page's. */
export const Footer = memo(({ wide = false }: { wide?: boolean }) => {
    const { t } = useTranslation();
    const columns: { title: string; links: FooterLink[] }[] = [
        {
            title: t('footer.product'),
            links: [
                { label: t('nav.documentation'), url: '/docs', internal: true },
                { label: t('nav.playground'), url: '/tools/playground', internal: true },
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
    const linkClass = 'inline-flex items-center min-h-6 text-sm text-text-muted hover:text-text transition-colors';

    return (
        <footer className={`frame ${wide ? 'frame-wide' : ''} px-4 py-12 lg:px-12 border-t border-border`}>
            <div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-10">
                    <div className="col-span-2">
                        <div className="flex items-center gap-2.5 font-bold">
                            <img src="/stewbeet-logo.png" alt="" width={28} height={28} className="pixelated w-7 h-7" />
                            StewBeet
                        </div>
                        <p className="mt-4 max-w-xs text-sm text-text-muted leading-relaxed">{t('footer.tagline')}</p>
                        <div className="mt-5 flex items-center gap-4 text-text-muted">
                            <a href="https://github.com/Stoupy51/StewBeet" target="_blank" rel="noopener noreferrer" aria-label="GitHub" className="p-1 -m-1 hover:text-text transition-colors">
                                <SiGithub className="w-5 h-5" aria-hidden="true" />
                            </a>
                            <a href="https://discord.gg/anxzu6rA9F" target="_blank" rel="noopener noreferrer" aria-label="Discord" className="p-1 -m-1 hover:text-text transition-colors">
                                <SiDiscord className="w-5 h-5" aria-hidden="true" />
                            </a>
                            <a href="https://marketplace.visualstudio.com/items?itemName=stoupy.stewbeet" target="_blank" rel="noopener noreferrer" aria-label="VS Code" className="p-1 -m-1 hover:text-text transition-colors">
                                <VscodeMark className="w-5 h-5" aria-hidden="true" />
                            </a>
                        </div>
                    </div>

                    {columns.map((column) => (
                        <div key={column.title}>
                            <h3 className="label">{column.title}</h3>
                            <ul className="mt-4 space-y-1">
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

                <div className="mt-12 pt-6 border-t border-border flex flex-col sm:flex-row justify-between gap-3 font-mono text-xs text-text-muted">
                    <p>
                        © {new Date().getFullYear()} StewBeet · {t('footer.by')}{' '}
                        <a href="https://github.com/Stoupy51" target="_blank" rel="noopener noreferrer" className="text-text hover:text-link transition-colors">Stoupy51</a>
                    </p>
                    <p>v{stats.version} · {t('footer.license')}</p>
                </div>
            </div>
        </footer>
    );
});
Footer.displayName = 'Footer';
