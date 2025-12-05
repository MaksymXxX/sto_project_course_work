import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import api from '../utils/api';
import { toast } from 'react-toastify';
import CustomDatePicker from './CustomDatePicker';

const CustomerAppointment = () => {
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
  const [editMode, setEditMode] = useState(false);
  const [editAppointmentId, setEditAppointmentId] = useState(null);
  const [discount, setDiscount] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Спочатку завантажуємо послуги з урахуванням мови
        const servicesResponse = await api.get(`/api/services/?language=${language}`);
        setServices(servicesResponse.data);

        // Перевіряємо чи це режим редагування
        if (location.state?.editMode && location.state?.appointmentData) {
          const appointmentData = location.state.appointmentData;

          // Спочатку встановлюємо режим редагування
          setEditMode(true);
          setEditAppointmentId(appointmentData.id);

          // Завантажуємо профіль для розрахунку знижки
          try {
            const profileResponse = await api.get('/api/customers/profile/');

            // Розраховуємо знижку після завантаження профілю
            const completedAppointments = profileResponse.data.completed_appointments_count || 0;
            const discountPercentage = Math.min(completedAppointments * 0.5, 10);
            setDiscount(discountPercentage);
          } catch (profileError) {
            console.error('Помилка завантаження профілю:', profileError);
          }

          // Заповнюємо форму даними існуючого запису
          const editFormData = {
            service: appointmentData.service?.id?.toString() || '',
            appointment_date: appointmentData.appointment_date,
            appointment_time: appointmentData.appointment_time ? appointmentData.appointment_time.substring(0, 5) : '',
            guest_name: appointmentData.guest_name || '',
            guest_phone: appointmentData.guest_phone || '',
            guest_email: appointmentData.guest_email || '',
            notes: appointmentData.notes || ''
          };

          // Встановлюємо форму
          setFormData(editFormData);

          // Завантажуємо доступні часи для цієї дати та послуги
          if (appointmentData.service?.id && appointmentData.appointment_date) {
            // Використовуємо setTimeout щоб дати час React оновити стан
            setTimeout(() => {
              const formattedTime = appointmentData.appointment_time ? appointmentData.appointment_time.substring(0, 5) : null;
              fetchAvailableTimes(appointmentData.appointment_date, appointmentData.service.id, formattedTime);
            }, 100);
          }
        } else {
          // Потім завантажуємо профіль для нового запису
          try {
            const profileResponse = await api.get('/api/customers/profile/');

            // Розраховуємо знижку після завантаження профілю
            const completedAppointments = profileResponse.data.completed_appointments_count || 0;
            const discountPercentage = Math.min(completedAppointments * 0.5, 10);
            setDiscount(discountPercentage);

            // Заповнюємо форму даними користувача
            if (profileResponse.data && profileResponse.data.user) {
              const userData = profileResponse.data.user;
              const customerData = profileResponse.data;

              const newFormData = {
                ...formData,
                guest_name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim(),
                guest_email: userData.email || '',
                guest_phone: customerData.phone || ''
              };

              setFormData(newFormData);
            }
          } catch (profileError) {
            console.error('Помилка завантаження профілю:', profileError);
          }
        }
      } catch (error) {
        console.error('Помилка завантаження даних:', error);
      }
    };

    fetchData();
  }, [location.state, language]); // eslint-disable-line react-hooks/exhaustive-deps

  // useEffect для обробки зміни послуги
  useEffect(() => {
    if (formData.service) {
      // Якщо змінилася послуга, очищаємо доступні часи
      setAvailableTimes([]);
    }
  }, [formData.service]);

  const fetchAvailableTimes = async (date, serviceId, previousTime = null) => {
    try {
      let url = `/api/boxes/available_times/?date=${date}&service_id=${serviceId}`;

      // Якщо ми в режимі редагування, додаємо ID запису для виключення
      if (editMode && editAppointmentId) {
        url += `&exclude_appointment_id=${editAppointmentId}`;
      }

      const response = await api.get(url);
      const times = response.data.available_times || [];

      // Якщо у нас є попередньо обраний час, додаємо його до списку доступних часів
      if (previousTime && !times.includes(previousTime)) {
        times.push(previousTime);
        times.sort(); // Сортуємо часи
      }

      setAvailableTimes(times);
    } catch (error) {
      console.error('Помилка отримання доступних часів:', error);
      toast.error('Помилка отримання доступних часів');
      setAvailableTimes([]);
    }
  };

  const handleDateSelect = (date, service) => {
    if (service && service.id) {
      fetchAvailableTimes(date, service.id, formData.appointment_time);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Якщо змінюється послуга, очищаємо дату та час
    if (name === 'service') {
      setFormData(prev => ({
        ...prev,
        appointment_date: '',
        appointment_time: ''
      }));
      setAvailableTimes([]); // Очищаємо доступні часи
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Перевіряємо час до запису (тільки для редагування)
      if (editMode) {
        const now = new Date();
        const appointmentDate = new Date(formData.appointment_date);
        const appointmentTime = formData.appointment_time.split(':');
        appointmentDate.setHours(parseInt(appointmentTime[0]), parseInt(appointmentTime[1]), 0, 0);

        const timeDifference = appointmentDate.getTime() - now.getTime();
        const hoursDifference = timeDifference / (1000 * 60 * 60);

        if (hoursDifference < 2) {
          toast.error('Не можна редагувати запис менше ніж за 2 години до його початку. Зверніться до адміністратора для внесення змін.');
          setLoading(false);
          return;
        }
      }

      const appointmentData = {
        service_id: parseInt(formData.service),
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time,
        guest_name: formData.guest_name,
        guest_phone: formData.guest_phone,
        guest_email: formData.guest_email,
        notes: formData.notes
      };

      let response;
      if (editMode) {
        // Оновлення існуючого запису
        response = await api.put(`/api/appointments/${editAppointmentId}/?language=${language}`, appointmentData);
        toast.success(t('appointment_updated', translations.appointment_updated));
      } else {
        // Створення нового запису
        response = await api.post(`/api/appointments/?language=${language}`, appointmentData);

        // Показуємо інформацію про призначений бокс
        if (response.data.box) {
          const boxName = response.data.box.name;
          toast.success(t('appointment_created_with_box', {
            uk: `Запис успішно створено! Призначено бокс: ${boxName}`,
            en: `Appointment successfully created! Assigned box: ${boxName}`
          }));
        } else {
          toast.success(t('appointment_created', translations.appointment_created));
        }
      }

      navigate('/dashboard');
    } catch (error) {
      console.error('Помилка створення/оновлення запису:', error);
      if (error.response?.data) {
        Object.values(error.response.data).forEach(message => {
          toast.error(Array.isArray(message) ? message[0] : message);
        });
      } else {
        toast.error(editMode ? t('error_updating_appointment', { uk: 'Помилка оновлення запису', en: 'Error updating appointment' }) : t('error_creating_appointment', { uk: 'Помилка створення запису', en: 'Error creating appointment' }));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }} key={`appointment-form-${language}`}>
      <div className="card-header">
        <h2 className="card-title">
          {editMode ? t('edit_appointment', { uk: 'Редагування запису', en: 'Edit appointment' }) : t('book_appointment', translations.book_appointment)}
        </h2>
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
                {service.name} - {service.price} {language === 'en' ? 'UAH' : 'грн'} ({service.duration_minutes} {language === 'en' ? 'min' : 'хв'})
              </option>
            ))}
          </select>
        </div>

        {/* Відображення знижки та фінальної ціни */}
        {formData.service && discount > 0 && (
          <div className="discount-info">
            <div className="discount-details">
              <p><strong>{t('your_discount', translations.your_discount)}: {discount.toFixed(1)}%</strong></p>
              {(() => {
                const selectedService = services.find(s => s.id.toString() === formData.service);
                if (selectedService) {
                  const originalPrice = selectedService.price;
                  const discountAmount = (originalPrice * discount) / 100;
                  const finalPrice = originalPrice - discountAmount;
                  return (
                    <div className="price-breakdown">
                      <p>{t('original_price', translations.original_price)}: {originalPrice} {language === 'en' ? 'UAH' : 'грн'}</p>
                      <p>{t('discount_amount', translations.discount_amount)}: -{discountAmount.toFixed(2)} {language === 'en' ? 'UAH' : 'грн'}</p>
                      <p className="final-price"><strong>{t('final_price', translations.final_price)}: {finalPrice.toFixed(2)} {language === 'en' ? 'UAH' : 'грн'}</strong></p>
                    </div>
                  );
                }
                return null;
              })()}
            </div>
          </div>
        )}

        {formData.service && (
          <div className="form-group">
            <label>{t('select_date', translations.select_date)} *</label>
            <CustomDatePicker
              selectedService={services.find(s => s.id.toString() === formData.service)}
              value={formData.appointment_date}
              excludeAppointmentId={editMode ? editAppointmentId : null}
              onChange={(e) => {
                setFormData(prev => ({ ...prev, appointment_date: e.target.value }));
                handleDateSelect(e.target.value, services.find(s => s.id.toString() === formData.service));
              }}
              language={language}
            />
          </div>
        )}

        {formData.appointment_date && formData.service && (
          <div className="form-group">
            <label htmlFor="appointment_time">{t('select_time', translations.select_time)} *</label>
            <select
              id="appointment_time"
              name="appointment_time"
              value={formData.appointment_time}
              onChange={handleChange}
              className="form-control"
              required
            >
              <option value="">{t('select_time_option', { uk: 'Оберіть час', en: 'Select time' })}</option>
              {availableTimes.map(time => (
                <option key={time} value={time}>
                  {new Date(`2000-01-01T${time}`).toLocaleTimeString(language === 'en' ? 'en-US' : 'uk-UA', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </option>
              ))}
            </select>
          </div>
        )}

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

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? t('loading', translations.loading) : (editMode ? t('update_appointment', { uk: 'Оновити запис', en: 'Update appointment' }) : t('create_appointment', { uk: 'Створити запис', en: 'Create appointment' }))}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/dashboard')}
          >
            {t('cancel', translations.cancel)}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CustomerAppointment;