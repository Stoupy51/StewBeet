import { useMemo, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { useTranslation } from '../i18n/useTranslation';

/** One day of a public series, exactly as /api/telemetry/streams returns it. */
export interface TelemetryDay {
    date: string;
    events: number;
    avgDurationSeconds: number;
}

export interface TelemetryBreakdown {
    label: string;
    count: number;
    percentage: number;
}

const PIE_COLORS = ['#f25c70', '#7fd35b', '#f2c14e', '#7dd3fc', '#d0795a', '#b4a7f5', '#c4bbb0', '#ff8a99', '#5eead4', '#5cb83a'];

/** Height of the plot. Bars are read against each other, so the number only sets the proportions. */
const PLOT_HEIGHT = 176;

/** A day with events never disappears into the baseline, and a day without one never pretends to have any. */
const MIN_BAR_PIXELS = 3;

/**
 * Thirty daily counts of one stream, as one bar per day.
 *
 * One series, so one colour and no legend: the heading names what the bars are. The only value
 * printed on the plot is the busiest day, because a number above all thirty bars is noise and the
 * hover readout already answers "how many on that one". Days with nothing keep their slot and
 * their tooltip, drawn as a flat tick, since a gap in the row would read as missing data instead
 * of as a quiet day.
 *
 * `unitLabel` and `averageLabel` come from the stream being drawn, so the same plot reads as builds,
 * runs or conversions without a second copy of it existing.
 *
 * The table under the plot is not a fallback, it is the same data in the form a screen reader,
 * a copy-paste or a colourblind reader can actually use, and it is why the bars themselves are
 * left out of the tab order rather than adding thirty stops between the heading and the link.
 */
export const TelemetryChart: React.FC<{ days: TelemetryDay[]; unitLabel: string; averageLabel: string }> = ({ days, unitLabel, averageLabel }) => {
    const { t, language } = useTranslation();
    const [hovered, setHovered] = useState<number | null>(null);

    const locale = language === 'fr' ? 'fr-FR' : 'en-US';
    const dayFormat = useMemo(() => new Intl.DateTimeFormat(locale, { month: 'short', day: 'numeric', timeZone: 'UTC' }), [locale]);
    const peak = Math.max(...days.map(day => day.events), 1);
    const peakIndex = days.findIndex(day => day.events === peak);

    const readout = hovered === null ? null : days[hovered];
    const tooltipAnchor = hovered === null ? 0 : ((hovered + 0.5) / days.length) * 100;
    // Near either end the tooltip would hang off the panel, so it stops centring and pins instead.
    const tooltipSide = hovered !== null && hovered < 3 ? 'start' : hovered !== null && hovered > days.length - 4 ? 'end' : 'center';

    return (
        <div>
            <div className="relative" style={{ height: PLOT_HEIGHT }}>
                {readout && (
                    <div
                        className="absolute -top-2 z-10 pointer-events-none rounded-panel border border-ink-800 bg-ink-950/95 px-3 py-2 shadow-black/50 whitespace-nowrap"
                        style={{
                            left: tooltipSide === 'end' ? undefined : `${tooltipAnchor}%`,
                            right: tooltipSide === 'end' ? 0 : undefined,
                            transform: tooltipSide === 'center' ? 'translateX(-50%)' : undefined,
                            marginLeft: tooltipSide === 'start' ? '-0.5rem' : undefined,
                        }}
                    >
                        <div className="text-xs font-mono text-ink-400">{dayFormat.format(new Date(`${readout.date}T00:00:00Z`))}</div>
                        <div className="text-sm text-ink-100">
                            {readout.events.toLocaleString(locale)} {unitLabel}
                        </div>
                        {readout.avgDurationSeconds > 0 && (
                            <div className="text-xs text-ink-400">
                                {averageLabel} {readout.avgDurationSeconds.toFixed(1)}s
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
                                    className="absolute inset-x-0 -translate-y-1 text-center text-[0.625rem] font-mono text-ink-400"
                                    style={{ bottom: `${(day.events / peak) * 100}%` }}
                                >
                                    {peak}
                                </span>
                            )}
                            <div
                                className={`w-full rounded-t-[4px] transition-colors ${
                                    day.events > 0
                                        ? hovered === index ? 'bg-beet-300' : 'bg-beet-600'
                                        : 'bg-ink-700'
                                }`}
                                style={{
                                    height: day.events > 0
                                        ? `max(${MIN_BAR_PIXELS}px, ${(day.events / peak) * 100}%)`
                                        : `${MIN_BAR_PIXELS - 1}px`,
                                }}
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Hairline baseline, one shade off the panel: it places the bars without competing with them. */}
            <div className="h-px w-full bg-ink-800" />

            <div className="mt-2 flex justify-between text-[0.6875rem] font-mono text-ink-500">
                <span>{dayFormat.format(new Date(`${days[0].date}T00:00:00Z`))}</span>
                <span>{dayFormat.format(new Date(`${days[days.length - 1].date}T00:00:00Z`))}</span>
            </div>

            <details className="mt-4 group">
                <summary className="cursor-pointer text-sm text-ink-400 hover:text-ink-200 transition-colors">
                    {t('telemetry.tableToggle')}
                </summary>
                <div className="mt-3 max-h-64 overflow-y-auto rounded-panel border border-ink-800">
                    <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-ink-900 text-left text-xs uppercase tracking-wide text-ink-400">
                            <tr>
                                <th scope="col" className="px-3 py-2 font-medium">{t('telemetry.tableDate')}</th>
                                <th scope="col" className="px-3 py-2 font-medium text-right">{unitLabel}</th>
                                <th scope="col" className="px-3 py-2 font-medium text-right">{t('telemetry.tableAverage')}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-ink-50/5">
                            {days.map(day => (
                                <tr key={day.date}>
                                    <td className="px-3 py-1.5 font-mono text-ink-300">{day.date}</td>
                                    <td className="px-3 py-1.5 text-right text-ink-200">{day.events.toLocaleString(locale)}</td>
                                    <td className="px-3 py-1.5 text-right text-ink-400">{day.avgDurationSeconds > 0 ? `${day.avgDurationSeconds.toFixed(1)}s` : '-'}</td>
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
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

    const chartData = useMemo(
        () => items.map((item, index) => ({
            name: item.label,
            value: item.count,
            percentage: item.percentage,
            fill: PIE_COLORS[index % PIE_COLORS.length],
        })),
        [items],
    );

    const displayedItems = items.slice(0, 6);

    return (
        <div className="rounded-panel border border-ink-800 bg-ink-900/40 p-4">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-300">{title}</h3>

            {items.length === 0 ? (
                <p className="text-sm text-ink-400">{emptyLabel}</p>
            ) : (
                <div className="grid gap-4 md:gap-3">
                    <div className="h-40 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Tooltip
                                    formatter={(value, name, item) => {
                                        const rawValue = Array.isArray(value) ? Number(value[0] ?? 0) : Number(value ?? 0);
                                        const maybePayload = typeof item === 'object' && item !== null && 'payload' in item
                                            ? (item as { payload?: { name?: string; value?: number; percentage?: number } }).payload
                                            : undefined;
                                        const label = maybePayload?.name ?? String(name ?? '');
                                        const count = typeof maybePayload?.value === 'number' ? maybePayload.value : rawValue;
                                        const percentage = typeof maybePayload?.percentage === 'number' ? maybePayload.percentage : 0;
                                        return [`${count.toLocaleString(locale)} (${percentage.toFixed(1)}%)`, label];
                                    }}
                                    contentStyle={{
                                        backgroundColor: 'rgb(var(--ink-900) / 0.97)',
                                        border: '1px solid rgb(var(--ink-700))',
                                        borderRadius: '12px',
                                        color: 'rgb(var(--ink-100))',
                                    }}
                                />
                                <Pie
                                    data={chartData}
                                    dataKey="value"
                                    nameKey="name"
                                    innerRadius={42}
                                    outerRadius={58}
                                    paddingAngle={2}
                                    cx="50%"
                                    cy="50%"
                                    isAnimationActive={true}
                                    onMouseEnter={(_, index) => setHoveredIndex(index)}
                                    onMouseLeave={() => setHoveredIndex(null)}
                                >
                                    {chartData.map((entry, index) => (
                                        <Cell
                                            key={`${title}-${entry.name}`}
                                            fill={entry.fill}
                                            className="stroke-ink-950"
                                            strokeWidth={2}
                                            opacity={hoveredIndex === null || hoveredIndex === index ? 1 : 0.45}
                                        />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="space-y-2 text-sm text-ink-300">
                        {displayedItems.map((item, index) => (
                            <button
                                key={`${title}-${item.label}`}
                                type="button"
                                className="flex w-full items-center justify-between gap-3 rounded-md border border-transparent px-2 py-1 text-left transition-colors hover:border-ink-800 hover:bg-ink-850"
                                onMouseEnter={() => setHoveredIndex(index)}
                                onMouseLeave={() => setHoveredIndex(null)}
                            >
                                <span className="flex min-w-0 items-center gap-2">
                                    <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} />
                                    <span className="truncate font-medium text-ink-200">{item.label}</span>
                                </span>
                                <span className="tabular-nums text-ink-400">
                                    {item.count.toLocaleString(locale)} <span className="text-ink-500">({item.percentage.toFixed(1)}%)</span>
                                </span>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

