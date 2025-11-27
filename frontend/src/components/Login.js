import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import api from '../utils/api';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const { language, t } = useLanguage();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Перевірка email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError(t('enter_valid_email', { uk: 'Введіть коректну email адресу', en: 'Enter a valid email address' }));
      setLoading(false);
      return;
    }

    // Перевірка пароля
    if (!formData.password) {
      setError(t('enter_password', { uk: 'Введіть пароль', en: 'Enter password' }));
      setLoading(false);
      return;
    }

    try {
      const response = await api.post('/api/auth/login/', formData);
      
      if (response.data.access) {
        login(response.data.access, response.data.user);
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Помилка входу:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError(t('login_error', { uk: 'Помилка входу. Перевірте ваші дані.', en: 'Login error. Check your credentials.' }));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container" key={`login-${language}`}>
      {/* Навігація назад */}
      <div className="back-navigation">
        <Link to="/" className="back-link">
          <span className="back-arrow">←</span>
          <div className="back-text">
            <span>{t('back', { uk: 'Повернутися', en: 'Back' })}</span>
            <span>{t('to_main', { uk: 'на головну', en: 'to main' })}</span>
            <span>{t('page', { uk: 'сторінку', en: 'page' })}</span>
          </div>
        </Link>
      </div>

      {/* Основна форма */}
      <div className="login-form-container">
        <h1 className="login-title">{t('authorization', { uk: 'АВТОРИЗАЦІЯ', en: 'AUTHORIZATION' })}</h1>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder={t('email', { uk: 'ПОШТА', en: 'EMAIL' })}
              className="form-input"
              required
            />
          </div>
          
          <div className="form-group">
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder={t('password_field', { uk: 'ПАРОЛЬ', en: 'PASSWORD' })}
              className="form-input"
              required
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? t('loading', { uk: 'Завантаження...', en: 'Loading...' }) : t('login', { uk: 'УВІЙТИ', en: 'LOGIN' })}
          </button>
        </form>
      </div>

      {/* Секція реєстрації */}
      <div className="registration-section">
        <p className="registration-question">{t('no_account', { uk: 'Немає акаунту?', en: 'No account?' })}</p>
        <Link to="/register" className="register-button">
          {t('register', { uk: 'ЗАРЕЄСТРУВАТИСЯ', en: 'REGISTER' })}
        </Link>
      </div>
    </div>
  );
};

export default Login; 