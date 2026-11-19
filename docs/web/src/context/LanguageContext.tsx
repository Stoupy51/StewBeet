import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import { pageAt } from '../docsPages';

export type Language = 'en' | 'fr';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// eslint-disable-next-line react-refresh/only-export-components
export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};

/** The language the reader picked with the EN/FR button, if they ever did. */
// eslint-disable-next-line react-refresh/only-export-components
export function savedLanguage(): Language | null {
    try {
        const saved = localStorage.getItem('language');
        return saved === 'en' || saved === 'fr' ? saved : null;
    } catch {
        // Storage disabled, or the server rendering the page
        return null;
    }
}

function browserLanguage(): Language {
    return typeof navigator !== 'undefined' && navigator.language?.toLowerCase().startsWith('fr') ? 'fr' : 'en';
}

interface LanguageProviderProps {
    children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
    const { pathname } = useLocation();
    // A doc page starts in the language of its address, which the server rendered it in, so it hydrates unchanged
    const [language, setLanguageState] = useState<Language>(() => pageAt(pathname)?.language ?? savedLanguage() ?? browserLanguage());

    // The document was served as lang="en" and never updated, so a screen reader kept
    // reading French pages with an English voice and pronunciation rules.
    useEffect(() => {
        document.documentElement.lang = language;
    }, [language]);

    /** Saved only when the reader picks it, so the language of an address they opened is never taken for their choice. */
    const setLanguage = (lang: Language) => {
        setLanguageState(lang);
        try {
            localStorage.setItem('language', lang);
        } catch {
            // Storage disabled: the choice lasts for this visit
        }
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage }}>
            {children}
        </LanguageContext.Provider>
    );
};
