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
        <ul aria-label={t('trust.label')} className={`gap-10 ${className}`}>
            {metrics.map(({ value, label }) => (
                <li key={label}>
                    <span className="block font-pixel text-[1.375rem] leading-none tabular-nums">{value}</span>
                    <span className="block mt-1.5 text-[0.8125rem] text-text-muted">{label}</span>
                </li>
            ))}
        </ul>
    );
};
