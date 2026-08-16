import { memo } from 'react';
import { Link } from 'react-router-dom';
import { HiExternalLink } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { HEADING, TEXT_ACCENT_HOVER } from '../theme';

/** A footer link. Everything here leaves the site except where `internal` says otherwise. */
interface FooterLink {
    label: string;
    url: string;
    internal?: boolean;
}

export const Footer = memo(() => {
    const { t } = useTranslation();
    const links: Record<string, FooterLink[]> = {
        [t('footer.community')]: [
            { label: t('footer.github'), url: 'https://github.com/Stoupy51/StewBeet' },
            { label: t('footer.discord'), url: 'https://discord.gg/anxzu6rA9F' },
            { label: t('footer.youtube'), url: 'https://www.youtube.com/watch?v=zkcQn23DRaw' },
        ],
        [t('footer.resources')]: [
            { label: t('footer.pypiPackage'), url: 'https://pypi.org/project/stewbeet/' },
            { label: t('footer.planetMinecraft'), url: 'https://www.planetminecraft.com/data-pack/python-datapack/' },
            { label: t('footer.credits'), url: '/credits', internal: true },
            { label: t('footer.reportBug'), url: 'https://github.com/Stoupy51/StewBeet/issues' },
            { label: t('footer.telemetry'), url: '/telemetry', internal: true },
        ]
    };
    const linkClass = 'text-slate-400 hover:text-white transition-colors text-sm flex items-center gap-1 group';

    return (
        <footer className="bg-slate-950 border-t border-white/10 relative">
            <div className="max-w-6xl mx-auto px-4 py-16 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
                    {/* Logo & Description */}
                    <div className="md:col-span-2">
                        <div className={`flex items-center gap-2 text-2xl font-bold ${HEADING} mb-4`}>
                            <img src="/stewbeet-logo.png" alt="StewBeet" className="w-8 h-8" />
                            StewBeet
                        </div>
                        <p className="text-slate-400 text-sm leading-relaxed">
                            {t('footer.tagline')}
                        </p>
                        <div className="flex gap-3 mt-6">
                            <a href="https://github.com/Stoupy51/StewBeet" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white transition-colors">
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" /></svg>
                            </a>
                            <a href="https://discord.gg/anxzu6rA9F" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white transition-colors">
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" /></svg>
                            </a>
                        </div>
                    </div>

                    {/* Links Sections */}
                    {Object.entries(links).map(([category, items]) => (
                        <div key={category}>
                            <h3 className="text-white font-semibold mb-4">{category}</h3>
                            <ul className="space-y-2">
                                {items.map((link) => (
                                    <li key={link.label}>
                                        {link.internal ? (
                                            <Link to={link.url} className={linkClass}>
                                                {link.label}
                                            </Link>
                                        ) : (
                                            <a
                                                href={link.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className={linkClass}
                                            >
                                                {link.label}
                                                <HiExternalLink className="text-xs opacity-0 group-hover:opacity-100 transition-opacity" />
                                            </a>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* The shields.io badges that used to sit here are now the trust strip under
                    the hero: same numbers, baked at build time, seen by everyone rather than
                    only by visitors who scrolled the whole page. */}
                <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="text-slate-400 text-sm">
                        © {new Date().getFullYear()} {t('footer.copyright')} <a href="https://github.com/Stoupy51" target="_blank" rel="noopener noreferrer" className={TEXT_ACCENT_HOVER}>Stoupy51</a>
                    </div>
                    <p className="text-slate-400 text-sm font-mono">{t('footer.license')}</p>
                </div>
            </div>
        </footer>
    );
});
Footer.displayName = 'Footer';
