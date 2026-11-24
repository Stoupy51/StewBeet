import { HiCheck, HiOutlineClipboard } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { PageHeader } from './PageHeader';
import { useTranslation } from '../i18n/useTranslation';
import { useClipboard } from '../hooks/useClipboard';
import { SITE_ORIGIN } from '../utils/pageMeta';
import type { Language } from '../context/LanguageContext';

const STACK = `${SITE_ORIGIN}/img/stack/stewbeet-stack`;
/** The manual GIF weighs 16 MB, so it stays out of the site image and is served from the repository. */
const MANUAL_GIF = 'https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/ingame_manual.gif';

interface MediaItem {
    title: Record<Language, string>;
    text: Record<Language, string>;
    preview: string;
    /** One link per format, the label saying what Discord does with it. */
    files: { label: string; url: string }[];
}

const MEDIA: MediaItem[] = [
    {
        title: { en: 'beet, bolt, mecha and StewBeet', fr: 'beet, bolt, mecha et StewBeet' },
        text: { en: 'Who does what when a pack builds. The GIF plays in Discord, the SVG animates on the web.', fr: 'Qui fait quoi quand un pack se build. Le GIF se joue sur Discord, le SVG s\'anime sur le web.' },
        preview: `${STACK}.en.dark.png`,
        files: [
            { label: 'GIF EN', url: `${STACK}.en.dark.gif` },
            { label: 'GIF FR', url: `${STACK}.fr.dark.gif` },
            { label: 'PNG EN', url: `${STACK}.en.dark.png` },
            { label: 'PNG FR', url: `${STACK}.fr.dark.png` },
            { label: 'PNG EN light', url: `${STACK}.en.light.png` },
            { label: 'PNG FR light', url: `${STACK}.fr.light.png` },
            { label: 'SVG EN', url: `${STACK}.en.dark.svg` },
            { label: 'SVG FR', url: `${STACK}.fr.dark.svg` },
        ],
    },
    {
        title: { en: 'The in-game manual', fr: 'Le manuel en jeu' },
        text: { en: 'Stardust Fragment\'s manual, browsed page by page: every item and its recipes, written by the build.', fr: 'Le manuel de Stardust Fragment, page par page : chaque item et ses recipes, écrits par le build.' },
        preview: `${SITE_ORIGIN}/ingame_manual_poster.jpg`,
        files: [
            { label: 'MP4', url: `${SITE_ORIGIN}/ingame_manual.mp4` },
            { label: 'GIF', url: MANUAL_GIF },
        ],
    },
    {
        title: { en: 'The VS Code extension', fr: 'L\'extension VS Code' },
        text: { en: 'Commands checked inside Python and bolt, and a built command opened at the line that wrote it.', fr: 'Les commandes vérifiées dans le Python et le bolt, et une commande buildée ouverte à la ligne qui l\'a écrite.' },
        preview: `${SITE_ORIGIN}/vscode_extension_poster.jpg`,
        files: [
            { label: 'MP4', url: `${SITE_ORIGIN}/vscode_extension.mp4` },
            { label: 'MP4 beet', url: `${SITE_ORIGIN}/vscode_extension_beet.mp4` },
            { label: 'MP4 bolt', url: `${SITE_ORIGIN}/vscode_extension_bolt.mp4` },
        ],
    },
    {
        title: { en: 'Logo', fr: 'Logo' },
        text: { en: 'The stew pot, as pixel art.', fr: 'La marmite, en pixel art.' },
        preview: `${SITE_ORIGIN}/stewbeet-logo.png`,
        files: [
            { label: 'PNG 256', url: `${SITE_ORIGIN}/stewbeet-logo.png` },
            { label: 'PNG 1024', url: `${SITE_ORIGIN}/stewbeet-1024.png` },
        ],
    },
];

/** A format: its name opens the file, the button copies its address for a chat. */
const FileLink = ({ label, url }: { label: string; url: string }) => {
    const [copied, copy] = useClipboard();
    const { t } = useTranslation();

    return (
        <li className="flex border border-border">
            <a href={url} target="_blank" rel="noopener noreferrer" className="flex items-center min-h-10 px-3 font-mono text-sm hover:text-link transition-colors">{label}</a>
            <button type="button" onClick={() => copy(url)} className="flex items-center justify-center w-10 border-l border-border text-text-muted hover:text-text transition-colors active:scale-[0.98]">
                {copied ? <HiCheck className="text-generated" aria-hidden="true" /> : <HiOutlineClipboard aria-hidden="true" />}
                <span className="sr-only">{copied ? t('copy.copied') : `${t('copy.action')} ${label}`}</span>
            </button>
        </li>
    );
};

/** Every image and video worth sending to someone, each format a link to copy. */
export const MediaPage = () => {
    const { t, language } = useTranslation();

    return (
        <div className="min-h-screen">
            <Navbar />
            <main>
                <PageHeader title={t('media.title')} lead={t('media.lead')} />
                {MEDIA.map((item) => (
                    <section key={item.preview} className="frame px-4 py-10 lg:px-12 border-t border-border grid gap-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] lg:gap-12">
                        <img src={item.preview} alt="" loading="lazy" className={`max-w-full max-h-72 w-auto border border-border ${item.preview.endsWith('logo.png') ? 'pixelated max-w-[8rem]' : ''}`} />
                        <div>
                            <h2 className="text-[1.5rem] leading-tight font-bold">{item.title[language]}</h2>
                            <p className="mt-2 text-text-muted text-pretty">{item.text[language]}</p>
                            <ul className="mt-5 flex flex-wrap gap-2">
                                {item.files.map((file) => <FileLink key={file.url} {...file} />)}
                            </ul>
                        </div>
                    </section>
                ))}
            </main>
            <Footer />
        </div>
    );
};
