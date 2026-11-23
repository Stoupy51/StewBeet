import { HiCheck, HiOutlineClipboard } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useClipboard } from '../hooks/useClipboard';

/** A shell command as a button: one click copies it, and the icon confirms for two seconds. */
export const CopyCommand = ({ command }: { command: string }) => {
    const [copied, copy] = useClipboard();
    const { t } = useTranslation();

    return (
        <button
            type="button"
            onClick={() => copy(command)}
            className="group flex items-center justify-between gap-3 min-w-0 h-11 px-4 bg-code-surface border border-code-border hover:border-ink-600 text-code-text transition-colors active:scale-[0.98]"
        >
            <span className="font-mono text-sm truncate">
                <span className="text-code-text-muted select-none">$ </span>{command}
            </span>
            {copied
                ? <HiCheck className="flex-shrink-0 text-generated" aria-hidden="true" />
                : <HiOutlineClipboard className="flex-shrink-0 text-code-text-muted group-hover:text-code-text transition-colors" aria-hidden="true" />}
            <span className="sr-only">{copied ? t('copy.copied') : t('copy.command')}</span>
        </button>
    );
};
