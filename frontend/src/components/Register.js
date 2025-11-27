import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import api from '../utils/api';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
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

    // Перевірка паролів
    if (formData.password !== formData.confirmPassword) {
      setError(t('passwords_dont_match', { uk: 'Паролі не співпадають', en: 'Passwords do not match' }));
      setLoading(false);
      return;
    }

    // Перевірка довжини пароля
    if (formData.password.length < 6) {
      setError(t('password_min_length', { uk: 'Пароль повинен містити мінімум 6 символів', en: 'Password must contain at least 6 characters' }));
      setLoading(false);
      return;
    }

    try {
      const response = await api.post('/api/auth/register/', {
        email: formData.email,
        password: formData.password
      });
      
      if (response.data.access) {
        login(response.data.access, response.data.user);
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Помилка реєстрації:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.response?.data?.email) {
        setError(t('user_exists', { uk: 'Користувач з такою поштою вже існує', en: 'User with this email already exists' }));
      } else if (error.response?.data?.password) {
        setError(error.response.data.password[0]);
      } else {
        setError(t('registration_error', { uk: 'Помилка реєстрації. Спробуйте ще раз.', en: 'Registration error. Try again.' }));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container" key={`register-${language}`}>
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
      <div className="register-form-container">
        <h1 className="register-title">{t('registration', { uk: 'РЕЄСТРАЦІЯ', en: 'REGISTRATION' })}</h1>
        
        <form onSubmit={handleSubmit} className="register-form">
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

          <div className="form-group">
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder={t('confirm_password_field', { uk: 'ПОВТОРИТИ ПАРОЛЬ', en: 'CONFIRM PASSWORD' })}
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
            className="register-button"
            disabled={loading}
          >
            {loading ? t('loading', { uk: 'Завантаження...', en: 'Loading...' }) : t('register', { uk: 'ЗАРЕЄСТРУВАТИСЯ', en: 'REGISTER' })}
          </button>
        </form>
      </div>

      {/* Секція входу */}
      <div className="login-section">
        <p className="login-question">{t('have_account', { uk: 'Є акаунт?', en: 'Have an account?' })}</p>
        <Link to="/login" className="login-link-button">
          {t('login', { uk: 'УВІЙТИ', en: 'LOGIN' })}
        </Link>
      </div>
    </div>
  );
};

export default Register; 