import { useContext, useState } from 'react';
import { HiCheck, HiOutlineClipboard } from 'react-icons/hi';
import { PAGE_THEMES, PrehighlightedCode, codeKey, useShiki } from '../hooks/useShiki';
import { useClipboard } from '../hooks/useClipboard';
import { useTranslation } from '../i18n/useTranslation';
import { metaValue } from '../utils/docMarkdown';

/** Shell languages and the prompt drawn before each of their lines, which copying leaves out. */
const PROMPTS: Record<string, string> = {
    bash: 'md-shell', sh: 'md-shell', shell: 'md-shell', zsh: 'md-shell', console: 'md-shell',
    powershell: 'md-shell md-shell-ps', ps1: 'md-shell md-shell-ps', pwsh: 'md-shell md-shell-ps', cmd: 'md-shell md-shell-ps',
};

export interface CodeSample {
    code: string;
    language: string;
}

const CopyButton = ({ text }: { text: string }) => {
    const [copied, copy] = useClipboard();
    const { t } = useTranslation();
    return (
        <button
            type="button"
            onClick={() => copy(text)}
            className="ml-auto flex items-center gap-1.5 h-10 min-w-10 px-3 text-code-text-muted hover:text-code-text transition-colors"
        >
            {copied && <span className="font-sans text-xs text-generated">{t('copy.copied')}</span>}
            {copied ? <HiCheck className="w-4 h-4 text-generated" aria-hidden="true" /> : <HiOutlineClipboard className="w-4 h-4" aria-hidden="true" />}
            <span className="sr-only">{copied ? '' : t('copy.action')}</span>
        </button>
    );
};

/** A block highlighted at build time carries its key, which main.tsx reads its markup back by when it hydrates a server-rendered page. */
const Highlighted = ({ code, language, hidden, className = '' }: CodeSample & { hidden?: boolean; className?: string }) => {
    const html = useShiki(code, language, PAGE_THEMES);
    const key = codeKey(language, code);
    const isPrebuilt = key in useContext(PrehighlightedCode);
    return <div hidden={hidden} data-code-key={isPrebuilt ? key : undefined} className={`${PROMPTS[language] ?? ''} ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
};

/**
 * A fenced block, titled by the `title="..."` after its language, "Terminal" for a shell, or its
 * language. Plain text has no title bar, only the copy button in its corner.
 */
export const CodeBlock = ({ code, language, meta, style }: CodeSample & { meta?: string; style?: React.CSSProperties }) => {
    const { t } = useTranslation();
    const title = metaValue(meta, 'title') ?? (PROMPTS[language] ? t('code.terminal') : language === 'text' ? '' : language);
    return (
        <div className="md-code" style={style}>
            {title ? (
                <div className="md-code-head">
                    <span className="truncate">{title}</span>
                    <CopyButton text={code} />
                </div>
            ) : (
                <div className="absolute top-0 right-0"><CopyButton text={code} /></div>
            )}
            <Highlighted code={code} language={language} className={title ? '' : 'pr-9'} />
        </div>
    );
};

/** Consecutive fenced blocks marked `tab="..."`, one panel with a tab each. Every tab stays rendered, so switching never re-highlights. */
export const CodeTabs = ({ tabs, style }: { tabs: (CodeSample & { label: string })[]; style?: React.CSSProperties }) => {
    const [active, setActive] = useState(0);
    return (
        <div className="md-code" style={style}>
            <div className="md-code-head pl-0" role="tablist">
                {tabs.map((tab, index) => (
                    <button
                        key={tab.label}
                        type="button"
                        role="tab"
                        aria-selected={index === active}
                        onClick={() => setActive(index)}
                        className={`h-10 px-3.5 font-sans text-[0.8125rem] transition-colors ${
                            index === active ? 'bg-code-text/[0.08] text-code-text font-semibold' : 'text-code-text-muted hover:text-code-text'
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
                <CopyButton text={tabs[active].code} />
            </div>
            {tabs.map((tab, index) => <Highlighted key={tab.label} code={tab.code} language={tab.language} hidden={index !== active} />)}
        </div>
    );
};
