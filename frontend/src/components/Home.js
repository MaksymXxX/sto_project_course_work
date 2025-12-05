import React, { useState, useEffect, useMemo } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import api from '../utils/api';
import logo from '../assets/images/Flux_Dev_Simple_black_and_white_Minimalist_logo_for_a_car_serv_2.jpg';

const Home = () => {
  const { language, t } = useLanguage();
  const [stoInfo, setStoInfo] = useState(null);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Примусово очищаємо дані перед завантаженням нових
        setStoInfo(null);
        setServices([]);
        setLoading(true);
        
        const timestamp = new Date().getTime();
        
        const [stoInfoResponse, servicesResponse] = await Promise.all([
          api.get(`/api/sto-info/?language=${language}&t=${timestamp}`),
          api.get(`/api/services/featured/?language=${language}&t=${timestamp}`)
        ]);
        
        // Оновлюємо дані тільки після успішного отримання
        setStoInfo(stoInfoResponse.data);
        setServices(servicesResponse.data);
      } catch (error) {
        console.error('Помилка завантаження даних:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [language]); // Тільки залежність від мови

  // Кешуємо переклади для уникнення зайвих перерендерів
  const translatedContent = useMemo(() => {
    const content = {
      welcomeTitle: stoInfo?.name || t('welcome_title', translations.welcome_title),
      motto: stoInfo?.motto || t('motto', { uk: 'Надійність. Якість. Доступність.', en: 'Reliability. Quality. Accessibility.' }),
      welcomeText: stoInfo?.welcome_text || t('welcome_subtitle', translations.welcome_subtitle),
      whatYouCanTitle: stoInfo?.what_you_can_title || t('what_you_can_title', translations.what_you_can_title),
      whatYouCanItems: stoInfo?.what_you_can_items || [
        t('what_you_can_1', translations.what_you_can_1),
        t('what_you_can_2', translations.what_you_can_2),
        t('what_you_can_3', translations.what_you_can_3),
        t('what_you_can_4', translations.what_you_can_4),
        t('what_you_can_5', translations.what_you_can_5),
        t('what_you_can_6', translations.what_you_can_6)
      ],
      featuredServices: t('featured_services', translations.featured_services),
      phone: t('phone', translations.phone),
      address: t('address', translations.address),
      workingHours: t('working_hours', { uk: 'Графік роботи', en: 'Working Hours' }),
      addressValue: t('address_value', translations.address_value),
      workingHoursWeekdays: t('working_hours_weekdays', translations.working_hours_weekdays),
      workingHoursWeekend: t('working_hours_weekend', translations.working_hours_weekend)
    };
    return content;
  }, [stoInfo, t]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return <div className="text-center">{t('loading', translations.loading)}</div>;
  }

  return (
    <div className="home-container" key={`home-${language}`}>
      {/* Основний контент */}
      <div className="main-content">
        {/* Ліва секція */}
        <div className="left-section">
          <div className="main-logo">
            <img src={logo} alt="СТО AutoServis" className="main-logo-img" />
          </div>
          
          <div className="company-info">
            <h1 className="company-name">
              {translatedContent.welcomeTitle}
            </h1>
            <div className="company-motto">
              {translatedContent.motto}
            </div>
          </div>

          <div className="welcome-section">
            <p className="welcome-text">
              {translatedContent.welcomeText}
            </p>
          </div>

          <div className="services-intro">
            <h3>{translatedContent.whatYouCanTitle}</h3>
            <ul>
              {translatedContent.whatYouCanItems.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="main-services">
            <h3>{translatedContent.featuredServices}:</h3>
            <ul>
              {services.length > 0 ? (
                services.map((service, index) => (
                  <li key={service.id}>{service.name}</li>
                ))
              ) : (
                <>
                  <li>{t('what_you_can_1', translations.what_you_can_1)}</li>
                  <li>{t('what_you_can_4', translations.what_you_can_4)}</li>
                  <li>{t('what_you_can_3', translations.what_you_can_3)}</li>
                  <li>{t('what_you_can_2', translations.what_you_can_2)}</li>
                  <li>{t('what_you_can_6', translations.what_you_can_6)}</li>
                  <li>{t('what_you_can_5', translations.what_you_can_5)}</li>
                </>
              )}
            </ul>
          </div>
        </div>

        {/* Права секція */}
        <div className="right-section">
          <div className="image-placeholder">
            {/* Зображення СТО */}
          </div>
        </div>
      </div>

      {/* Футер */}
      <div className="footer">
        <div className="footer-content">
          <div className="footer-column">
            <h4>{t('phone', translations.phone)}:</h4>
            <p>{stoInfo?.phone || '044 123 45 67'}</p>
          </div>
          <div className="footer-column">
            <h4>Email:</h4>
            <p>{stoInfo?.email || 'info@autoservis.ua'}</p>
          </div>
          <div className="footer-column">
            <h4>{t('address', translations.address)}:</h4>
            <p>{stoInfo?.address || t('address_value', translations.address_value)}</p>
          </div>
          <div className="footer-column">
            <h4>{t('working_hours', { uk: 'Графік роботи', en: 'Working Hours' })}:</h4>
            <p>{stoInfo?.working_hours || t('working_hours_weekdays', translations.working_hours_weekdays)}</p>
            <p>{stoInfo?.working_hours_weekend || t('working_hours_weekend', translations.working_hours_weekend)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 