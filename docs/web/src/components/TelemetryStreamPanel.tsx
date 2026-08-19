import { Link } from 'react-router-dom';
import { HiArrowRight } from 'react-icons/hi';
import { TelemetryBreakdownChart, TelemetryChart, type TelemetryBreakdown, type TelemetryDay } from './TelemetryChart';
import { useTranslation } from '../i18n/useTranslation';
import { TEXT_ACCENT, TEXT_ACCENT_HOVER } from '../theme';
import type { TelemetryStream } from '../api/telemetry/streams';

/** One stream of `GET /api/telemetry/streams?days=30`. */
export interface StreamSeries {
    stream: string;
    days: TelemetryDay[];
    total: number;
    avgDurationSeconds: number;
    breakdowns: Record<string, TelemetryBreakdown[]>;
}

/**
 * One counter, drawn from its registry entry and its series and from nothing else.
 *
 * Every string it needs is looked up by convention: `telemetry.streams.<id>.*` for the panel and
 * `telemetry.dimensions.<name>` for each breakdown. A new counter is therefore a registry entry and
 * a block of translations, with no case to add here and no component to write.
 */
export const TelemetryStreamPanel: React.FC<{ stream: TelemetryStream; series: StreamSeries }> = ({ stream, series }) => {
    const { t, language } = useTranslation();
    const locale = language === 'fr' ? 'fr-FR' : 'en-US';

    const label = (field: string): string => t(`telemetry.streams.${stream.id}.${field}`);
    const unit = label('unit');
    const average = label('average');

    return (
        <div>
            <h2 className="text-sm font-medium uppercase tracking-wide text-slate-400">{label('title')}</h2>

            <p className={`mt-3 mb-1 text-4xl md:text-5xl font-bold tabular-nums ${TEXT_ACCENT}`}>
                {series.total.toLocaleString(locale)}
            </p>
            <p className="mb-8 text-sm text-slate-400">
                {unit}
                {series.avgDurationSeconds > 0 && ` · ${average} ${series.avgDurationSeconds.toFixed(1)}s`}
            </p>

            {series.days.length > 0 && <TelemetryChart days={series.days} unitLabel={unit} averageLabel={average} />}

            {/* Two dimensions or three, laid out so a pie is never squeezed into a third of a phone. */}
            <div className={`mt-8 grid gap-4 ${stream.dimensions.length >= 3 ? 'md:grid-cols-3' : 'md:grid-cols-2'}`}>
                {stream.dimensions.map(dimension => (
                    <TelemetryBreakdownChart
                        key={dimension}
                        title={t(`telemetry.dimensions.${dimension}`)}
                        items={series.breakdowns[dimension] ?? []}
                        emptyLabel={t('telemetry.noDimensionData')}
                    />
                ))}
            </div>

            <p className="mt-6 text-sm text-slate-400 leading-relaxed">{label('note')}</p>

            {stream.href && (
                <Link to={stream.href} className={`group mt-3 inline-flex items-center gap-2 text-sm ${TEXT_ACCENT_HOVER} hover:underline underline-offset-4`}>
                    {label('link')}
                    <HiArrowRight className="group-hover:translate-x-1 transition-transform" aria-hidden="true" />
                </Link>
            )}
        </div>
    );
};
