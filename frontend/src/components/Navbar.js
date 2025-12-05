import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import logo from '../assets/images/Flux_Dev_Simple_black_and_white_Minimalist_logo_for_a_car_serv_2.jpg'; // Логотип автомобіля з ключем
import userAvatar from '../assets/images/profile-icon-design-free-vector.jpg'; // Фото користувача
import LanguageSwitcher from './LanguageSwitcher';

const Navbar = () => {
  const { isAuthenticated, user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();


  const handleProfileClick = () => {
    if (isAuthenticated) {
      // Іконка профілю завжди веде в особистий кабінет
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Ліва частина - Логотип */}
        <div className="navbar-brand">
          <Link to="/" className="brand-link">
            <img src={logo} alt="СТО AutoServis" className="brand-logo-img" />
            <span className="brand-text">AutoServis</span>
          </Link>
        </div>

        {/* Центральна частина - Меню */}
        <ul className={`navbar-menu ${isAuthenticated && user?.is_staff ? 'admin-menu' : ''}`}>
          {!isAuthenticated || !user?.is_staff ? (
            <>
              <li>
                <Link to="/" className="nav-link">{t('home', translations.home)}</Link>
              </li>
              <li>
                <Link to="/services" className="nav-link">{t('services', translations.services)}</Link>
              </li>
              <li>
                <Link to={isAuthenticated ? "/appointment" : "/guest-appointment"} className="nav-link">{t('appointment', translations.appointment)}</Link>
              </li>
            </>
          ) : (
            <li>
              <Link to="/admin" className="nav-link">{t('admin_panel', translations.admin_panel)}</Link>
            </li>
          )}
        </ul>

        {/* Права частина - Кнопки авторизації або іконка профілю */}
        <div className="navbar-right">
          <LanguageSwitcher />
          {isAuthenticated ? (
            <div className="navbar-profile-icon" onClick={handleProfileClick}>
              <img src={userAvatar} alt="Особистий кабінет" className="navbar-profile-img" />
            </div>
          ) : (
            <div className="auth-buttons-navbar">
              <Link to="/login" className="nav-link">{t('login', translations.login)}</Link>
              <Link to="/register" className="nav-link">{t('register', translations.register)}</Link>
              <div className="navbar-profile-icon" onClick={handleProfileClick}>
                <img src={userAvatar} alt="Особистий кабінет" className="navbar-profile-img" />
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 