import axios from 'axios';

// Налаштування базового URL для API
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Інтерцептор для обробки помилок та токенів
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Токен застарів або недійсний
      console.error('Токен недійсний, перенаправляємо на логін');
      localStorage.removeItem('token');
      localStorage.removeItem('refresh');
      delete api.defaults.headers.common['Authorization'];
      
      // Перенаправляємо на логін
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Інтерцептор для встановлення токена та заголовків
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Додаємо заголовки для уникнення кешування
    config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
    config.headers['Pragma'] = 'no-cache';
    config.headers['Expires'] = '0';
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api; 