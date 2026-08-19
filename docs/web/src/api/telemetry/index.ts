/**
 * The public surface of the telemetry feature.
 *
 * Split three ways because the parts change for different reasons: streams.ts is the list of what
 * is counted, storage.ts is how a count is kept, handlers.ts is what HTTP does with it. Adding a
 * counter touches only the first.
 */
export {
    bucketOf,
    DEFAULT_STREAM_ID,
    DURATION_DIMENSION,
    durationBucket,
    findStream,
    inputSizeBucket,
    packSizeBucket,
    TELEMETRY_STREAMS,
    type StreamId,
    type StreamSource,
    type TelemetryStream,
} from './streams';

export {
    allStreams,
    dayKey,
    recordEvent,
    RETENTION_DAYS,
    streamSeries,
    windowDays,
    type EventDetails,
    type PublicBreakdown,
    type PublicDay,
    type PublicStream,
} from './storage';

export {
    countBuild,
    handleTelemetryBuild,
    handleTelemetryBuilds,
    handleTelemetryEvent,
    handleTelemetryStreams,
    publicSeries,
    resetTelemetryState,
} from './handlers';
