import { useState } from 'react';
import { HiArrowRight, HiCheck, HiClipboard } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n/useTranslation';
import { BTN_PRIMARY, BTN_SECONDARY, ICON_ACCENT } from '../theme';

/**
 * The page previously ended on the template cards and went straight into the footer, so a
 * visitor who read the whole thing and was persuaded had no action in front of them. This
 * is the safety net: one message, one primary action, on a background that separates it
 * from every section above.
 */
export const FinalCTA: React.FC = () => {
    const { t, language } = useTranslation();
    const [copied, setCopied] = useState(false);
    const gettingStarted = `/markdown?src=${encodeURIComponent(language === 'fr' ? '0_getting_started/fr.md' : '0_getting_started/en.md')}`;

    const handleCopy = () => {
        navigator.clipboard.writeText('pip install stewbeet');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <section className="relative bg-mc-emerald/[0.07] border-y border-mc-emerald/25">
            <div className="max-w-3xl mx-auto px-4 py-20 text-center">
                <h2 className="text-3xl md:text-4xl font-bold text-slate-50 mb-4">{t('finalCta.title')}</h2>
                <p className="text-lg text-slate-300 mb-9 max-w-xl mx-auto leading-relaxed">{t('finalCta.subtitle')}</p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
                    <Link
                        to={gettingStarted}
                        className={`inline-flex items-center gap-2 px-7 py-3 rounded-panel font-semibold transition-colors ${BTN_PRIMARY}`}
                    >
                        {t('finalCta.action')}
                        <HiArrowRight aria-hidden="true" />
                    </Link>

                    <button
                        onClick={handleCopy}
                        className={`group inline-flex items-center gap-3 px-5 py-3 rounded-panel transition-colors ${BTN_SECONDARY}`}
                    >
                        <span className="font-mono text-sm">
                            <span className={ICON_ACCENT}>$</span> pip install stewbeet
                        </span>
                        {copied
                            ? <HiCheck className="text-mc-emerald" aria-hidden="true" />
                            : <HiClipboard className="text-slate-400 group-hover:text-slate-200 transition-colors" aria-hidden="true" />}
                        <span className="sr-only">{copied ? t('finalCta.copied') : t('finalCta.copyCommand')}</span>
                    </button>
                </div>

                <p className="text-sm text-slate-400">{t('finalCta.microcopy')}</p>
            </div>
        </section>
    );
};
