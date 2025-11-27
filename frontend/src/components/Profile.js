import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    phone: '',
    address: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/api/customers/profile/');
        setProfile(response.data);
        setFormData({
          phone: response.data.phone || '',
          address: response.data.address || ''
        });
      } catch (error) {
        console.error('Помилка завантаження профілю:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await api.put('/api/customers/update_profile/', formData);
      toast.success('Профіль успішно оновлено!');
      
      // Оновлюємо дані профілю
      const response = await api.get('/api/customers/profile/');
      setProfile(response.data);
    } catch (error) {
      toast.error('Помилка оновлення профілю');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center">Завантаження профілю...</div>;
  }

  return (
    <div>
      <h1 className="page-title">Редагування профілю</h1>
      
      <div className="grid grid-2">
        {/* Інформація про користувача */}
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">Особиста інформація</h2>
          </div>
          
          <div className="mb-3">
            <strong>Ім'я:</strong> {user?.first_name} {user?.last_name}
          </div>
          <div className="mb-3">
            <strong>Email:</strong> {user?.email}
          </div>
          <div className="mb-3">
            <strong>Логін:</strong> {user?.username}
          </div>
          <div className="mb-3">
            <strong>Бали лояльності:</strong> {profile?.loyalty_points || 0}
          </div>
          <div className="mb-3">
            <strong>Статус:</strong> {profile?.is_blocked ? 'Заблокований' : 'Активний'}
          </div>
        </div>

        {/* Форма редагування */}
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">Редагування контактних даних</h2>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="phone">Телефон:</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                className="form-control"
                value={formData.phone}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="address">Адреса:</label>
              <textarea
                id="address"
                name="address"
                className="form-control"
                value={formData.address}
                onChange={handleChange}
                rows="3"
              />
            </div>
            
            <button
              type="submit"
              className="btn btn-primary"
              disabled={saving}
            >
              {saving ? 'Збереження...' : 'Зберегти зміни'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile; 