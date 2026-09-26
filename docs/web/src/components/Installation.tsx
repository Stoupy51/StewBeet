import { useState } from 'react';
import { HiCheck, HiOutlineClipboard } from 'react-icons/hi';
import stats from '../generated/stats.json';
import { Templates } from './Templates';
import { CodeTab } from './CodeTab';
import { useTranslation } from '../i18n/useTranslation';
import { useClipboard } from '../hooks/useClipboard';
import { PAGE, SECTION_TITLE } from '../theme';

type Tone = 'muted' | 'ok' | 'info' | 'warn';

interface Step {
    titleKey: string;
    descKey: string;
    command: string;
    output: { text: string; tone?: Tone }[];
}

const TONE: Record<Tone, string> = {
    muted: 'text-ink-400',
    ok: 'text-leaf-400',
    info: 'text-sky-300',
    warn: 'text-mc-gold',
};

const STEPS: Step[] = [
    {
        titleKey: 'installation.step1',
        descKey: 'installation.step1Desc',
        command: 'python --version',
        output: [{ text: 'Python 3.14.7' }],
    },
    {
        titleKey: 'installation.step2',
        descKey: 'installation.step2Desc',
        command: 'pip install stewbeet',
        output: [
            { text: 'Collecting stewbeet' },
            { text: `Downloading stewbeet-${stats.version}-py3-none-any.whl (45 kB)` },
            { text: 'Installing collected packages: stewbeet' },
            { text: `Successfully installed stewbeet-${stats.version}`, tone: 'ok' },
        ],
    },
    {
        titleKey: 'installation.step3',
        descKey: 'installation.step3Desc',
        command: 'stewbeet init',
        output: [
            { text: '[INFO] Available templates:', tone: 'ok' },
            { text: '  - "minimal":   A very minimal template using only one `stewbeet` plugin.' },
            { text: '  - "basic":     (Recommended) Complete configuration with all plugins but WITHOUT coded examples.' },
            { text: '  - "extensive": Complete template with ALL features and coded examples (ruby ore, tools, etc.).' },
            { text: '' },
            { text: 'Please choose a template from the list above: basic', tone: 'warn' },
            { text: '[INFO] Template initialized successfully!', tone: 'ok' },
        ],
    },
    {
        titleKey: 'installation.step4',
        descKey: 'installation.step4Desc',
        command: 'stewbeet',
        output: [
            { text: '[PROGRESS] resource_pack.sounds: 44.76ms', tone: 'info' },
            { text: '[PROGRESS] resource_pack.item_models: 3.60ms', tone: 'info' },
            { text: '[PROGRESS] custom_recipes: 6.55ms', tone: 'info' },
            { text: 'Creating manual pages: 100%|############| 28/28 [69.36it/s]', tone: 'muted' },
            { text: '[PROGRESS] ingame_manual: 0.66s', tone: 'info' },
            { text: '[PROGRESS] datapack.custom_blocks: 3.10ms', tone: 'info' },
            { text: '[PROGRESS] datapack.loot_tables: 3.13ms', tone: 'info' },
            { text: '[INFO] Official libraries used: Common Signals, Smithed Custom Block, Smithed Crafter, Furnace NBT Recipes, SmartOreGeneration, Bookshelf Math', tone: 'ok' },
            { text: 'Generating lang file: 100%|##########| 198/198 [4731.85it/s]', tone: 'muted' },
            { text: '[PROGRESS] merge_smithed_weld: 0.58s', tone: 'info' },
            { text: '' },
            { text: '[DEBUG] Total execution time: 4.96s', tone: 'muted' },
            { text: 'Done!', tone: 'ok' },
        ],
    },
];

const CopyIcon = ({ command }: { command: string }) => {
    const { t } = useTranslation();
    const [copied, copy] = useClipboard();
    return (
        <button
            type="button"
            onClick={() => copy(command)}
            aria-label={copied ? t('copy.copied') : t('copy.command')}
            className="flex items-center gap-1.5 font-mono text-xs text-ink-400 hover:text-ink-50 transition-colors"
        >
            {copied ? <HiCheck className="text-leaf-400" aria-hidden="true" /> : <HiOutlineClipboard aria-hidden="true" />}
            {copied ? t('copy.copied') : t('copy.action')}
        </button>
    );
};

export const Installation: React.FC = () => {
    const { t } = useTranslation();
    const [active, setActive] = useState(0);
    const step = STEPS[active];

    return (
        <section id="installation" className="py-14 md:py-28 border-t border-ink-800 scroll-mt-14">
            <div className={PAGE}>
                <div data-rise className="max-w-3xl">
                    <h2 className={SECTION_TITLE}>{t('installation.title')}</h2>
                </div>

                <div data-rise className="mt-12 grid grid-cols-1 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] gap-6">
                    <ol className="flex flex-col gap-1">
                        {STEPS.map((item, index) => {
                            const isActive = index === active;
                            return (
                                <li key={item.command}>
                                    <button
                                        onClick={() => setActive(index)}
                                        aria-pressed={isActive}
                                        className={`w-full text-left flex gap-4 p-4 rounded-panel border transition-colors ${
                                            isActive ? 'border-ink-700 bg-ink-900' : 'border-transparent hover:bg-ink-900/60'
                                        }`}
                                    >
                                        <span className={`font-mono text-sm pt-0.5 ${isActive ? 'text-beet-400' : 'text-ink-500'}`}>
                                            {String(index + 1).padStart(2, '0')}
                                        </span>
                                        <span className="min-w-0">
                                            <span className={`block font-medium ${isActive ? 'text-ink-50' : 'text-ink-200'}`}>{t(item.titleKey)}</span>
                                            <span className="block mt-0.5 text-sm text-ink-400">{t(item.descKey)}</span>
                                            <code className="block mt-2 font-mono text-xs text-ink-300">$ {item.command}</code>
                                        </span>
                                    </button>
                                </li>
                            );
                        })}
                    </ol>

                    <div className="flex flex-col gap-3 min-w-0">
                        <CodeTab path={t('installation.terminal')} accessory={<CopyIcon command={step.command} />} className="code-dark h-[26rem]">
                            <div className="flex-1 overflow-auto custom-scrollbar p-5 font-mono text-[0.8125rem] leading-relaxed">
                                <p className="text-ink-100">
                                    <span className="text-beet-400 select-none">$ </span>{step.command}
                                </p>
                                <div className="mt-2 space-y-0.5 text-ink-300">
                                    {step.output.map((line, index) => (
                                        <p key={index} className={`${line.tone ? TONE[line.tone] : ''} ${line.text === '' ? 'h-4' : ''} break-words`}>
                                            {line.text}
                                        </p>
                                    ))}
                                </div>
                            </div>
                        </CodeTab>

                        {/* pip is the command in the steps, so uv gets its equivalent here */}
                        <p className="text-xs text-ink-400 leading-relaxed">
                            {t('installation.uvNote')}{' '}
                            <code className="font-mono text-ink-200">uvx stewbeet init</code>{' '}
                            {t('installation.uvNoteThen')}{' '}
                            <code className="font-mono text-ink-200">uv run stewbeet build</code>{' '}
                            {t('installation.uvNoteEnd')}
                        </p>
                    </div>
                </div>

                <Templates />
            </div>
        </section>
    );
};
