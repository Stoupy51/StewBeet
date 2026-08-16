import { useMemo, useState } from 'react';
import { useTranslation } from '../i18n/useTranslation';

/** One day of the public series, exactly as /api/telemetry/builds returns it. */
export interface TelemetryDay {
    date: string;
    builds: number;
    avgDurationSeconds: number;
}

export interface TelemetryBreakdown {
    label: string;
    count: number;
    percentage: number;
}

const PIE_COLORS = ['#38bdf8', '#34d399', '#a78bfa', '#fbbf24', '#f87171', '#fb7185', '#22d3ee', '#f472b6', '#4ade80', '#c084fc'];

/** Height of the plot. Bars are read against each other, so the number only sets the proportions. */
const PLOT_HEIGHT = 176;

/** A day with builds never disappears into the baseline, and a day without one never pretends to have any. */
const MIN_BAR_PIXELS = 3;

/**
 * Thirty daily build counts, as one bar per day.
 *
 * One series, so one colour and no legend: the heading names what the bars are. The only value
 * printed on the plot is the busiest day, because a number above all thirty bars is noise and the
 * hover readout already answers "how many on that one". Days with no builds keep their slot and
 * their tooltip, drawn as a flat tick, since a gap in the row would read as missing data instead
 * of as a quiet day.
 *
 * The table under the plot is not a fallback, it is the same data in the form a screen reader,
 * a copy-paste or a colourblind reader can actually use, and it is why the bars themselves are
 * left out of the tab order rather than adding thirty stops between the heading and the link.
 */
export const TelemetryChart: React.FC<{ days: TelemetryDay[] }> = ({ days }) => {
    const { t, language } = useTranslation();
    const [hovered, setHovered] = useState<number | null>(null);

    const locale = language === 'fr' ? 'fr-FR' : 'en-US';
    const dayFormat = useMemo(() => new Intl.DateTimeFormat(locale, { month: 'short', day: 'numeric', timeZone: 'UTC' }), [locale]);
    const peak = Math.max(...days.map(day => day.builds), 1);
    const peakIndex = days.findIndex(day => day.builds === peak);

    const readout = hovered === null ? null : days[hovered];
    const tooltipAnchor = hovered === null ? 0 : ((hovered + 0.5) / days.length) * 100;
    // Near either end the tooltip would hang off the panel, so it stops centring and pins instead.
    const tooltipSide = hovered !== null && hovered < 3 ? 'start' : hovered !== null && hovered > days.length - 4 ? 'end' : 'center';

    return (
        <div>
            <div className="relative" style={{ height: PLOT_HEIGHT }}>
                {readout && (
                    <div
                        className="absolute -top-2 z-10 pointer-events-none rounded-panel border border-white/15 bg-slate-950/95 px-3 py-2 shadow-lg shadow-black/50 whitespace-nowrap"
                        style={{
                            left: tooltipSide === 'end' ? undefined : `${tooltipAnchor}%`,
                            right: tooltipSide === 'end' ? 0 : undefined,
                            transform: tooltipSide === 'center' ? 'translateX(-50%)' : undefined,
                            marginLeft: tooltipSide === 'start' ? '-0.5rem' : undefined,
                        }}
                    >
                        <div className="text-xs font-mono text-slate-400">{dayFormat.format(new Date(`${readout.date}T00:00:00Z`))}</div>
                        <div className="text-sm text-slate-100">
                            {readout.builds.toLocaleString(locale)} {t('telemetry.buildsLabel')}
                        </div>
                        {readout.builds > 0 && (
                            <div className="text-xs text-slate-400">
                                {t('telemetry.averageBuild')} {readout.avgDurationSeconds.toFixed(1)}s
                            </div>
                        )}
                    </div>
                )}

                <div
                    className="flex h-full items-end gap-[2px]"
                    role="img"
                    aria-label={t('telemetry.chartAlt')}
                    onMouseLeave={() => setHovered(null)}
                >
                    {days.map((day, index) => (
                        <div
                            key={day.date}
                            className="relative flex h-full flex-1 cursor-default items-end"
                            onMouseEnter={() => setHovered(index)}
                        >
                            {index === peakIndex && peak > 0 && (
                                <span
                                    className="absolute inset-x-0 -translate-y-1 text-center text-[0.625rem] font-mono text-slate-400"
                                    style={{ bottom: `${(day.builds / peak) * 100}%` }}
                                >
                                    {peak}
                                </span>
                            )}
                            <div
                                className={`w-full rounded-t-[4px] transition-colors ${
                                    day.builds > 0
                                        ? hovered === index ? 'bg-mc-diamond' : 'bg-mc-emerald'
                                        : 'bg-slate-700'
                                }`}
                                style={{
                                    height: day.builds > 0
                                        ? `max(${MIN_BAR_PIXELS}px, ${(day.builds / peak) * 100}%)`
                                        : `${MIN_BAR_PIXELS - 1}px`,
                                }}
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Hairline baseline, one shade off the panel: it places the bars without competing with them. */}
            <div className="h-px w-full bg-white/10" />

            <div className="mt-2 flex justify-between text-[0.6875rem] font-mono text-slate-500">
                <span>{dayFormat.format(new Date(`${days[0].date}T00:00:00Z`))}</span>
                <span>{dayFormat.format(new Date(`${days[days.length - 1].date}T00:00:00Z`))}</span>
            </div>

            <details className="mt-4 group">
                <summary className="cursor-pointer text-sm text-slate-400 hover:text-slate-200 transition-colors">
                    {t('telemetry.tableToggle')}
                </summary>
                <div className="mt-3 max-h-64 overflow-y-auto rounded-panel border border-white/10">
                    <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-slate-900 text-left text-xs uppercase tracking-wide text-slate-400">
                            <tr>
                                <th scope="col" className="px-3 py-2 font-medium">{t('telemetry.tableDate')}</th>
                                <th scope="col" className="px-3 py-2 font-medium text-right">{t('telemetry.tableBuilds')}</th>
                                <th scope="col" className="px-3 py-2 font-medium text-right">{t('telemetry.tableAverage')}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {days.map(day => (
                                <tr key={day.date}>
                                    <td className="px-3 py-1.5 font-mono text-slate-300">{day.date}</td>
                                    <td className="px-3 py-1.5 text-right text-slate-200">{day.builds.toLocaleString(locale)}</td>
                                    <td className="px-3 py-1.5 text-right text-slate-400">{day.builds > 0 ? `${day.avgDurationSeconds.toFixed(1)}s` : '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </details>
        </div>
    );
};

export const TelemetryBreakdownChart: React.FC<{ title: string; items: TelemetryBreakdown[]; emptyLabel: string }> = ({ title, items, emptyLabel }) => {
    const { language } = useTranslation();
    const locale = language === 'fr' ? 'fr-FR' : 'en-US';

    const pieBackground = useMemo(() => {
        if (items.length === 0) return 'linear-gradient(#1e293b, #1e293b)';
        let start = 0;
        const segments = items.map((item, index) => {
            const end = start + item.percentage;
            const color = PIE_COLORS[index % PIE_COLORS.length];
            const segment = `${color} ${start}% ${end}%`;
            start = end;
            return segment;
        });
        return `conic-gradient(${segments.join(', ')})`;
    }, [items]);

    const displayedItems = items.slice(0, 6);

    return (
        <div className="rounded-panel border border-white/10 bg-slate-900/40 p-4">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-300">{title}</h3>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                <div className="relative mx-auto h-24 w-24 shrink-0 rounded-full border border-white/10 shadow-lg shadow-black/30" style={{ background: pieBackground }}>
                    <div className="absolute inset-[22%] rounded-full border border-white/10 bg-slate-950" />
                </div>

                <div className="min-w-0 flex-1">
                    {items.length > 0 ? (
                        <ul className="space-y-2 text-sm text-slate-300">
                            {displayedItems.map((item, index) => (
                                <li key={`${title}-${item.label}`} className="flex items-center justify-between gap-3">
                                    <span className="flex min-w-0 items-center gap-2">
                                        <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} />
                                        <span className="truncate">{item.label}</span>
                                    </span>
                                    <span className="tabular-nums text-slate-400">
                                        {item.count.toLocaleString(locale)} ({item.percentage.toFixed(1)}%)
                                    </span>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-sm text-slate-400">{emptyLabel}</p>
                    )}
                </div>
            </div>
        </div>
    );
};

