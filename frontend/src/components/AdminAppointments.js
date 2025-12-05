import React, { useState } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import Modal from './Modal';
import { useLanguage } from '../contexts/LanguageContext';
import './AdminAppointments.css';

const AdminAppointments = () => {
  const { language } = useLanguage();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [boxes, setBoxes] = useState([]);
  const [services, setServices] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showFilters, setShowFilters] = useState(true);

  // Розширені фільтри
  const [filters, setFilters] = useState({
    date_from: '',
    date_to: '',
    box_id: '',
    service_id: '',
    status: '',
    customer_name: '',
    time_from: '',
    time_to: '',
    price_min: '',
    price_max: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);

      // Завантажуємо бокси та послуги для фільтрів
      const [boxesResponse, servicesResponse] = await Promise.all([
        api.get('/api/boxes/'),
        api.get('/api/services/')
      ]);

      setBoxes(boxesResponse.data);
      setServices(servicesResponse.data);

      // Завантажуємо бронювання з фільтрами
      const params = new URLSearchParams();
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      if (filters.box_id) params.append('box_id', filters.box_id);
      if (filters.service_id) params.append('service_id', filters.service_id);
      if (filters.status) params.append('status', filters.status);
      if (filters.customer_name) params.append('customer_name', filters.customer_name);
      if (filters.time_from) params.append('time_from', filters.time_from);
      if (filters.time_to) params.append('time_to', filters.time_to);
      if (filters.price_min) params.append('price_min', filters.price_min);
      if (filters.price_max) params.append('price_max', filters.price_max);

      const appointmentsResponse = await api.get(`/api/admin/appointments/?${params.toString()}`);
      setAppointments(appointmentsResponse.data);
    } catch (error) {
      console.error('Помилка завантаження даних:', error);
      toast.error('Помилка завантаження даних');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      date_from: '',
      date_to: '',
      box_id: '',
      service_id: '',
      status: '',
      customer_name: '',
      time_from: '',
      time_to: '',
      price_min: '',
      price_max: ''
    });
  };

  const getActiveFiltersCount = () => {
    return Object.values(filters).filter(value => value !== '').length;
  };

  const handleAppointmentAction = async (appointmentId, action) => {
    try {
      let successMessage = '';

      switch (action) {
        case 'confirm':
          await api.post(`/api/appointments/${appointmentId}/confirm/`);
          successMessage = 'Запис підтверджено';
          break;
        case 'cancel':
          await api.post(`/api/appointments/${appointmentId}/cancel/`);
          successMessage = 'Запис скасовано';
          break;
        case 'complete':
          await api.post(`/api/appointments/${appointmentId}/complete/`);
          successMessage = 'Запис завершено';
          break;
        default:
          return;
      }

      toast.success(successMessage);
      fetchData(); // Оновлюємо список
    } catch (error) {
      console.error(`Помилка ${action}:`, error);
      toast.error(`Помилка при ${action === 'confirm' ? 'підтвердженні' : action === 'cancel' ? 'скасуванні' : 'завершенні'} запису`);
    }
  };

  const openAppointmentDetails = (appointment) => {
    setSelectedAppointment(appointment);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedAppointment(null);
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'status-badge status-pending';
      case 'confirmed':
        return 'status-badge status-confirmed';
      case 'completed':
        return 'status-badge status-completed';
      case 'cancelled':
        return 'status-badge status-cancelled';
      case 'cancelled_by_admin':
        return 'status-badge status-cancelled-admin';
      default:
        return 'status-badge';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'Очікує';
      case 'confirmed':
        return 'Підтверджено';
      case 'completed':
        return 'Завершено';
      case 'cancelled':
        return 'Скасовано клієнтом';
      case 'cancelled_by_admin':
        return 'Скасовано адміністратором';
      default:
        return status;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('uk-UA');
  };

  const formatTime = (timeString) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('uk-UA', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="text-center">Завантаження...</div>;
  }

  return (
    <div className="admin-appointments">
      <div className="admin-header">
        <h1>Управління бронюваннями</h1>
        <div className="header-actions">
          <button
            className="btn btn-outline-primary"
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? 'Сховати фільтри' : 'Показати фільтри'}
          </button>
        </div>
      </div>

      {/* Розширені фільтри */}
      {showFilters && (
        <div className="filters-section">
          <div className="filters-header">
            <h3>Фільтри {getActiveFiltersCount() > 0 && `(${getActiveFiltersCount()} активних)`}</h3>
            <button
              className="btn btn-sm btn-outline-secondary"
              onClick={clearFilters}
              disabled={getActiveFiltersCount() === 0}
            >
              Очистити всі
            </button>
          </div>

          <div className="filters-grid">
            {/* Основні фільтри */}
            <div className="filter-row">
              <div className="filter-group">
                <label>Дата від:</label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => handleFilterChange('date_from', e.target.value)}
                />
              </div>

              <div className="filter-group">
                <label>Дата до:</label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => handleFilterChange('date_to', e.target.value)}
                />
              </div>

              <div className="filter-group">
                <label>Час від:</label>
                <input
                  type="time"
                  value={filters.time_from}
                  onChange={(e) => handleFilterChange('time_from', e.target.value)}
                />
              </div>

              <div className="filter-group">
                <label>Час до:</label>
                <input
                  type="time"
                  value={filters.time_to}
                  onChange={(e) => handleFilterChange('time_to', e.target.value)}
                />
              </div>
            </div>

            <div className="filter-row">
              <div className="filter-group">
                <label>Бокс:</label>
                <select
                  value={filters.box_id}
                  onChange={(e) => handleFilterChange('box_id', e.target.value)}
                >
                  <option value="">Всі бокси</option>
                  {boxes.map(box => (
                    <option key={box.id} value={box.id}>{box.name}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>Послуга:</label>
                <select
                  value={filters.service_id}
                  onChange={(e) => handleFilterChange('service_id', e.target.value)}
                >
                  <option value="">Всі послуги</option>
                  {services.map(service => (
                    <option key={service.id} value={service.id}>{service.name}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>Статус:</label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <option value="">Всі статуси</option>
                  <option value="pending">Очікує</option>
                  <option value="confirmed">Підтверджено</option>
                  <option value="completed">Завершено</option>
                  <option value="cancelled">Скасовано</option>
                </select>
              </div>

              <div className="filter-group">
                <label>Клієнт (ім'я):</label>
                <input
                  type="text"
                  placeholder="Введіть ім'я клієнта"
                  value={filters.customer_name}
                  onChange={(e) => handleFilterChange('customer_name', e.target.value)}
                />
              </div>
            </div>

            <div className="filter-row">
              <div className="filter-group">
                <label>Ціна від ({language === 'en' ? 'UAH' : 'грн'}):</label>
                <input
                  type="number"
                  placeholder="Мін. ціна"
                  value={filters.price_min}
                  onChange={(e) => handleFilterChange('price_min', e.target.value)}
                />
              </div>

              <div className="filter-group">
                <label>Ціна до ({language === 'en' ? 'UAH' : 'грн'}):</label>
                <input
                  type="number"
                  placeholder="Макс. ціна"
                  value={filters.price_max}
                  onChange={(e) => handleFilterChange('price_max', e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Список бронювань */}
      <div className="appointments-list">
        <div className="list-header">
          <h3>Список бронювань ({appointments.length})</h3>
          <div className="list-actions">
            <button
              className="btn btn-sm btn-outline-primary"
              onClick={fetchData}
            >
              Оновити
            </button>
          </div>
        </div>

        {appointments.length === 0 ? (
          <div className="no-appointments">
            <p>Бронювань не знайдено</p>
            {getActiveFiltersCount() > 0 && (
              <button
                className="btn btn-outline-secondary"
                onClick={clearFilters}
              >
                Очистити фільтри
              </button>
            )}
          </div>
        ) : (
          <div className="appointments-table">
            {loading && (
              <div className="loading-overlay">
                <div className="loading-spinner">Завантаження...</div>
              </div>
            )}
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Клієнт</th>
                  <th>Послуга</th>
                  <th>Дата</th>
                  <th>Час</th>
                  <th>Бокс</th>
                  <th>Статус</th>
                  <th>Ціна</th>
                  <th>Дії</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map(appointment => (
                  <tr key={appointment.id}>
                    <td>{appointment.id}</td>
                    <td>
                      {appointment.customer ?
                        `${appointment.customer.user?.first_name || ''} ${appointment.customer.user?.last_name || ''}`.trim() ||
                        appointment.guest_name :
                        appointment.guest_name
                      }
                    </td>
                    <td>{appointment.service?.name}</td>
                    <td>{formatDate(appointment.appointment_date)}</td>
                    <td>{formatTime(appointment.appointment_time)}</td>
                    <td>{appointment.box?.name}</td>
                    <td>
                      <span className={getStatusBadgeClass(appointment.status)}>
                        {getStatusText(appointment.status)}
                      </span>
                    </td>
                    <td>{appointment.total_price} {language === 'en' ? 'UAH' : 'грн'}</td>
                    <td>
                      <div className="appointment-actions">
                        <button
                          className="btn btn-sm btn-info"
                          onClick={() => openAppointmentDetails(appointment)}
                        >
                          Деталі
                        </button>

                        {appointment.status === 'pending' && (
                          <>
                            <button
                              className="btn btn-sm btn-success"
                              onClick={() => handleAppointmentAction(appointment.id, 'confirm')}
                            >
                              Підтвердити
                            </button>
                            <button
                              className="btn btn-sm btn-warning"
                              onClick={() => handleAppointmentAction(appointment.id, 'cancel')}
                            >
                              Скасувати
                            </button>
                          </>
                        )}

                        {appointment.status === 'confirmed' && (
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() => handleAppointmentAction(appointment.id, 'complete')}
                          >
                            Завершити
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Модальне вікно з деталями */}
      <Modal
        isOpen={modalOpen}
        onClose={closeModal}
        title={`Деталі бронювання #${selectedAppointment?.id}`}
      >
        {selectedAppointment && (
          <div className="appointment-details">
            <div className="detail-row">
              <strong>ID:</strong> {selectedAppointment.id}
            </div>
            <div className="detail-row">
              <strong>Клієнт:</strong>
              {selectedAppointment.customer ?
                `${selectedAppointment.customer.user?.first_name || ''} ${selectedAppointment.customer.user?.last_name || ''}`.trim() ||
                selectedAppointment.guest_name :
                selectedAppointment.guest_name
              }
            </div>
            <div className="detail-row">
              <strong>Телефон:</strong> {selectedAppointment.guest_phone}
            </div>
            <div className="detail-row">
              <strong>Email:</strong> {selectedAppointment.guest_email}
            </div>
            <div className="detail-row">
              <strong>Послуга:</strong> {selectedAppointment.service?.name}
            </div>
            <div className="detail-row">
              <strong>Дата:</strong> {formatDate(selectedAppointment.appointment_date)}
            </div>
            <div className="detail-row">
              <strong>Час:</strong> {formatTime(selectedAppointment.appointment_time)}
            </div>
            <div className="detail-row">
              <strong>Бокс:</strong> {selectedAppointment.box?.name}
            </div>
            <div className="detail-row">
              <strong>Статус:</strong>
              <span className={getStatusBadgeClass(selectedAppointment.status)}>
                {getStatusText(selectedAppointment.status)}
              </span>
            </div>
            <div className="detail-row">
              <strong>Ціна:</strong> {selectedAppointment.total_price} {language === 'en' ? 'UAH' : 'грн'}
            </div>
            {selectedAppointment.notes && (
              <div className="detail-row">
                <strong>Примітки:</strong> {selectedAppointment.notes}
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AdminAppointments; 