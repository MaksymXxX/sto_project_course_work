import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import userAvatar from '../assets/images/profile-icon-design-free-vector.jpg';
import './Dashboard.css';

const Dashboard = () => {
  const { isAuthenticated, logout } = useAuth();
  const { language, t } = useLanguage();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password_confirm: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [expandedAppointments, setExpandedAppointments] = useState(new Set());

  useEffect(() => {
    // Перевіряємо авторизацію
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        const [profileResponse, appointmentsResponse] = await Promise.all([
          api.get('/api/customers/profile/'),
          api.get(`/api/appointments/my_appointments/?language=${language}`)
        ]);
        
        console.log('Profile response:', profileResponse.data); // Debug log
        
        setProfile(profileResponse.data);
        setAppointments(appointmentsResponse.data || []);
        
        // Заповнюємо форму редагування
        if (profileResponse.data && profileResponse.data.user) {
          setEditForm({
            first_name: profileResponse.data.user.first_name || '',
            last_name: profileResponse.data.user.last_name || '',
            email: profileResponse.data.user.email || ''
          });
        }
      } catch (error) {
        console.error('Помилка завантаження даних:', error);
        if (error.response?.status === 401) {
          logout();
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, navigate, logout, language]);

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Валідація паролів
      if (editForm.password || editForm.password_confirm) {
        if (!editForm.password) {
          alert(t('enter_new_password', { uk: 'Будь ласка, введіть новий пароль', en: 'Please enter a new password' }));
          setLoading(false);
          return;
        }
        if (!editForm.password_confirm) {
          alert(t('confirm_new_password', { uk: 'Будь ласка, підтвердіть новий пароль', en: 'Please confirm the new password' }));
          setLoading(false);
          return;
        }
        if (editForm.password !== editForm.password_confirm) {
          alert(t('passwords_dont_match', { uk: 'Паролі не співпадають', en: 'Passwords do not match' }));
          setLoading(false);
          return;
        }
        if (editForm.password.length < 8) {
          alert(t('password_min_8_chars', { uk: 'Пароль повинен містити мінімум 8 символів', en: 'Password must contain at least 8 characters' }));
          setLoading(false);
          return;
        }
        
        // Додаткові перевірки для кращої валідації
        const password = editForm.password;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        
        if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
          alert(t('password_complexity', { uk: 'Пароль повинен містити великі та малі літери, а також цифри', en: 'Password must contain uppercase and lowercase letters, and numbers' }));
          setLoading(false);
          return;
        }
      }

      // Створюємо FormData для завантаження файлу
      const formData = new FormData();
      formData.append('first_name', editForm.first_name);
      formData.append('last_name', editForm.last_name);
      formData.append('email', editForm.email);
      
      // Додаємо пароль, якщо він введений
      if (editForm.password) {
        formData.append('password', editForm.password);
      }
      
      if (selectedFile) {
        formData.append('avatar', selectedFile);
      }

      // Оновлюємо дані користувача
      const userUpdateResponse = await api.put('/api/customers/update_profile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Update response:', userUpdateResponse.data); // Debug log
      
      setProfile(userUpdateResponse.data);
      setEditing(false);
      setSelectedFile(null);
      setPreviewUrl(null);
      
      // Очищаємо поля пароля
      setEditForm({
        ...editForm,
        password: '',
        password_confirm: ''
      });
      
      alert(t('profile_updated', { uk: 'Профіль успішно оновлено!', en: 'Profile updated successfully!' }));
    } catch (error) {
      console.error('Помилка оновлення профілю:', error);
      if (error.response?.status === 401) {
        logout();
        navigate('/login');
      } else if (error.response?.data?.error) {
        alert(error.response.data.error);
      } else {
        alert(t('profile_update_error', { uk: 'Помилка оновлення профілю. Спробуйте ще раз.', en: 'Profile update error. Try again.' }));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEditChange = (e) => {
    setEditForm({
      ...editForm,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      
      // Створюємо превью
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const calculateDiscount = () => {
    // Логіка розрахунку знижки на основі кількості відвідувань
    const completedAppointments = appointments.filter(app => app.status === 'completed').length;
    const discount = Math.min(completedAppointments * 0.5, 10); // 0.5% за кожне відвідування, максимум 10%
    return discount;
  };

  const handleCancelAppointment = async (appointmentId) => {
    if (!window.confirm(t('confirm_cancel_appointment', { uk: 'Ви впевнені, що хочете скасувати цей запис?', en: 'Are you sure you want to cancel this appointment?' }))) {
      return;
    }

    try {
      await api.post(`/api/appointments/${appointmentId}/cancel/`);
      
      // Оновлюємо список записів
      const updatedAppointments = appointments.map(app => 
        app.id === appointmentId ? { ...app, status: 'cancelled' } : app
      );
      setAppointments(updatedAppointments);
      
      alert(t('appointment_cancelled', { uk: 'Запис успішно скасовано', en: 'Appointment cancelled successfully' }));
    } catch (error) {
      console.error('Помилка скасування запису:', error);
      if (error.response?.data?.error) {
        alert(error.response.data.error);
      } else {
        alert(t('cancel_appointment_error', { uk: 'Помилка скасування запису. Спробуйте ще раз.', en: 'Error cancelling appointment. Try again.' }));
      }
    }
  };

  const toggleAppointmentDetails = (appointmentId) => {
    const newExpanded = new Set(expandedAppointments);
    if (newExpanded.has(appointmentId)) {
      newExpanded.delete(appointmentId);
    } else {
      newExpanded.add(appointmentId);
    }
    setExpandedAppointments(newExpanded);
  };

  const canEditAppointment = (appointment) => {
    // Перевіряємо чи до запису залишилося більше 2 годин
    const now = new Date();
    const appointmentDate = new Date(appointment.appointment_date);
    const appointmentTime = appointment.appointment_time.split(':');
    appointmentDate.setHours(parseInt(appointmentTime[0]), parseInt(appointmentTime[1]), 0, 0);
    
    const timeDifference = appointmentDate.getTime() - now.getTime();
    const hoursDifference = timeDifference / (1000 * 60 * 60);
    
    return hoursDifference >= 2;
  };

  const handleEditAppointment = (appointment) => {
    // Navigate to appointment page with pre-filled data
    navigate('/appointment', { 
      state: { 
        editMode: true, 
        appointmentData: appointment 
      } 
    });
  };

  // Функція для отримання URL аватара
  const getAvatarUrl = () => {
    if (profile?.avatar) {
      return profile.avatar;
    }
    return userAvatar;
  };

  if (loading) {
    return <div className="text-center">{t('loading', { uk: 'Завантаження...', en: 'Loading...' })}</div>;
  }

  return (
    <div className="dashboard-container" key={`dashboard-${language}`}>
      {/* Заголовок */}
      <div className="dashboard-header">
        <h1 className="dashboard-title">{t('personal_cabinet', { uk: 'ОСОБИСТИЙ КАБІНЕТ', en: 'PERSONAL CABINET' })}</h1>
        <div className="header-actions">
          <button 
            className="edit-profile-btn"
            onClick={() => setEditing(!editing)}
          >
            {t('edit_profile', { uk: 'Редагувати профіль', en: 'Edit Profile' })}
          </button>
          <button 
            className="logout-btn"
            onClick={() => {
              logout();
              navigate('/');
            }}
          >
            {t('logout', { uk: 'Вийти', en: 'Logout' })}
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Ліва секція - Профіль */}
        <div className="profile-section">
          <div className="profile-avatar">
            <img 
              src={editing && previewUrl ? previewUrl : getAvatarUrl()} 
              alt={t('user_avatar', { uk: 'Аватар користувача', en: 'User avatar' })} 
              className="avatar-img" 
            />
            {editing && (
              <div className="avatar-upload">
                <input
                  type="file"
                  id="avatar-upload"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="avatar-input"
                />
                <label htmlFor="avatar-upload" className="avatar-upload-btn">
                  {t('change_photo', { uk: 'Змінити фото', en: 'Change photo' })}
                </label>
              </div>
            )}
          </div>

          <div className="profile-form">
            {editing ? (
              <form onSubmit={handleEditSubmit} className="edit-form">
                <div className="form-group">
                  <label>{t('first_name', { uk: 'Ім\'я', en: 'First Name' })}</label>
                  <input
                    type="text"
                    name="first_name"
                    value={editForm.first_name}
                    onChange={handleEditChange}
                    className="form-input"
                  />
                </div>
                
                <div className="form-group">
                  <label>{t('last_name', { uk: 'Фамілія', en: 'Last Name' })}</label>
                  <input
                    type="text"
                    name="last_name"
                    value={editForm.last_name}
                    onChange={handleEditChange}
                    className="form-input"
                  />
                </div>
                
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={editForm.email}
                    onChange={handleEditChange}
                    className="form-input"
                  />
                </div>
                
                <div className="form-group">
                  <label>{t('new_password_optional', { uk: 'Новий пароль (залиште порожнім, якщо не хочете змінювати)', en: 'New password (leave empty if you don\'t want to change)' })}</label>
                  <input
                    type="password"
                    name="password"
                    value={editForm.password}
                    onChange={handleEditChange}
                    className="form-input"
                    placeholder={t('enter_new_password_placeholder', { uk: 'Введіть новий пароль', en: 'Enter new password' })}
                  />
                  <small style={{color: '#666', fontSize: '12px', marginTop: '4px'}}>
                    {t('password_requirements', { uk: 'Пароль повинен містити мінімум 8 символів, великі та малі літери, цифри', en: 'Password must contain at least 8 characters, uppercase and lowercase letters, numbers' })}
                  </small>
                </div>
                
                <div className="form-group">
                  <label>{t('confirm_new_password', { uk: 'Підтвердіть новий пароль', en: 'Confirm new password' })}</label>
                  <input
                    type="password"
                    name="password_confirm"
                    value={editForm.password_confirm}
                    onChange={handleEditChange}
                    className="form-input"
                    placeholder={t('repeat_new_password', { uk: 'Повторіть новий пароль', en: 'Repeat new password' })}
                  />
                  <small style={{color: '#666', fontSize: '12px', marginTop: '4px'}}>
                    {t('confirm_password_hint', { uk: 'Введіть пароль ще раз для підтвердження', en: 'Enter password again for confirmation' })}
                  </small>
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="save-btn">{t('save', { uk: 'Зберегти', en: 'Save' })}</button>
                  <button 
                    type="button" 
                    className="cancel-btn"
                    onClick={() => {
                      setEditing(false);
                      setSelectedFile(null);
                      setPreviewUrl(null);
                      setEditForm({
                        ...editForm,
                        password: '',
                        password_confirm: ''
                      });
                    }}
                  >
                    {t('cancel', { uk: 'Скасувати', en: 'Cancel' })}
                  </button>
                </div>
              </form>
            ) : (
              <div className="profile-info">
                <div className="info-group">
                  <label>{t('first_name', { uk: 'Ім\'я', en: 'First Name' })}</label>
                  <div className="info-value">{profile?.user?.first_name || t('not_specified', { uk: 'Не вказано', en: 'Not specified' })}</div>
                </div>
                
                <div className="info-group">
                  <label>{t('last_name', { uk: 'Фамілія', en: 'Last Name' })}</label>
                  <div className="info-value">{profile?.user?.last_name || t('not_specified', { uk: 'Не вказано', en: 'Not specified' })}</div>
                </div>
                
                <div className="info-group">
                  <label>Email</label>
                  <div className="info-value">{profile?.user?.email || t('not_specified', { uk: 'Не вказано', en: 'Not specified' })}</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Права секція - Знижка та записи */}
        <div className="right-section">
          {/* Знижка */}
          <div className="discount-section">
            <div className="discount-info">
              <p className="discount-text">
                {t('personal_discount', { uk: 'Ваша персональна знижка становить', en: 'Your personal discount is' })} {calculateDiscount()}%
              </p>
              <div className="discount-details">
                <p>{t('discount_every_2_visits', { uk: 'Кожне 2 відвідування дарує вам 1% знижки.', en: 'Every 2 visits give you 1% discount.' })}</p>
                <p>{t('max_discount_10', { uk: 'Максимальна знижка - 10%', en: 'Maximum discount - 10%' })}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Записи - перенесено вниз */}
      <div className="appointments-section-bottom">
        <div className="appointments-header">
          <h3 className="appointments-title">{t('your_appointments', { uk: 'ВАШІ ЗАПИСИ:', en: 'YOUR APPOINTMENTS:' })}</h3>
        </div>
        
        {appointments.length === 0 ? (
          <p className="no-appointments">{t('no_appointments_yet', { uk: 'У вас поки немає записів', en: 'You don\'t have any appointments yet' })}</p>
        ) : (
          <div className="appointments-list">
            {appointments.map((appointment) => (
              <div key={appointment.id} className="appointment-item">
                <div className="appointment-header">
                  <div className="appointment-status">
                    <span className={`status-badge status-${appointment.status}`}>
                      {appointment.status === 'pending' && t('pending_confirmation', { uk: 'Очікує підтвердження', en: 'Pending confirmation' })}
                      {appointment.status === 'confirmed' && t('confirmed', { uk: 'Підтверджено', en: 'Confirmed' })}
                      {appointment.status === 'in_progress' && t('in_progress', { uk: 'В процесі', en: 'In progress' })}
                      {appointment.status === 'completed' && t('completed', { uk: 'Завершено', en: 'Completed' })}
                      {appointment.status === 'cancelled' && t('cancelled_by_client', { uk: 'Скасовано клієнтом', en: 'Cancelled by client' })}
                      {appointment.status === 'cancelled_by_admin' && t('cancelled_by_admin', { uk: 'Скасовано адміністратором', en: 'Cancelled by administrator' })}
                    </span>
                  </div>
                  <div className="appointment-date">
                    {new Date(appointment.appointment_date).toLocaleDateString(language === 'en' ? 'en-US' : 'uk-UA', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                  <div className="appointment-actions-header">
                    {appointment.status === 'pending' && canEditAppointment(appointment) && (
                      <button 
                        className="edit-appointment-btn"
                        onClick={() => handleEditAppointment(appointment)}
                      >
                        {t('edit', { uk: 'Змінити', en: 'Edit' })}
                      </button>
                    )}
                    {appointment.status === 'pending' && !canEditAppointment(appointment) && (
                      <span className="edit-disabled-text">
                        {t('edit_less_2_hours', { uk: 'Змінити (менше 2 годин)', en: 'Edit (less than 2 hours)' })}
                      </span>
                    )}
                    <button 
                      className="expand-details-btn"
                      onClick={() => toggleAppointmentDetails(appointment.id)}
                    >
                      <span className={`expand-arrow ${expandedAppointments.has(appointment.id) ? 'expanded' : ''}`}>
                        ▼
                      </span>
                    </button>
                  </div>
                </div>
                
                {expandedAppointments.has(appointment.id) && (
                  <div className="appointment-details">
                    <div className="detail-row">
                      <span className="detail-label">{t('service', { uk: 'Послуга:', en: 'Service:' })}</span>
                      <span className="detail-value">{appointment.service?.name}</span>
                    </div>
                    
                    <div className="detail-row">
                      <span className="detail-label">{t('time', { uk: 'Час:', en: 'Time:' })}</span>
                      <span className="detail-value">
                        {new Date(`2000-01-01T${appointment.appointment_time}`).toLocaleTimeString(language === 'en' ? 'en-US' : 'uk-UA', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    
                    {appointment.box && (
                      <div className="detail-row">
                        <span className="detail-label">{t('box', { uk: 'Бокс:', en: 'Box:' })}</span>
                        <span className="detail-value">{appointment.box.name}</span>
                      </div>
                    )}
                    
                    <div className="detail-row">
                      <span className="detail-label">{t('cost', { uk: 'Вартість:', en: 'Cost:' })}</span>
                      <span className="detail-value">
                        {appointment.total_price} {language === 'en' ? 'UAH' : 'грн'}
                        {(() => {
                          const selectedService = appointment.service;
                          if (selectedService && selectedService.price !== appointment.total_price) {
                            const discountAmount = selectedService.price - appointment.total_price;
                            const discountPercentage = (discountAmount / selectedService.price) * 100;
                            return (
                              <span className="discount-applied">
                                {' '}({t('discount', { uk: 'знижка', en: 'discount' })} {discountPercentage.toFixed(1)}%: -{discountAmount.toFixed(2)} {language === 'en' ? 'UAH' : 'грн'})
                              </span>
                            );
                          }
                          return null;
                        })()}
                      </span>
                    </div>
                    
                    {appointment.notes && (
                      <div className="detail-row">
                        <span className="detail-label">{t('notes', { uk: 'Примітки:', en: 'Notes:' })}</span>
                        <span className="detail-value">{appointment.notes}</span>
                      </div>
                    )}
                  </div>
                )}
                
                <div className="appointment-actions">
                  {appointment.status === 'pending' && (
                    <button 
                      className="cancel-appointment-btn"
                      onClick={() => handleCancelAppointment(appointment.id)}
                    >
                      {t('cancel_appointment', { uk: 'Скасувати запис', en: 'Cancel appointment' })}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 