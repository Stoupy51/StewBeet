import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

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

interface LanguageProviderProps {
    children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
    // Get initial language from localStorage or auto-detect for first visit
    const [language, setLanguageState] = useState<Language>(() => {
        try {
            const saved = localStorage.getItem('language');
            
            // If language is already saved, use it
            if (saved === 'en' || saved === 'fr') {
                return saved;
            }
            
            // First visit: auto-detect language based on browser locale
            // Check if the browser language is French
            const browserLang = navigator.language || (navigator as Navigator & { userLanguage?: string }).userLanguage;
            if (browserLang && browserLang.toLowerCase().startsWith('fr')) {
                return 'fr';
            }
            
            // Default to English for other locales
            return 'en';
        } catch {
            return 'en';
        }
    });

    // Save language to localStorage whenever it changes
    useEffect(() => {
        try {
            localStorage.setItem('language', language);
        } catch (error) {
            console.error('Failed to save language to localStorage:', error);
        }
    }, [language]);

    // The document was served as lang="en" and never updated, so a screen reader kept
    // reading French pages with an English voice and pronunciation rules.
    useEffect(() => {
        document.documentElement.lang = language;
    }, [language]);

    const setLanguage = (lang: Language) => {
        setLanguageState(lang);
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage }}>
            {children}
        </LanguageContext.Provider>
    );
};
