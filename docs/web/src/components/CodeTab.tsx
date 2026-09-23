/**
 * A code or file panel headed by a flat file tab: the path, an optional language label and an
 * accessory slot on the right (a file count, a copy button). `h-full` lets two panels in one grid
 * row end on the same line.
 */
export const CodeTab = ({ path, lang, accessory, className = '', children }: {
    path: string;
    lang?: string;
    accessory?: React.ReactNode;
    className?: string;
    children: React.ReactNode;
}) => (
    <div className={`h-full flex flex-col min-h-0 rounded-panel border border-ink-800 bg-ink-900 overflow-hidden ${className}`}>
        <div className="flex items-center gap-3 h-10 px-4 border-b border-ink-800 bg-ink-950/40 flex-shrink-0">
            <span className="font-mono text-xs text-ink-200 truncate">{path}</span>
            {lang && (
                <span className="font-mono text-[0.6875rem] uppercase tracking-wider text-ink-400 flex-shrink-0">{lang}</span>
            )}
            {accessory && <div className="ml-auto flex-shrink-0">{accessory}</div>}
        </div>
        {children}
    </div>
);
