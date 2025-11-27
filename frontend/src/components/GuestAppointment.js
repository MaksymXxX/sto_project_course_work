import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import api from '../utils/api';
import { toast } from 'react-toastify';
import CustomDatePicker from './CustomDatePicker';

const GuestAppointment = () => {
  const { language, t } = useLanguage();
  const [formData, setFormData] = useState({
    service: '',
    appointment_date: '',
    appointment_time: '',
    guest_name: '',
    guest_phone: '',
    guest_email: '',
    notes: ''
  });

  const [services, setServices] = useState([]);
  const [availableTimes, setAvailableTimes] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchServices();
  }, [language]);

  const fetchServices = async () => {
    try {
      const response = await api.get(`/api/services/?language=${language}`);
      setServices(response.data);
    } catch (error) {
      console.error('Помилка отримання послуг:', error);
      toast.error(t('error_loading_services', { uk: 'Помилка отримання послуг', en: 'Error loading services' }));
    }
  };

  const fetchAvailableTimes = async (date, serviceId) => {
    try {
      const response = await api.get(`/api/boxes/available_times/?date=${date}&service_id=${serviceId}`);
      setAvailableTimes(response.data.available_times || []);
    } catch (error) {
      console.error('Помилка отримання доступних часів:', error);
      toast.error('Помилка отримання доступних часів');
      setAvailableTimes([]);
    }
  };

  const handleDateSelect = (date, service) => {
    if (service && service.id) {
      fetchAvailableTimes(date, service.id);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Якщо змінюється послуга, очищаємо час
    if (name === 'service') {
      setFormData(prev => ({
        ...prev,
        appointment_time: ''
      }));
      setAvailableTimes([]);
    }
  };

  const checkDateAvailability = async (date) => {
    try {
      const response = await api.get(`/api/boxes/available_times/?date=${date}`);
      const availableTimes = response.data.available_times || [];
      
      if (availableTimes.length === 0) {
        toast.warning('На цю дату немає доступних слотів. Оберіть іншу дату.');
        setFormData(prev => ({ ...prev, appointment_date: '', appointment_time: '' }));
      }
    } catch (error) {
      console.error('Помилка перевірки доступності дати:', error);
    }
  };

  const checkTimeAvailability = async (date, time) => {
    try {
      const response = await api.get(`/api/boxes/available_boxes/?date=${date}&time=${time}`);
      const availableBoxes = response.data;
      
      if (availableBoxes.length === 0) {
        toast.warning('На цей час немає вільних боксів. Оберіть інший час.');
        setFormData(prev => ({ ...prev, appointment_time: '' }));
      }
    } catch (error) {
      console.error('Помилка перевірки доступності часу:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const appointmentData = {
        service_id: parseInt(formData.service),
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time,
        guest_name: formData.guest_name,
        guest_phone: formData.guest_phone,
        guest_email: formData.guest_email,
        notes: formData.notes
      };

      console.log('Відправляємо дані:', appointmentData);
      const response = await api.post('/api/guest-appointments/', appointmentData);
      console.log('Отримана відповідь:', response.data);
      
      // Показуємо інформацію про призначений бокс
      if (response.data.box) {
        console.log('Бокс призначено:', response.data.box.name);
        toast.success(t('appointment_created_with_box', { 
          uk: `Запис успішно створено! Призначено бокс: ${response.data.box.name}`, 
          en: `Appointment successfully created! Assigned box: ${response.data.box.name}` 
        }));
      } else {
        console.log('Бокс НЕ призначено');
        toast.success(t('appointment_created', translations.appointment_created));
      }
      
      navigate('/');
    } catch (error) {
      console.error('Помилка створення запису:', error);
      if (error.response?.data) {
        Object.values(error.response.data).forEach(message => {
          toast.error(Array.isArray(message) ? message[0] : message);
        });
      } else {
        toast.error(t('error_creating_appointment', { uk: 'Помилка створення запису', en: 'Error creating appointment' }));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div className="card-header">
        <h2 className="card-title">{t('book_appointment', translations.book_appointment)}</h2>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="guest_name">{t('first_name', translations.first_name)}:</label>
          <input
            type="text"
            id="guest_name"
            name="guest_name"
            className="form-control"
            value={formData.guest_name}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="guest_phone">{t('phone', translations.phone)}:</label>
          <input
            type="tel"
            id="guest_phone"
            name="guest_phone"
            className="form-control"
            value={formData.guest_phone}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="guest_email">{t('email', translations.email)}:</label>
          <input
            type="email"
            id="guest_email"
            name="guest_email"
            className="form-control"
            value={formData.guest_email}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="service">{t('select_service', translations.select_service)} *</label>
          <select
            id="service"
            name="service"
            value={formData.service}
            onChange={handleChange}
            className="form-control"
            required
          >
            <option value="">{t('select_service_option', { uk: 'Оберіть послугу', en: 'Select service' })}</option>
            {services.map(service => (
              <option key={service.id} value={service.id}>
                {service.name} - {service.price} {t('currency', translations.currency)}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="appointment_date">{t('select_date', translations.select_date)} *</label>
          <CustomDatePicker
            value={formData.appointment_date}
            onChange={handleChange}
            disabled={!formData.service}
            selectedService={services.find(s => s.id === parseInt(formData.service))}
            onDateSelect={handleDateSelect}
            availableDates={[]} // Force CustomDatePicker to fetch dates based on selected service
            language={language}
          />
        </div>

        <div className="form-group">
          <label htmlFor="appointment_time">{t('select_time', translations.select_time)} *</label>
          <select
            id="appointment_time"
            name="appointment_time"
            value={formData.appointment_time}
            onChange={handleChange}
            className="form-control"
            required
            disabled={!formData.appointment_date || availableTimes.length === 0}
          >
            <option value="">{t('select_time_option', { uk: 'Оберіть час', en: 'Select time' })}</option>
            {availableTimes.map(time => (
              <option key={time} value={time}>
                {time}
              </option>
            ))}
          </select>
          {formData.appointment_date && availableTimes.length === 0 && (
            <small className="text-muted">{t('no_available_times', { uk: 'Немає доступних часів для обраної дати', en: 'No available times for selected date' })}</small>
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="notes">{t('notes', translations.notes)}:</label>
          <textarea
            id="notes"
            name="notes"
            className="form-control"
            value={formData.notes}
            onChange={handleChange}
            rows="3"
          />
        </div>
        
        <button
          type="submit"
          className="btn btn-primary w-100"
          disabled={loading}
        >
          {loading ? t('creating_appointment', { uk: 'Створення запису...', en: 'Creating appointment...' }) : t('submit_appointment', translations.submit_appointment)}
        </button>
      </form>
    </div>
  );
};

export default GuestAppointment; 