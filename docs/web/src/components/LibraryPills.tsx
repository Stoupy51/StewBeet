import type { Entry } from './builtWithData';

/**
 * A row of library names with their maintainer.
 *
 * Copper rather than emerald: these are other people's projects, and the brand colour on the
 * home page means "this is StewBeet". Shared by the home page section and the credits page.
 */

const LIBRARY_PILL =
    'bg-mc-copper/10 border-mc-copper/30 text-slate-100 hover:bg-mc-copper/20 hover:border-mc-copper/60';

export const LibraryPills = ({ entries }: { entries: Entry[] }) => (
    <div className="flex flex-wrap gap-2">
        {entries.map((entry) => (
            <a
                key={entry.url}
                href={entry.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`inline-flex items-baseline gap-2 px-3 py-1.5 rounded-panel border text-sm transition-colors ${LIBRARY_PILL}`}
            >
                <span className="font-medium">{entry.name}</span>
                <span className="text-[0.6875rem] font-mono text-mc-copper/90">{entry.owner}</span>
            </a>
        ))}
    </div>
);
