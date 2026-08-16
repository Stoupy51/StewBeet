import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiArrowLeft, HiCheck, HiExternalLink, HiX } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { TelemetryChart, type TelemetryDay } from './TelemetryChart';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { HEADING, SELECTION_BRAND, TEXT_ACCENT, TEXT_ACCENT_HOVER } from '../theme';

/** The file the whole feature lives in. Linking the repository root instead would prove nothing. */
const IMPLEMENTATION_URL = 'https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/telemetry.py';

/** Shape of `GET /api/telemetry/builds?days=30`. */
interface TelemetrySeries {
    days: TelemetryDay[];
    total: number;
    avgDurationSeconds: number;
}

/** The three collected fields, and the eleven things that are never looked at, as translation keys. */
const COLLECTED = ['telemetry.collectedVersion', 'telemetry.collectedPython', 'telemetry.collectedDuration', 'telemetry.collectedDay'] as const;
const NOT_COLLECTED = [
    'telemetry.notProject', 'telemetry.notCode', 'telemetry.notPaths', 'telemetry.notUsername',
    'telemetry.notHostname', 'telemetry.notEnv', 'telemetry.notGit', 'telemetry.notIp', 'telemetry.notIdentifiers',
] as const;

/**
 * The public telemetry page.
 *
 * It exists to answer three questions without the reader having to trust a paragraph: what leaves
 * their machine, how to stop it, and where the code that sends it is. The numbers at the top are
 * the same aggregates anyone can pull from the public endpoint.
 */
export const TelemetryPage: React.FC = () => {
    const { t, language } = useTranslation();
    const motionSafe = useMotionSafe();
    const [series, setSeries] = useState<TelemetrySeries | null>(null);
    const [failed, setFailed] = useState(false);

    useEffect(() => {
        let cancelled = false;
        fetch('/api/telemetry/builds?days=30')
            .then(response => (response.ok ? response.json() as Promise<TelemetrySeries> : Promise.reject(new Error(String(response.status)))))
            .then(data => { if (!cancelled && data.days?.length) setSeries(data); })
            .catch(() => { if (!cancelled) setFailed(true); });
        return () => { cancelled = true; };
    }, []);

    const locale = language === 'fr' ? 'fr-FR' : 'en-US';

    return (
        <div className={`min-h-screen bg-slate-950 text-slate-100 ${SELECTION_BRAND}`}>
            <Navbar />

            <main>
                <div className="relative z-10 pt-28 pb-8 px-4">
                    <div className="max-w-3xl mx-auto text-center">
                        <motion.h1
                            {...motionSafe({ initial: { y: 20 }, animate: { y: 0 } })}
                            className={`text-3xl md:text-4xl font-bold mb-3 ${HEADING}`}
                        >
                            {t('telemetry.title')}
                        </motion.h1>
                        <motion.p
                            {...motionSafe({ initial: { y: 20 }, animate: { y: 0 }, transition: { delay: 0.1 } })}
                            className="text-slate-300"
                        >
                            {t('telemetry.subtitle')}
                        </motion.p>
                    </div>
                </div>

                {/* ── Public statistics ──────────────────────────────────────── */}
                <div className="relative z-10 pb-12 px-4">
                    <motion.section
                        {...motionSafe({ initial: { y: 20 }, animate: { y: 0 }, transition: { delay: 0.15 } })}
                        className="max-w-3xl mx-auto rounded-panel border border-white/10 bg-slate-900/40 p-6 md:p-8"
                    >
                        <h2 className="text-sm font-medium uppercase tracking-wide text-slate-400">{t('telemetry.statsTitle')}</h2>

                        {series ? (
                            <>
                                <p className={`mt-3 mb-1 text-4xl md:text-5xl font-bold tabular-nums ${TEXT_ACCENT}`}>
                                    {series.total.toLocaleString(locale)}
                                </p>
                                <p className="mb-8 text-sm text-slate-400">
                                    {t('telemetry.buildsLabel')}
                                    {series.avgDurationSeconds > 0 && ` · ${t('telemetry.averageBuild')} ${series.avgDurationSeconds.toFixed(1)}s`}
                                </p>
                                <TelemetryChart days={series.days} />
                            </>
                        ) : (
                            <p className="mt-4 text-slate-400">{failed ? t('telemetry.statsUnavailable') : t('telemetry.statsLoading')}</p>
                        )}
                    </motion.section>
                </div>

                {/* ── What is collected ──────────────────────────────────────── */}
                <div className="relative z-10 pb-12 px-4">
                    <div className="max-w-3xl mx-auto">
                        <h2 className={`text-xl font-bold mb-2 ${HEADING}`}>{t('telemetry.collectedTitle')}</h2>
                        <p className="text-sm text-slate-400 mb-5">{t('telemetry.collectedWhy')}</p>

                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="rounded-panel border border-white/10 bg-slate-900/40 p-5">
                                <h3 className="text-sm font-semibold text-slate-200 mb-3">{t('telemetry.collectedHeading')}</h3>
                                <ul className="space-y-2">
                                    {COLLECTED.map(key => (
                                        <li key={key} className="flex items-start gap-2 text-sm text-slate-300">
                                            <HiCheck className={`mt-0.5 flex-shrink-0 ${TEXT_ACCENT}`} aria-hidden="true" />
                                            {t(key)}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="rounded-panel border border-white/10 bg-slate-900/40 p-5">
                                <h3 className="text-sm font-semibold text-slate-200 mb-3">{t('telemetry.notCollectedHeading')}</h3>
                                <ul className="space-y-2">
                                    {NOT_COLLECTED.map(key => (
                                        <li key={key} className="flex items-start gap-2 text-sm text-slate-400">
                                            <HiX className="mt-0.5 flex-shrink-0 text-mc-redstone" aria-hidden="true" />
                                            {t(key)}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        <p className="mt-5 text-sm text-slate-400">{t('telemetry.aggregateNote')}</p>
                    </div>
                </div>

                {/* ── Disabling it */}
                <div className="relative z-10 pb-12 px-4">
                    <div className="max-w-3xl mx-auto">
                        <h2 className={`text-xl font-bold mb-2 ${HEADING}`}>{t('telemetry.disableTitle')}</h2>
                        <p className="text-sm text-slate-400 mb-4">{t('telemetry.disableIntro')}</p>

                        <pre className="rounded-panel border border-white/10 bg-slate-900/60 p-4 overflow-x-auto text-sm font-mono text-slate-200">
{`# Linux / macOS
export STEWBEET_TELEMETRY=0
stewbeet build

# Windows PowerShell
$env:STEWBEET_TELEMETRY = "0"
stewbeet build`}
                        </pre>

                        <p className="mt-4 text-sm text-slate-400">{t('telemetry.disableNote')}</p>
                    </div>
                </div>

                {/* ── The code itself */}
                <div className="relative z-10 pb-20 px-4">
                    <div className="max-w-3xl mx-auto pt-6 border-t border-white/10">
                        <h2 className={`text-xl font-bold mb-2 ${HEADING}`}>{t('telemetry.sourceTitle')}</h2>
                        <p className="text-sm text-slate-400 mb-4">{t('telemetry.sourceIntro')}</p>

                        <a
                            href={IMPLEMENTATION_URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`inline-flex items-center gap-2 text-sm font-mono ${TEXT_ACCENT_HOVER} underline-offset-4 hover:underline break-all`}
                        >
                            python_package/stewbeet/telemetry.py
                            <HiExternalLink className="text-[0.875em] flex-shrink-0" aria-hidden="true" />
                        </a>

                        <p className="mt-4 text-sm text-slate-400">{t('telemetry.serverNote')}</p>

                        <div className="mt-10">
                            <Link
                                to="/"
                                className="group inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
                            >
                                <HiArrowLeft className="group-hover:-translate-x-1 transition-transform" aria-hidden="true" />
                                {t('telemetry.backHome')}
                            </Link>
                        </div>
                    </div>
                </div>
            </main>

            <Footer />
        </div>
    );
};
