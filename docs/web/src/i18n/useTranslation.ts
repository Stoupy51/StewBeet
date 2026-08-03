import { useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { getTranslation } from './translations';

export function useTranslation() {
    const { language } = useLanguage();

    // Stable across renders so effects can depend on `t` without re-running every render
    const t = useCallback((key: string): string => getTranslation(language, key), [language]);

    return { t, language };
}
