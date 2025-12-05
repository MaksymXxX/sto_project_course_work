import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useLanguage } from '../contexts/LanguageContext';

const ServiceHistory = () => {
  const { language } = useLanguage();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get('/api/service-history/');
        setHistory(response.data);
      } catch (error) {
        console.error('Помилка завантаження історії:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return <div className="text-center">Завантаження історії...</div>;
  }

  return (
    <div>
      <h1 className="page-title">Історія обслуговування</h1>

      {history.length > 0 ? (
        <div className="card">
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Послуга</th>
                  <th>Дата завершення</th>
                  <th>Фактична тривалість</th>
                  <th>Фінальна вартість</th>
                  <th>Примітки механіка</th>
                </tr>
              </thead>
              <tbody>
                {history.map(item => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.appointment.service.name}</strong>
                      <br />
                      <small>Запис: {item.appointment.appointment_date} {item.appointment.appointment_time}</small>
                    </td>
                    <td>{new Date(item.completed_at).toLocaleDateString(language === 'en' ? 'en-US' : 'uk-UA')}</td>
                    <td>{item.actual_duration} {language === 'en' ? 'minutes' : 'хвилин'}</td>
                    <td>{item.final_price} {language === 'en' ? 'UAH' : 'грн'}</td>
                    <td>
                      {item.mechanic_notes ? (
                        <small>{item.mechanic_notes}</small>
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
            <h3>Історія обслуговування порожня</h3>
            <p>Тут будуть відображатися завершені обслуговування</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ServiceHistory; 