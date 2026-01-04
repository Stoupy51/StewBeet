import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

export type Language = 'en' | 'fr';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

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
    // Get initial language from localStorage or default to 'en'
    const [language, setLanguageState] = useState<Language>(() => {
        try {
            const saved = localStorage.getItem('language');
            return (saved === 'en' || saved === 'fr') ? saved : 'en';
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

    const setLanguage = (lang: Language) => {
        setLanguageState(lang);
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage }}>
            {children}
        </LanguageContext.Provider>
    );
};
