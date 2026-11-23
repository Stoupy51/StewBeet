import { Link } from 'react-router-dom';
import { HiRefresh } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useIntro } from '../hooks/useIntro';
import { TrustStrip } from './TrustStrip';
import { DOC_PAGES, docHref } from '../docsPages';
import heroCode from '../generated/heroCode.json';
import { BLOCK_FILES } from '../heroBuild';
import stats from '../generated/stats.json';

const RELEASES_URL = 'https://github.com/Stoupy51/StewBeet/releases';
const BLOCK_RENDER = '/generated/hero/resource_pack__assets__stardust__textures__font__high_res__life_crystal_block.png';
const CRYSTAL_TEXTURE = '/img/hero/life_crystal.png';
/** Taken in Minecraft 26.3 with Stardust Fragment's built packs, the build's last frame. */
const INGAME_CAPTURE = '/img/hero/life_crystal_block_ingame.webp';

/** The name and lore of the block, as `playground/hero/src/definitions.py` gives them and the game shows them. */
const BLOCK_NAME = 'Life Crystal Block';
const BLOCK_LORE = 'Break it to get the crystal back';

function daysSince(iso: string): number {
    return Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000));
}

function releaseAge(days: number, t: (key: string) => string): string {
    if (days === 0) return t('hero.releasedToday');
    if (days === 1) return t('hero.releasedYesterday');
    return t('hero.releasedDaysAgo').replace('{n}', String(days));
}

const count = (part: string) => BLOCK_FILES.filter((leaf) => leaf.path?.includes(part)).length;
const TOOLTIP_ROWS: [string, number][] = [
    ['hero.blockFunctions', count('/function/custom_blocks/')],
    ['hero.crafterRecipes', count('/smithed_crafter/')],
    ['hero.lootTables', count('/loot_table/')],
    ['hero.manualPages', count('/dialog/manual/')],
    ['hero.resourcePackFiles', count('resource_pack/')],
];

const quickstart = DOC_PAGES.find((page) => page.src.en === 'quickstart/en.md')!;

/** Starts the build animation over: the attribute comes off, the browser forgets the animations, and it goes back on. */
function replayBuild() {
    const root = document.documentElement;
    delete root.dataset.intro;
    void root.offsetWidth;
    root.dataset.intro = 'play';
}

/**
 * The definition of a real block, and what the build made of it: its items dropping into
 * inventory slots and the game's item tooltip listing the files. On a desktop it sits beside the
 * headline, overlapping its code panel; on a phone it is the section under the hero.
 */
const BuildProof = () => {
    const { t } = useTranslation();
    const block = heroCode.snippets.find(({ id }) => id === 'block') ?? heroCode.snippets[0];

    return (
        <div className="mt-16 lg:mt-0 min-w-0 flex flex-col">
            <h2 className="text-2xl leading-tight font-bold lg:sr-only">{t('hero.proofTitle')}</h2>

            <div className="mt-3.5 lg:mt-0 bg-code-surface border border-code-border text-code-text">
                <p className="flex items-center h-9 lg:h-10 px-3 lg:px-3.5 border-b border-code-border font-mono text-xs text-code-text-muted">{t('hero.codeCaption')}</p>
                <div className="hero-code" dangerouslySetInnerHTML={{ __html: block.html }} />
            </div>

            <div className="mt-5 lg:-mt-[18px] lg:ml-16 grid lg:grid-cols-[auto_auto] lg:justify-start items-start gap-2.5 lg:gap-x-3.5 lg:gap-y-3">
                <div className="mc-panel self-start flex gap-0.5 p-3 lg:p-2.5 outline outline-4 outline-surface">
                    <div className="mc-slot"><img src={BLOCK_RENDER} alt={BLOCK_NAME} width={32} height={32} className="build-drop" style={{ '--slot': 0 } as React.CSSProperties} /></div>
                    <div className="mc-slot"><img src={CRYSTAL_TEXTURE} alt="Life Crystal" width={32} height={32} className="pixelated build-drop" style={{ '--slot': 1 } as React.CSSProperties} /></div>
                    <div className="mc-slot" />
                    <div className="mc-slot" />
                    <div className="mc-slot lg:hidden" />
                    <div className="mc-slot lg:hidden" />
                </div>
                <div className="mc-tooltip self-start ml-[26px] lg:ml-0 lg:mt-[26px] lg:row-span-2 px-2.5 py-2" role="note">
                    <p className="text-white">{BLOCK_NAME}</p>
                    <p className="text-mc-lore italic">{BLOCK_LORE}</p>
                    <p className="mt-2 build-rise" style={{ '--row': 0 } as React.CSSProperties}>{t('hero.writtenByBuild')}</p>
                    {TOOLTIP_ROWS.map(([key, value], index) => (
                        <p key={key} className="build-rise" style={{ '--row': index + 1 } as React.CSSProperties}>
                            {t(key).replace('{n}', String(value))}
                        </p>
                    ))}
                </div>
                <figure className="build-rise lg:col-start-1 lg:row-start-2 lg:w-[11rem]" style={{ '--row': TOOLTIP_ROWS.length + 2 } as React.CSSProperties}>
                    <img src={INGAME_CAPTURE} alt={t('hero.ingameAlt')} width={528} height={396} className="w-full border border-border" />
                    <figcaption className="mt-1.5 font-pixel text-[0.6875rem] text-text-muted">{t('hero.ingameCaption')}</figcaption>
                </figure>
            </div>

            <p className="mt-3 lg:mt-4 text-[0.8125rem] leading-normal text-text-muted">
                {t('hero.proofCaption').replace('{n}', String(BLOCK_FILES.length))}{' '}
                <button type="button" onClick={replayBuild} className="motion-reduce:hidden inline-flex items-center gap-1 min-h-6 text-link hover:text-text transition-colors">
                    <HiRefresh className="w-3.5 h-3.5" aria-hidden="true" />
                    {t('hero.replay')}
                </button>
            </p>
        </div>
    );
};

export const Hero = () => {
    const { t, language } = useTranslation();
    useIntro();

    return (
        <section id="hero" className="pt-14 lg:pt-16">
            <div className="frame px-4 pt-7 pb-10 lg:px-12 lg:py-16 lg:grid lg:grid-cols-[minmax(0,1fr)_35rem] lg:gap-14">
                <div className="flex flex-col">
                    <a href={RELEASES_URL} target="_blank" rel="noopener noreferrer" className="self-start inline-block min-h-6 leading-6 font-pixel text-[0.6875rem] lg:text-[0.8125rem] text-text-muted hover:text-text transition-colors">
                        v{stats.version}
                        {/* The age is computed again in the browser, days after the prerender, so the text may differ. */}
                        {stats.releasedAt && <span suppressHydrationWarning>, {releaseAge(daysSince(stats.releasedAt), t)}</span>}
                        , {t('hero.license')}
                    </a>

                    <h1 className="mt-3.5 lg:mt-4 text-[2.25rem] leading-[1.15] lg:text-[3.25rem] lg:leading-[1.12] font-bold text-balance">
                        {t('hero.title')}
                    </h1>

                    <p className="mt-[18px] lg:mt-[22px] text-[1.0625rem] lg:text-[1.1875rem] leading-normal text-text-muted text-pretty">
                        {t('hero.subtitle')}
                    </p>

                    <div className="mt-6 lg:mt-7 flex flex-col lg:flex-row gap-1.5 lg:gap-3">
                        <Link to={docHref(quickstart, language)} className="flex items-center justify-center h-12 lg:px-[22px] bg-primary hover:bg-primary-hover text-on-primary font-semibold transition-colors active:scale-[0.98]">
                            {t('hero.readQuickstart')}
                        </Link>
                        <Link to="/docs" className="flex items-center justify-center h-11 lg:h-12 lg:px-[22px] lg:border lg:border-border text-link lg:text-text font-semibold hover:text-text lg:hover:border-ink-600 transition-colors">
                            {t('hero.browseDocs')}
                        </Link>
                    </div>

                    <p className="mt-[18px] lg:mt-[22px] pt-4 lg:pt-0 border-t border-border lg:border-0 text-[0.9375rem] leading-normal text-text-muted">
                        <strong className="font-semibold text-text">{t('hero.newToPython')}</strong> {t('hero.newToPythonText')}
                    </p>

                    <div className="hidden lg:flex flex-1 flex-col justify-end pt-10">
                        <TrustStrip className="flex pt-6 border-t border-border" />
                    </div>
                </div>

                <BuildProof />
            </div>
        </section>
    );
};
