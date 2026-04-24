import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';

/**
 * Holds markdown content pre-fetched by the SSR server (server.tsx).
 * null  = client-side render; component should fetch normally.
 * string = SSR path; component uses this as initial content, skips client fetch.
 */
const MarkdownContentContext = createContext<string | null>(null);

// eslint-disable-next-line react-refresh/only-export-components
export const useMarkdownContent = () => useContext(MarkdownContentContext);

export const MarkdownContentProvider: React.FC<{ content: string; children: ReactNode }> = ({ content, children }) => (
    <MarkdownContentContext.Provider value={content}>
        {children}
    </MarkdownContentContext.Provider>
);
