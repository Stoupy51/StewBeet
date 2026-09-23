import { useTranslation } from '../i18n/useTranslation';
import stats from '../generated/stats.json';
import { TOTAL_BUILT_WITH } from './builtWithData';
import { PAGE } from '../theme';

/**
 * The numbers that answer "does anyone use this?", right under the proof they back up.
 * Values come from src/generated/stats.json, written at build time by scripts/build-stats.ts; a
 * metric that failed to fetch is null and is dropped rather than shown stale. The release age sits
 * in the hero eyebrow, so it is not repeated here.
 */

interface Metric {
    value: string;
    label: string;
}

/** Whole thousands read as rounder and more honest than a precise figure that ages badly. */
function formatCount(count: number): string {
    return count >= 1000 ? `${(count / 1000).toFixed(1)}k` : String(count);
}

export const TrustStrip: React.FC = () => {
    const { t } = useTranslation();

    const metrics: Metric[] = [
        ...(stats.downloadsPerMonth ? [{ value: formatCount(stats.downloadsPerMonth), label: t('trust.downloadsPerMonth') }] : []),
        { value: String(TOTAL_BUILT_WITH), label: t('trust.publicProjects') },
        ...(stats.stars ? [{ value: String(stats.stars), label: t('trust.githubStars') }] : []),
    ];

    return (
        <section aria-label={t('trust.label')} className="border-t border-ink-800 bg-ink-900/50">
            <div className={`${PAGE} py-6 grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-0 sm:divide-x sm:divide-ink-800`}>
                {metrics.map(({ value, label }) => (
                    <div key={label} className="flex items-baseline justify-center gap-3">
                        <span className="font-mono text-2xl text-ink-50 tabular-nums">{value}</span>
                        <span className="text-sm text-ink-400">{label}</span>
                    </div>
                ))}
            </div>
        </section>
    );
};
