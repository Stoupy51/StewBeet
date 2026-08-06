import { HiOutlineClock, HiOutlineCube, HiOutlineDownload, HiOutlineStar } from 'react-icons/hi';
import { useTranslation } from '../i18n/useTranslation';
import { TEXT_ACCENT } from '../theme';
import stats from '../generated/stats.json';
import { TOTAL_BUILT_WITH } from './builtWithData';

/**
 * The numbers that answer "is this alive and does anyone use it?": the question a visitor
 * asks immediately after understanding what the tool does.
 *
 * They were previously three shields.io images in the footer, which meant a visitor had to
 * scroll the entire page to find any evidence of adoption, and the badges arrived without
 * intrinsic dimensions and shifted the layout as they loaded. The values now come from
 * src/generated/stats.json, written at build time by scripts/build-stats.ts.
 *
 * A metric that failed to fetch is null and is dropped rather than shown stale.
 */

interface Metric {
    icon: React.ComponentType<{ className?: string }>;
    value: string;
    label: string;
}

/** Whole thousands read as rounder and more honest than a precise figure that ages badly. */
function formatCount(count: number): string {
    return count >= 1000 ? `${(count / 1000).toFixed(1)}k` : String(count);
}

function formatAge(iso: string, template: string): string {
    const days = Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000);
    if (days <= 0) return template.replace('{n}', '0');
    return template.replace('{n}', String(days));
}

export const TrustStrip: React.FC = () => {
    const { t } = useTranslation();

    const metrics: Metric[] = [];

    if (stats.version) {
        metrics.push({
            icon: HiOutlineClock,
            value: `v${stats.version}`,
            label: stats.releasedAt ? formatAge(stats.releasedAt, t('trust.releasedDaysAgo')) : t('trust.latestRelease'),
        });
    }
    if (stats.downloadsPerMonth) {
        metrics.push({
            icon: HiOutlineDownload,
            value: formatCount(stats.downloadsPerMonth),
            label: t('trust.downloadsPerMonth'),
        });
    }
    metrics.push({
        icon: HiOutlineCube,
        value: String(TOTAL_BUILT_WITH),
        label: t('trust.publicProjects'),
    });
    if (stats.stars) {
        metrics.push({
            icon: HiOutlineStar,
            value: String(stats.stars),
            label: t('trust.githubStars'),
        });
    }

    return (
        <section aria-label={t('trust.label')} className="border-y border-white/10 bg-slate-950">
            <div className="max-w-5xl mx-auto px-4 py-6 grid grid-cols-2 md:grid-cols-4 gap-y-6 gap-x-4">
                {metrics.map(({ icon: Icon, value, label }) => (
                    <div key={label} className="flex items-center gap-3 justify-center">
                        <Icon className={`text-xl flex-shrink-0 ${TEXT_ACCENT}`} />
                        <div className="min-w-0">
                            <p className="text-lg font-semibold text-slate-50 leading-tight font-mono">{value}</p>
                            <p className="text-xs text-slate-400 leading-tight">{label}</p>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
};
