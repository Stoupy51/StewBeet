import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';

/** A documentation page server.tsx already read, so the client starts from it instead of fetching it again. */
export interface PrerenderedDoc {
    src: string;
    content: string;
    /** Its code highlighted at build time, by `codeKey`. */
    highlighted: Record<string, string>;
}

const MarkdownContentContext = createContext<PrerenderedDoc | null>(null);

// eslint-disable-next-line react-refresh/only-export-components
export const useMarkdownContent = () => useContext(MarkdownContentContext);

export const MarkdownContentProvider: React.FC<{ doc: PrerenderedDoc | null; children: ReactNode }> = ({ doc, children }) => (
    <MarkdownContentContext.Provider value={doc}>
        {children}
    </MarkdownContentContext.Provider>
);
