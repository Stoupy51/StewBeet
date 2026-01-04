import { useLanguage } from '../context/LanguageContext';
import { getTranslation } from './translations';

export function useTranslation() {
    const { language } = useLanguage();
    
    const t = (key: string): string => {
        return getTranslation(language, key);
    };
    
    return { t, language };
}
