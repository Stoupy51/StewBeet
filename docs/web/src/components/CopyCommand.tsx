import { HiCheck, HiOutlineClipboard } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { useClipboard } from '../hooks/useClipboard';

const VARIANT = {
    default: 'border-ink-700 bg-ink-900 hover:border-ink-500 text-ink-100',
    primary: 'border-beet-500 bg-beet-600 hover:bg-beet-700 text-white',
} as const;

/** A shell command as a button: one click copies it, and the icon confirms for two seconds. */
export const CopyCommand = ({ command, variant = 'default', className = '' }: {
    command: string;
    variant?: keyof typeof VARIANT;
    className?: string;
}) => {
    const [copied, copy] = useClipboard();
    const { t } = useTranslation();

    return (
        <button
            type="button"
            onClick={() => copy(command)}
            className={`group inline-flex items-center gap-3 h-11 px-4 rounded-control border transition-colors ${VARIANT[variant]} ${className}`}
        >
            <span className="font-mono text-sm whitespace-nowrap">
                <span className="opacity-50 select-none">$ </span>{command}
            </span>
            {copied
                ? <HiCheck className={`flex-shrink-0 ${variant === 'primary' ? '' : 'text-leaf-400'}`} aria-hidden="true" />
                : <HiOutlineClipboard className="flex-shrink-0 opacity-60 group-hover:opacity-100 transition-opacity" aria-hidden="true" />}
            <span className="sr-only">{copied ? t('copy.copied') : t('copy.command')}</span>
        </button>
    );
};
