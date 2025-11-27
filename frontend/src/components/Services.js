import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import api from '../utils/api';
import Modal from './Modal';

const Services = () => {
  const { language, t } = useLanguage();
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);
  const [modalType, setModalType] = useState(''); // 'category' або 'service'

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Примусово очищаємо дані перед завантаженням нових
        setCategories([]);
        setServices([]);
        setLoading(true);
        
        const timestamp = new Date().getTime();
        const [categoriesResponse, servicesResponse] = await Promise.all([
          api.get(`/api/service-categories/?language=${language}&t=${timestamp}`),
          api.get(`/api/services/?language=${language}&t=${timestamp}`)
        ]);
        
        const categoriesData = categoriesResponse.data.results || categoriesResponse.data || [];
        const servicesData = servicesResponse.data || [];
        
        // Оновлюємо дані тільки після успішного отримання
        setCategories(categoriesData);
        setServices(servicesData);
      } catch (error) {
        console.error('Помилка завантаження даних:', error);
        setCategories([]);
        setServices([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [language]); // Тільки залежність від мови

  // Групуємо послуги за категоріями
  const servicesByCategory = Array.isArray(categories) ? categories.reduce((acc, category) => {
    const categoryServices = services.filter(service => service.category?.id === category.id);
    if (categoryServices.length > 0) {
      acc[category.name] = {
        category: category,
        services: categoryServices
      };
    }
    return acc;
  }, {}) : {};



  const handleCategoryClick = (categoryName) => {
    const categoryData = servicesByCategory[categoryName];
    if (categoryData) {
      setModalData(categoryData);
      setModalType('category');
      setModalOpen(true);
    }
  };

  const handleServiceClick = (service) => {
    setModalData(service);
    setModalType('service');
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalData(null);
    setModalType('');
  };

  if (loading) {
    return <div className="text-center">{t('loading', translations.loading)}</div>;
  }

  // Якщо немає даних, показуємо повідомлення
  if (Object.keys(servicesByCategory).length === 0) {
    return (
      <div className="services-page">
        <div className="services-header">
          <div className="services-title-section">
            <h1 className="services-main-title">{t('all_services', translations.all_services).toUpperCase()}</h1>
          </div>
        </div>

        <div className="services-content">
          <div className="text-center">
            <p>{t('no_services', { uk: 'Наразі немає доступних послуг', en: 'No services available at the moment' })}</p>
          </div>
        </div>
      </div>
    );
  }

  // Розподіляємо категорії по колонках
  const categoryEntries = Object.entries(servicesByCategory);
  const midPoint = Math.ceil(categoryEntries.length / 2);
  const leftColumn = categoryEntries.slice(0, midPoint);
  const rightColumn = categoryEntries.slice(midPoint);


  return (
    <div className="services-page" key={`services-${language}`}>
      {/* Header з навігацією */}
      <div className="services-header">
        <div className="services-title-section">
          <h1 className="services-main-title">{t('all_services', translations.all_services).toUpperCase()}</h1>
        </div>
      </div>

      {/* Основний контент з категоріями */}
      <div className="services-content">
        <div className="services-grid">
          {/* Ліва колонка */}
          <div className="services-column">
            {leftColumn.map(([categoryName, categoryData]) => (
              <div key={categoryName} className="service-category">
                <h2 
                  className="category-title clickable"
                  onClick={() => handleCategoryClick(categoryName)}
                >
                  {categoryName}
                </h2>
                <div className="service-list">
                  {categoryData.services.map((service, index) => (
                    <div 
                      key={index} 
                      className="service-item clickable"
                      onClick={() => handleServiceClick(service)}
                    >
                      <span className="service-name">{service.name}</span>
                      <span className="service-price">{t('from', { uk: 'від', en: 'from' })} {service.price} {t('currency', translations.currency)}</span>
                      <span className="service-duration">{service.duration_minutes} {t('minutes', translations.minutes)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Права колонка */}
          <div className="services-column">
            {rightColumn.map(([categoryName, categoryData]) => (
              <div key={categoryName} className="service-category">
                <h2 
                  className="category-title clickable"
                  onClick={() => handleCategoryClick(categoryName)}
                >
                  {categoryName}
                </h2>
                <div className="service-list">
                  {categoryData.services.map((service, index) => (
                    <div 
                      key={index} 
                      className="service-item clickable"
                      onClick={() => handleServiceClick(service)}
                    >
                      <span className="service-name">{service.name}</span>
                      <span className="service-price">{t('from', { uk: 'від', en: 'from' })} {service.price} {t('currency', translations.currency)}</span>
                      <span className="service-duration">{service.duration_minutes} {t('minutes', translations.minutes)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Модальне вікно */}
      <Modal 
        isOpen={modalOpen} 
        onClose={closeModal}
        title={modalType === 'category' ? modalData?.category?.name : modalData?.name}
      >
        {modalType === 'category' && modalData && (
          <div>
            <div className="modal-info-item">
              <div className="modal-info-label">{t('category_description', { uk: 'Опис категорії:', en: 'Category description:' })}</div>
              <div className="modal-info-value modal-description">
                {modalData.category.description}
              </div>
            </div>
            <div className="modal-info-item">
              <div className="modal-info-label">{t('services_in_category', { uk: 'Послуги в категорії:', en: 'Services in category:' })}</div>
              <ul className="modal-services-list">
                {modalData.services.map((service, index) => (
                  <li key={index}>
                    <div className="modal-service-item">
                      <span className="modal-service-name">{service.name}</span>
                      <span className="modal-service-price">{t('from', { uk: 'від', en: 'from' })} {service.price} {t('currency', translations.currency)}</span>
                      <span className="modal-service-duration">{service.duration_minutes} {t('minutes', translations.minutes)}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        {modalType === 'service' && modalData && (
          <div>
            <div className="modal-info-item">
              <div className="modal-info-label">{t('service_name', { uk: 'Назва послуги:', en: 'Service name:' })}</div>
              <div className="modal-info-value">{modalData.name}</div>
            </div>
            <div className="modal-info-item">
              <div className="modal-info-label">{t('description', { uk: 'Опис:', en: 'Description:' })}</div>
              <div className="modal-info-value modal-description">
                {modalData.description}
              </div>
            </div>
            <div className="modal-info-item">
              <div className="modal-info-label">{t('price', translations.price)}:</div>
              <div className="modal-info-value modal-price">
                {t('from', { uk: 'від', en: 'from' })} {modalData.price} {t('currency', translations.currency)}
              </div>
            </div>
            <div className="modal-info-item">
              <div className="modal-info-label">{t('duration', translations.duration)}:</div>
              <div className="modal-info-value">
                {modalData.duration_minutes} {t('minutes', translations.minutes)}
              </div>
            </div>
            <div className="modal-info-item">
              <div className="modal-info-label">{t('service_category', { uk: 'Категорія:', en: 'Category:' })}</div>
              <div className="modal-info-value">
                {modalData.category?.name}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Services; 