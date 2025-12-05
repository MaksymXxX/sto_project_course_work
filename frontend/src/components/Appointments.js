import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { useLanguage } from '../contexts/LanguageContext';

const Appointments = () => {
  const { language } = useLanguage();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const response = await api.get('/api/appointments/my_appointments/');
        setAppointments(response.data);
      } catch (error) {
        console.error('Помилка завантаження записів:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': { class: 'badge-warning', text: 'Очікує підтвердження' },
      'confirmed': { class: 'badge-info', text: 'Підтверджено' },
      'in_progress': { class: 'badge-primary', text: 'В роботі' },
      'completed': { class: 'badge-success', text: 'Завершено' },
      'cancelled': { class: 'badge-danger', text: 'Скасовано' }
    };
    
    const statusInfo = statusMap[status] || { class: 'badge-secondary', text: status };
    return <span className={`badge ${statusInfo.class}`}>{statusInfo.text}</span>;
  };

  if (loading) {
    return <div className="text-center">Завантаження записів...</div>;
  }

  return (
    <div>
      <h1 className="page-title">Мої записи</h1>
      
      {appointments.length > 0 ? (
        <div className="card">
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Послуга</th>
                  <th>Дата</th>
                  <th>Час</th>
                  <th>Статус</th>
                  <th>Вартість</th>
                  <th>Примітки</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map(appointment => (
                  <tr key={appointment.id}>
                    <td>
                      <strong>{appointment.service.name}</strong>
                      <br />
                      <small>{appointment.service.description}</small>
                    </td>
                    <td>{appointment.appointment_date}</td>
                    <td>{appointment.appointment_time}</td>
                    <td>{getStatusBadge(appointment.status)}</td>
                    <td>{appointment.total_price} {language === 'en' ? 'UAH' : 'грн'}</td>
                    <td>
                      {appointment.notes ? (
                        <small>{appointment.notes}</small>
                      ) : (
                        <small className="text-muted">Немає приміток</small>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="text-center">
            <h3>У вас поки немає записів</h3>
            <p>Запишіться на обслуговування, щоб побачити їх тут</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments; 