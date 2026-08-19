import { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useReducedMotion } from 'framer-motion';
import { HiChevronLeft, HiChevronRight } from 'react-icons/hi';
import { TelemetryStreamPanel, type StreamSeries } from './TelemetryStreamPanel';
import { useTranslation } from '../i18n/useTranslation';
import { TELEMETRY_STREAMS } from '../api/telemetry/streams';
import { TOGGLE_ACTIVE } from '../theme';

/** How far a finger has to travel before it counts as a swipe rather than a tap that wandered. */
const SWIPE_THRESHOLD_PX = 60;

/**
 * The counters, one panel at a time, with the visible one named in the URL.
 *
 * `?stream=` is the single source of truth rather than a piece of state kept beside it: the arrows,
 * the tabs and a swipe all do the same one thing, the back button works, and a link to a particular
 * counter is something you can paste to somebody.
 *
 * Every panel stays mounted and the strip is moved under a window, so sliding costs no re-render
 * and no refetch. The ones out of view are marked `inert`, which keeps their tables and their pie
 * legends out of the tab order instead of adding three panels worth of stops between two arrows.
 */
export const TelemetrySlider: React.FC<{ streams: Record<string, StreamSeries> }> = ({ streams }) => {
    const { t } = useTranslation();
    const prefersReducedMotion = useReducedMotion();
    const [searchParams, setSearchParams] = useSearchParams();
    const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
    const touchStartX = useRef<number | null>(null);

    const requested = TELEMETRY_STREAMS.findIndex(stream => stream.id === searchParams.get('stream'));
    const index = requested === -1 ? 0 : requested;
    const last = TELEMETRY_STREAMS.length - 1;

    const go = (next: number, focusTab = false): void => {
        const clamped = Math.min(Math.max(next, 0), last);
        if (clamped !== index) {
            const params = new URLSearchParams(searchParams);
            // The first panel is the default, so it stays a bare /telemetry rather than a URL that
            // says the same thing with a parameter on the end.
            if (clamped === 0) params.delete('stream');
            else params.set('stream', TELEMETRY_STREAMS[clamped].id);
            setSearchParams(params, { replace: true });
        }
        if (focusTab) tabRefs.current[clamped]?.focus();
    };

    // A tab far enough along the row to be off a phone screen is worth nothing if selecting it
    // leaves it out of sight, and this is the one thing the URL cannot express on its own.
    useEffect(() => {
        tabRefs.current[index]?.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: prefersReducedMotion ? 'auto' : 'smooth' });
    }, [index, prefersReducedMotion]);

    return (
        <section className="max-w-3xl mx-auto">
            <div className="flex items-center gap-2">
                <button
                    type="button"
                    onClick={() => go(index - 1)}
                    disabled={index === 0}
                    aria-label={t('telemetry.previousStream')}
                    className="flex-shrink-0 rounded-lg border border-white/10 p-2 text-slate-300 transition-colors hover:border-white/25 hover:text-white disabled:opacity-30 disabled:hover:border-white/10 disabled:hover:text-slate-300"
                >
                    <HiChevronLeft className="h-5 w-5" aria-hidden="true" />
                </button>

                <div
                    role="tablist"
                    aria-label={t('telemetry.streamTabs')}
                    className="flex min-w-0 flex-1 gap-2 overflow-x-auto custom-scrollbar py-1"
                    onKeyDown={event => {
                        if (event.key === 'ArrowRight') go(index + 1, true);
                        else if (event.key === 'ArrowLeft') go(index - 1, true);
                        else if (event.key === 'Home') go(0, true);
                        else if (event.key === 'End') go(last, true);
                        else return;
                        event.preventDefault();
                    }}
                >
                    {TELEMETRY_STREAMS.map((stream, position) => (
                        <button
                            key={stream.id}
                            ref={element => { tabRefs.current[position] = element; }}
                            type="button"
                            role="tab"
                            id={`telemetry-tab-${stream.id}`}
                            aria-selected={position === index}
                            aria-controls={`telemetry-panel-${stream.id}`}
                            tabIndex={position === index ? 0 : -1}
                            onClick={() => go(position)}
                            className={`flex-shrink-0 rounded-lg border px-3 py-1.5 text-sm transition-colors ${
                                position === index ? TOGGLE_ACTIVE : 'border-white/10 text-slate-400 hover:border-white/25 hover:text-slate-200'
                            }`}
                        >
                            {t(`telemetry.streams.${stream.id}.tab`)}
                        </button>
                    ))}
                </div>

                <button
                    type="button"
                    onClick={() => go(index + 1)}
                    disabled={index === last}
                    aria-label={t('telemetry.nextStream')}
                    className="flex-shrink-0 rounded-lg border border-white/10 p-2 text-slate-300 transition-colors hover:border-white/25 hover:text-white disabled:opacity-30 disabled:hover:border-white/10 disabled:hover:text-slate-300"
                >
                    <HiChevronRight className="h-5 w-5" aria-hidden="true" />
                </button>
            </div>

            <div
                className="mt-3 overflow-hidden rounded-panel border border-white/10 bg-slate-900/40"
                onTouchStart={event => { touchStartX.current = event.touches[0].clientX; }}
                onTouchEnd={event => {
                    if (touchStartX.current === null) return;
                    const travelled = event.changedTouches[0].clientX - touchStartX.current;
                    touchStartX.current = null;
                    if (Math.abs(travelled) >= SWIPE_THRESHOLD_PX) go(index + (travelled < 0 ? 1 : -1));
                }}
            >
                <div
                    className={`flex items-start ${prefersReducedMotion ? '' : 'transition-transform duration-300 ease-out'}`}
                    style={{ transform: `translateX(-${index * 100}%)` }}
                >
                    {TELEMETRY_STREAMS.map((stream, position) => (
                        <div
                            key={stream.id}
                            role="tabpanel"
                            id={`telemetry-panel-${stream.id}`}
                            aria-labelledby={`telemetry-tab-${stream.id}`}
                            inert={position !== index}
                            className="w-full flex-shrink-0 p-6 md:p-8"
                        >
                            <TelemetryStreamPanel
                                stream={stream}
                                series={streams[stream.id] ?? { stream: stream.id, days: [], total: 0, avgDurationSeconds: 0, breakdowns: {} }}
                            />
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
