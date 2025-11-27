import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const LoyaltyProgram = () => {
  const [profile, setProfile] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileResponse, transactionsResponse] = await Promise.all([
          api.get('/api/customers/profile/'),
          api.get('/api/loyalty-transactions/')
        ]);
        
        setProfile(profileResponse.data);
        setTransactions(transactionsResponse.data);
      } catch (error) {
        console.error('Помилка завантаження даних лояльності:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getTransactionTypeBadge = (type) => {
    return type === 'earned' ? 
      <span className="badge badge-success">Зароблено</span> : 
      <span className="badge badge-warning">Витрачено</span>;
  };

  if (loading) {
    return <div className="text-center">Завантаження програми лояльності...</div>;
  }

  return (
    <div>
      <h1 className="page-title">Програма лояльності</h1>
      
      <div className="grid grid-2">
        {/* Поточна інформація */}
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">Ваші бали</h2>
          </div>
          
          <div className="text-center">
            <div className="mb-3">
              <h3 className="text-success" style={{ fontSize: '3rem' }}>
                {profile?.loyalty_points || 0}
              </h3>
              <p>поточних балів</p>
            </div>
            
            <div className="alert alert-info">
              <strong>Як це працює:</strong>
              <ul style={{ textAlign: 'left', marginTop: '10px' }}>
                <li>За кожне обслуговування ви отримуєте бали</li>
                <li>1 гривня = 1 бал</li>
                <li>Бали можна використовувати для знижок</li>
                <li>Бали не мають терміну дії</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Статистика */}
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">Статистика</h2>
          </div>
          
          <div className="grid grid-2">
            <div className="text-center">
              <h4>Зароблено</h4>
              <p className="text-success">
                {transactions
                  .filter(t => t.transaction_type === 'earned')
                  .reduce((sum, t) => sum + t.points, 0)} балів
              </p>
            </div>
            <div className="text-center">
              <h4>Витрачено</h4>
              <p className="text-warning">
                {transactions
                  .filter(t => t.transaction_type === 'spent')
                  .reduce((sum, t) => sum + t.points, 0)} балів
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Історія транзакцій */}
      <div className="card">
        <div className="card-header">
          <h2 className="section-title">Історія транзакцій</h2>
        </div>
        
        {transactions.length > 0 ? (
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Тип</th>
                  <th>Кількість балів</th>
                  <th>Опис</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(transaction => (
                  <tr key={transaction.id}>
                    <td>{new Date(transaction.created_at).toLocaleDateString('uk-UA')}</td>
                    <td>{getTransactionTypeBadge(transaction.transaction_type)}</td>
                    <td>{transaction.points}</td>
                    <td>{transaction.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center">
            <p>У вас поки немає транзакцій</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoyaltyProgram; 