import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import './LanguageSwitcher.css';

const LanguageSwitcher = () => {
    const { language, changeLanguage } = useLanguage();

    const handleLanguageChange = (newLanguage) => {
        changeLanguage(newLanguage);
    };

    return (
        <div className="language-switcher">
            <button
                className={`lang-btn ${language === 'uk' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('uk')}
                title="Українська"
            >
                🇺🇦
            </button>
            <button
                className={`lang-btn ${language === 'en' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('en')}
                title="English"
            >
                🇺🇸
            </button>
        </div>
    );
};

export default LanguageSwitcher;
