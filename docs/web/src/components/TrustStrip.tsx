import { useTranslation } from '../i18n/useTranslation';
import stats from '../generated/stats.json';
import { TOTAL_BUILT_WITH } from './builtWithData';

/**
 * The numbers that answer "does anyone use this?", inside the hero so they sit above the fold with
 * the proof they back up. Values come from src/generated/stats.json, written at build time by
 * scripts/build-stats.ts; a metric that failed to fetch is null and is dropped rather than shown
 * stale. The release age sits in the hero eyebrow, so it is not repeated here.
 */

interface Metric {
    value: string;
    label: string;
}

/** Whole thousands read as rounder and more honest than a precise figure that ages badly. */
function formatCount(count: number): string {
    return count >= 1000 ? `${(count / 1000).toFixed(1)}k` : String(count);
}

export const TrustStrip = ({ className = '' }: { className?: string }) => {
    const { t } = useTranslation();

    const metrics: Metric[] = [
        ...(stats.downloadsPerMonth ? [{ value: formatCount(stats.downloadsPerMonth), label: t('trust.downloadsPerMonth') }] : []),
        { value: String(TOTAL_BUILT_WITH), label: t('trust.publicProjects') },
        ...(stats.stars ? [{ value: String(stats.stars), label: t('trust.githubStars') }] : []),
    ];

    return (
        // Stacked columns on phones, where three inline pairs would wrap unevenly.
        <ul aria-label={t('trust.label')} className={`grid grid-cols-3 gap-3 sm:flex sm:flex-wrap sm:items-baseline sm:justify-center sm:gap-x-8 sm:gap-y-2 ${className}`}>
            {metrics.map(({ value, label }) => (
                <li key={label} className="flex flex-col items-center gap-0.5 sm:flex-row sm:items-baseline sm:gap-2">
                    <span className="font-mono text-lg text-ink-50 tabular-nums">{value}</span>
                    <span className="text-xs sm:text-sm text-ink-400 leading-snug">{label}</span>
                </li>
            ))}
        </ul>
    );
};
