import type { Entry } from './builtWithData';

/**
 * A row of library names with their maintainer. Neutral rather than beet: these are other
 * people's projects, and the brand colour means "this is StewBeet". Shared by the home page
 * section and the credits page.
 */
export const LibraryPills = ({ entries }: { entries: Entry[] }) => (
    <div className="flex flex-wrap gap-2">
        {entries.map((entry) => (
            <a
                key={entry.url}
                href={entry.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-baseline gap-2 px-3 py-1.5 rounded-control border border-ink-800 bg-ink-900 text-sm text-ink-100 hover:border-ink-600 transition-colors"
            >
                <span className="font-medium">{entry.name}</span>
                <span className="font-mono text-[0.6875rem] text-mc-copper">{entry.owner}</span>
            </a>
        ))}
    </div>
);
