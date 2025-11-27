import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { translations } from '../translations/translations';

const LanguageContext = createContext();

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};

export const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState(() => {
        // Отримуємо збережену мову з localStorage або використовуємо українську за замовчуванням
        const savedLanguage = localStorage.getItem('language');
        return savedLanguage || 'uk';
    });

    // Зберігаємо мову в localStorage при зміні
    useEffect(() => {
        localStorage.setItem('language', language);
    }, [language]);

    // Функція для зміни мови
    const changeLanguage = useCallback((newLanguage) => {
        if (newLanguage === 'uk' || newLanguage === 'en') {
            // Примусово оновлюємо стан
            setLanguage(prevLanguage => {
                if (prevLanguage !== newLanguage) {
                    return newLanguage;
                }
                return prevLanguage;
            });
        }
    }, []);

    // Функція для отримання перекладу
    const t = (key, customTranslations = null) => {
        // Якщо передані кастомні переклади, використовуємо їх
        if (customTranslations) {
            if (language === 'en' && customTranslations.en) {
                return customTranslations.en;
            }
            return customTranslations.uk || key;
        }
        
        // Інакше використовуємо глобальний словник перекладів
        const translation = translations[key];
        
        if (!translation) return key;
        
        if (language === 'en' && translation.en) {
            return translation.en;
        }
        
        return translation.uk || key;
    };

    const value = {
        language,
        changeLanguage,
        t
    };

    return (
        <LanguageContext.Provider value={value}>
            {children}
        </LanguageContext.Provider>
    );
};
