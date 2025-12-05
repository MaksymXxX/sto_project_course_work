import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';
import { useLanguage } from '../contexts/LanguageContext';
import './AdminPanel.css';

const AdminPanel = () => {
  const { language, t } = useLanguage();
  const [statistics, setStatistics] = useState(null);
  const [weeklySchedule, setWeeklySchedule] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);
  const [boxes, setBoxes] = useState([]);
  const [stoInfo, setStoInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('statistics');

  // Фільтри для записів
  const [appointmentFilters, setAppointmentFilters] = useState({
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

  const [showAppointmentFilters, setShowAppointmentFilters] = useState(false);

  // Стани для форм
  const [showServiceForm, setShowServiceForm] = useState(false);
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showBoxForm, setShowBoxForm] = useState(false);
  const [showStoInfoForm, setShowStoInfoForm] = useState(false);
  const [showStoInfoFormEn, setShowStoInfoFormEn] = useState(false);
  const [showFeaturedServicesForm, setShowFeaturedServicesForm] = useState(false);

  const [editingService, setEditingService] = useState(null);
  const [editingCategory, setEditingCategory] = useState(null);
  const [editingBox, setEditingBox] = useState(null);

  // Стани для деталей запису
  const [showAppointmentDetails, setShowAppointmentDetails] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);

  // Стани для редагування клієнта
  const [showCustomerEditForm, setShowCustomerEditForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [customerEditForm, setCustomerEditForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password_confirm: ''
  });

  // Форми
  const [serviceForm, setServiceForm] = useState({
    name: '',
    name_en: '',
    description: '',
    description_en: '',
    price: '',
    duration_minutes: '',
    category_id: '',
    is_active: true
  });

  const [categoryForm, setCategoryForm] = useState({
    name: '',
    name_en: '',
    description: '',
    description_en: '',
    order: ''
  });

  const [boxForm, setBoxForm] = useState({
    name: '',
    name_en: '',
    description: '',
    description_en: '',
    is_active: true,
    working_hours: {
      monday: { start: '08:00', end: '18:00' },
      tuesday: { start: '08:00', end: '18:00' },
      wednesday: { start: '08:00', end: '18:00' },
      thursday: { start: '08:00', end: '18:00' },
      friday: { start: '08:00', end: '18:00' },
      saturday: { start: '09:00', end: '15:00' },
      sunday: { start: '00:00', end: '00:00' }
    }
  });

  const [stoInfoForm, setStoInfoForm] = useState({
    name: '',
    description: '',
    motto: '',
    welcome_text: '',
    what_you_can_title: '',
    what_you_can_items: [''],
    address: '',
    email: '',
    working_hours: '',
    is_active: true
  });

  const [stoInfoFormEn, setStoInfoFormEn] = useState({
    name_en: '',
    description_en: '',
    motto_en: '',
    welcome_text_en: '',
    what_you_can_title_en: '',
    what_you_can_items_en: [''],
    address_en: '',
    email: '',
    working_hours_en: '',
    is_active: true
  });

  // Debounce для фільтрів записів
  useEffect(() => {
    if (activeTab !== 'appointments') return;

    const timeoutId = setTimeout(() => {
      const params = new URLSearchParams();
      if (appointmentFilters.date_from) params.append('date_from', appointmentFilters.date_from);
      if (appointmentFilters.date_to) params.append('date_to', appointmentFilters.date_to);
      if (appointmentFilters.box_id) params.append('box_id', appointmentFilters.box_id);
      if (appointmentFilters.service_id) params.append('service_id', appointmentFilters.service_id);
      if (appointmentFilters.status) params.append('status', appointmentFilters.status);
      if (appointmentFilters.customer_name) params.append('customer_name', appointmentFilters.customer_name);
      if (appointmentFilters.time_from) params.append('time_from', appointmentFilters.time_from);
      if (appointmentFilters.time_to) params.append('time_to', appointmentFilters.time_to);
      if (appointmentFilters.price_min) params.append('price_min', appointmentFilters.price_min);
      if (appointmentFilters.price_max) params.append('price_max', appointmentFilters.price_max);

      api.get(`/api/admin/appointments/?${params.toString()}&language=${language}`)
        .then(response => {
          setAppointments(response.data || []);
        })
        .catch(error => {
          console.error('Помилка завантаження записів:', error);
          toast.error(t('load_appointments_error'));
        });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [appointmentFilters, language, activeTab, t]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchWeeklySchedule = useCallback(async () => {
    try {
      const response = await api.get(`/api/admin/weekly_schedule/?language=${language}`);
      setWeeklySchedule(response.data);
    } catch (error) {
      console.error('Помилка завантаження розкладу:', error);
      toast.error(t('load_schedule_error'));
    }
  }, [language, t]);

  const handleAppointmentFilterChange = (name, value) => {
    setAppointmentFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const clearAppointmentFilters = () => {
    setAppointmentFilters({
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
    return Object.values(appointmentFilters).filter(value => value !== '').length;
  };

  const formatDate = (dateString) => {
    if (!dateString) return t('not_specified');
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        console.error('Invalid date string:', dateString);
        return t('invalid_date');
      }
      return date.toLocaleDateString(language === 'en' ? 'en-US' : 'uk-UA');
    } catch (error) {
      console.error('Error formatting date:', error, dateString);
      return t('formatting_error');
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return t('not_specified');
    try {
      const time = new Date(`2000-01-01T${timeString}`);
      if (isNaN(time.getTime())) {
        console.error('Invalid time string:', timeString);
        return t('invalid_time');
      }
      return time.toLocaleTimeString(language === 'en' ? 'en-US' : 'uk-UA', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      console.error('Error formatting time:', error, timeString);
      return t('formatting_error');
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return t('pending');
      case 'confirmed':
        return t('confirmed');
      case 'completed':
        return t('completed');
      case 'cancelled':
        return t('cancelled_by_client');
      case 'cancelled_by_admin':
        return t('cancelled_by_admin');
      default:
        return status;
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'badge badge-warning';
      case 'confirmed':
        return 'badge badge-info';
      case 'completed':
        return 'badge badge-success';
      case 'cancelled':
        return 'badge badge-secondary';
      case 'cancelled_by_admin':
        return 'badge badge-danger';
      default:
        return 'badge badge-secondary';
    }
  };

  const getDayName = (dayName) => {
    // Якщо назва дня вже переведена (приходить з бекенду), повертаємо як є
    if (dayName === t('monday') || dayName === t('tuesday') || dayName === t('wednesday') ||
      dayName === t('thursday') || dayName === t('friday') || dayName === t('saturday') ||
      dayName === t('sunday')) {
      return dayName;
    }

    // Інакше переводимо з української або англійської
    const dayMap = {
      'Понеділок': t('monday'),
      'Вівторок': t('tuesday'),
      'Середа': t('wednesday'),
      'Четвер': t('thursday'),
      'П\'ятниця': t('friday'),
      'Субота': t('saturday'),
      'Неділя': t('sunday'),
      'Monday': t('monday'),
      'Tuesday': t('tuesday'),
      'Wednesday': t('wednesday'),
      'Thursday': t('thursday'),
      'Friday': t('friday'),
      'Saturday': t('saturday'),
      'Sunday': t('sunday')
    };
    return dayMap[dayName] || dayName;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsResponse, customersResponse, servicesResponse, categoriesResponse, boxesResponse, stoInfoResponse] = await Promise.all([
          api.get('/api/admin/statistics/'),
          api.get(`/api/admin/customer_management/?language=${language}`),
          api.get(`/api/admin/services_management/?language=${language}`),
          api.get(`/api/admin/categories_management/?language=${language}`),
          api.get(`/api/admin/boxes_management/?language=${language}`),
          api.get(`/api/admin/home_page_management/?language=${language}`)
        ]);


        setStatistics(statsResponse.data);
        setCustomers(customersResponse.data);
        setServices(servicesResponse.data);
        setCategories(categoriesResponse.data);
        setBoxes(boxesResponse.data);
        setStoInfo(stoInfoResponse.data);

        // Завантажуємо розклад тижня
        fetchWeeklySchedule();
      } catch (error) {
        console.error('Помилка завантаження адміністративних даних:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [language, fetchWeeklySchedule]);

  const handleBlockCustomer = async (customerId) => {
    try {
      await api.post(`/api/admin/${customerId}/block_customer/`);
      toast.success(t('customer_blocked'));
      const response = await api.get(`/api/admin/customer_management/?language=${language}`);
      setCustomers(response.data);
    } catch (error) {
      toast.error(t('block_customer_error'));
    }
  };

  const handleUnblockCustomer = async (customerId) => {
    try {
      await api.post(`/api/admin/${customerId}/unblock_customer/`);
      toast.success(t('customer_unblocked'));
      const response = await api.get(`/api/admin/customer_management/?language=${language}`);
      setCustomers(response.data);
    } catch (error) {
      toast.error(t('unblock_customer_error'));
    }
  };

  const handleEditCustomer = (customer) => {
    setEditingCustomer(customer);
    setCustomerEditForm({
      first_name: customer.user.first_name || '',
      last_name: customer.user.last_name || '',
      email: customer.user.email || '',
      password: '',
      password_confirm: ''
    });
    setShowCustomerEditForm(true);
  };

  const handleCustomerEditChange = (e) => {
    setCustomerEditForm({
      ...customerEditForm,
      [e.target.name]: e.target.value
    });
  };

  const handleUpdateCustomer = async (e) => {
    e.preventDefault();

    // Валідація пароля
    if (customerEditForm.password || customerEditForm.password_confirm) {
      if (!customerEditForm.password) {
        toast.error(t('please_enter_password'));
        return;
      }
      if (!customerEditForm.password_confirm) {
        toast.error(t('please_confirm_password'));
        return;
      }
      if (customerEditForm.password !== customerEditForm.password_confirm) {
        toast.error(t('passwords_dont_match'));
        return;
      }
      if (customerEditForm.password.length < 8) {
        toast.error(t('password_min_length'));
        return;
      }
    }

    try {
      const formData = new FormData();
      formData.append('first_name', customerEditForm.first_name);
      formData.append('last_name', customerEditForm.last_name);
      formData.append('email', customerEditForm.email);

      if (customerEditForm.password) {
        formData.append('password', customerEditForm.password);
      }

      await api.put(`/api/admin/${editingCustomer.id}/update_customer/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Оновлюємо список клієнтів
      const response = await api.get(`/api/admin/customer_management/?language=${language}`);
      setCustomers(response.data);

      setShowCustomerEditForm(false);
      setEditingCustomer(null);
      setCustomerEditForm({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        password_confirm: ''
      });

      toast.success(t('customer_data_updated'));
    } catch (error) {
      console.error('Помилка оновлення клієнта:', error);
      if (error.response?.data?.error) {
        toast.error(error.response.data.error);
      } else {
        toast.error('Помилка оновлення клієнта');
      }
    }
  };

  const handleConfirmAppointment = async (appointmentId) => {
    try {
      await api.post(`/api/appointments/${appointmentId}/confirm/`);
      toast.success(t('appointment_confirmed'));
      // Оновлення відбудеться автоматично через useEffect
    } catch (error) {
      toast.error(t('confirm_appointment_error'));
    }
  };

  const handleCompleteAppointment = async (appointmentId) => {
    try {
      await api.post(`/api/appointments/${appointmentId}/complete/`);
      toast.success(t('service_completed'));
      // Оновлення відбудеться автоматично через useEffect
    } catch (error) {
      toast.error(t('complete_service_error'));
    }
  };

  const handleCancelAppointment = async (appointmentId) => {
    try {
      await api.post(`/api/admin/${appointmentId}/cancel_appointment/`);
      toast.success(t('appointment_cancelled_admin'));
      // Оновлення відбудеться автоматично через useEffect
    } catch (error) {
      toast.error(t('cancel_appointment_error'));
    }
  };

  const handleViewAppointmentDetails = async (appointmentId) => {
    try {
      const response = await api.get(`/api/admin/${appointmentId}/appointment_details/?language=${language}`);
      setSelectedAppointment(response.data);
      setShowAppointmentDetails(true);
    } catch (error) {
      toast.error(t('load_appointment_details_error'));
    }
  };

  // Управління послугами
  const handleCreateService = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/admin/create_service/', serviceForm);
      toast.success(t('service_created_success'));
      setShowServiceForm(false);
      setServiceForm({
        name: '',
        name_en: '',
        description: '',
        description_en: '',
        price: '',
        duration_minutes: '',
        category_id: '',
        is_active: true
      });
      const response = await api.get(`/api/admin/services_management/?language=${language}`);
      setServices(response.data);
    } catch (error) {
      toast.error(t('service_create_error'));
    }
  };

  const handleUpdateService = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/api/admin/${editingService.id}/update_service/`, serviceForm);
      toast.success(t('service_updated_success'));
      setShowServiceForm(false);
      setEditingService(null);
      setServiceForm({
        name: '',
        name_en: '',
        description: '',
        description_en: '',
        price: '',
        duration_minutes: '',
        category_id: '',
        is_active: true
      });
      const response = await api.get(`/api/admin/services_management/?language=${language}`);
      setServices(response.data);
    } catch (error) {
      toast.error(t('service_update_error'));
    }
  };

  const handleDeleteService = async (serviceId) => {
    if (window.confirm('Ви впевнені, що хочете видалити цю послугу?')) {
      try {
        await api.delete(`/api/admin/${serviceId}/delete_service/`);
        toast.success(t('service_deleted_success'));
        const response = await api.get(`/api/admin/services_management/?language=${language}`);
        setServices(response.data);
      } catch (error) {
        toast.error(t('service_delete_error'));
      }
    }
  };

  const handleToggleServiceStatus = async (serviceId) => {
    try {
      await api.post(`/api/admin/${serviceId}/toggle_service_status/`);
      const response = await api.get(`/api/admin/services_management/?language=${language}`);
      setServices(response.data);
    } catch (error) {
      toast.error(t('service_status_toggle_error'));
    }
  };



  const editService = async (service) => {
    try {
      // Отримуємо повні дані послуги для редагування
      const response = await api.get(`/api/admin/${service.id}/get_service_for_edit/`);
      const serviceData = response.data;

      setEditingService(serviceData);
      setServiceForm({
        name: serviceData.name || '',
        name_en: serviceData.name_en || '',
        description: serviceData.description || '',
        description_en: serviceData.description_en || '',
        price: serviceData.price,
        duration_minutes: serviceData.duration_minutes,
        category_id: serviceData.category?.id || '',
        is_active: serviceData.is_active
      });
      setShowServiceForm(true);
    } catch (error) {
      toast.error(t('service_update_error'));
    }
  };

  // Управління категоріями
  const handleCreateCategory = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/admin/create_category/', categoryForm);
      toast.success(t('category_created_success'));
      setShowCategoryForm(false);
      setCategoryForm({
        name: '',
        name_en: '',
        description: '',
        description_en: '',
        order: ''
      });
      const response = await api.get(`/api/admin/categories_management/?language=${language}`);
      setCategories(response.data);
    } catch (error) {
      toast.error(t('category_create_error'));
    }
  };

  const handleUpdateCategory = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/api/admin/${editingCategory.id}/update_category/`, categoryForm);
      toast.success(t('category_updated_success'));
      setShowCategoryForm(false);
      setEditingCategory(null);
      setCategoryForm({
        name: '',
        name_en: '',
        description: '',
        description_en: '',
        order: ''
      });
      const response = await api.get(`/api/admin/categories_management/?language=${language}`);
      setCategories(response.data);
    } catch (error) {
      toast.error(t('category_update_error'));
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (window.confirm('Ви впевнені, що хочете видалити цю категорію? Всі послуги в цій категорії та записи на ці послуги також будуть видалені.')) {
      try {
        await api.delete(`/api/admin/${categoryId}/delete_category/`);
        toast.success(t('category_deleted_success'));

        // Оновлюємо списки категорій та послуг
        const [categoriesResponse, servicesResponse] = await Promise.all([
          api.get(`/api/admin/categories_management/?language=${language}`),
          api.get(`/api/admin/services_management/?language=${language}`)
        ]);
        setCategories(categoriesResponse.data);
        setServices(servicesResponse.data);
      } catch (error) {
        toast.error(t('category_delete_error'));
      }
    }
  };

  const editCategory = (category) => {
    setEditingCategory(category);
    setCategoryForm({
      name: category.name || '',
      name_en: category.name_en || '',
      description: category.description || '',
      description_en: category.description_en || '',
      order: category.order
    });
    setShowCategoryForm(true);
  };

  // Управління боксами
  const handleCreateBox = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/admin/create_box/', boxForm);
      toast.success(t('box_created_success'));
      setShowBoxForm(false);
      setBoxForm({
        name: '',
        name_en: '',
        description: '',
        description_en: '',
        is_active: true,
        working_hours: {
          monday: { start: '08:00', end: '18:00' },
          tuesday: { start: '08:00', end: '18:00' },
          wednesday: { start: '08:00', end: '18:00' },
          thursday: { start: '08:00', end: '18:00' },
          friday: { start: '08:00', end: '18:00' },
          saturday: { start: '09:00', end: '15:00' },
          sunday: { start: '00:00', end: '00:00' }
        }
      });
      const response = await api.get(`/api/admin/boxes_management/?language=${language}`);
      setBoxes(response.data);
    } catch (error) {
      toast.error(t('box_create_error'));
    }
  };

  const handleUpdateBox = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/api/admin/${editingBox.id}/update_box/`, boxForm);
      toast.success(t('box_updated_success'));
      setShowBoxForm(false);
      setEditingBox(null);
      setBoxForm({
        name: '',
        name_en: '',
        description: '',
        description_en: '',
        is_active: true,
        working_hours: {
          monday: { start: '08:00', end: '18:00' },
          tuesday: { start: '08:00', end: '18:00' },
          wednesday: { start: '08:00', end: '18:00' },
          thursday: { start: '08:00', end: '18:00' },
          friday: { start: '08:00', end: '18:00' },
          saturday: { start: '09:00', end: '15:00' },
          sunday: { start: '00:00', end: '00:00' }
        }
      });
      const response = await api.get(`/api/admin/boxes_management/?language=${language}`);
      setBoxes(response.data);
    } catch (error) {
      toast.error(t('box_update_error'));
    }
  };

  const handleDeleteBox = async (boxId) => {
    if (window.confirm('Ви впевнені, що хочете видалити цей бокс? Всі записи на цей бокс також будуть видалені.')) {
      try {
        await api.delete(`/api/admin/${boxId}/delete_box/`);
        toast.success(t('box_deleted_success'));
        const response = await api.get(`/api/admin/boxes_management/?language=${language}`);
        setBoxes(response.data);
      } catch (error) {
        toast.error(t('box_delete_error'));
      }
    }
  };

  const handleToggleBoxStatus = async (boxId) => {
    try {
      await api.post(`/api/admin/${boxId}/toggle_box_status/`);
      toast.success(t('box_status_toggle_success'));
      const response = await api.get(`/api/admin/boxes_management/?language=${language}`);
      setBoxes(response.data);
    } catch (error) {
      toast.error(t('box_status_toggle_error'));
    }
  };

  const editBox = (box) => {
    setEditingBox(box);
    setBoxForm({
      name: box.name || '',
      name_en: box.name_en || '',
      description: box.description || '',
      description_en: box.description_en || '',
      is_active: box.is_active,
      working_hours: box.working_hours || {
        monday: { start: '08:00', end: '18:00' },
        tuesday: { start: '08:00', end: '18:00' },
        wednesday: { start: '08:00', end: '18:00' },
        thursday: { start: '08:00', end: '18:00' },
        friday: { start: '08:00', end: '18:00' },
        saturday: { start: '09:00', end: '15:00' },
        sunday: { start: '00:00', end: '00:00' }
      }
    });
    setShowBoxForm(true);
  };

  // Управління головною сторінкою
  const handleUpdateStoInfo = async (e) => {
    e.preventDefault();
    try {
      // Фільтруємо порожні пункти перед відправкою
      const formData = {
        ...stoInfoForm,
        what_you_can_items: stoInfoForm.what_you_can_items.filter(item => item.trim() !== '')
      };

      await api.post('/api/admin/update_home_page/', formData);
      toast.success('Інформацію про СТО оновлено');
      setShowStoInfoForm(false);

      // Оновлюємо дані після успішного збереження
      const stoInfoResponse = await api.get(`/api/admin/home_page_management/?language=${language}`);
      setStoInfo(stoInfoResponse.data);
    } catch (error) {
      if (error.response) {
        toast.error(`Помилка оновлення: ${error.response.data.error || error.response.data}`);
      } else {
        toast.error('Помилка оновлення інформації про СТО');
      }
    }
  };

  const handleUpdateStoInfoEn = async (e) => {
    e.preventDefault();
    try {
      // Фільтруємо порожні пункти перед відправкою
      const formData = {
        ...stoInfoFormEn,
        what_you_can_items_en: stoInfoFormEn.what_you_can_items_en.filter(item => item.trim() !== '')
      };

      await api.post('/api/admin/update_home_page/', formData);
      toast.success('English version of STO information updated');
      setShowStoInfoFormEn(false);

      // Оновлюємо дані після успішного збереження
      const stoInfoResponse = await api.get(`/api/admin/home_page_management/?language=${language}`);
      setStoInfo(stoInfoResponse.data);
    } catch (error) {
      if (error.response) {
        toast.error(`Update error: ${error.response.data.error || error.response.data}`);
      } else {
        toast.error('Error updating English STO information');
      }
    }
  };

  if (loading) {
    return <div className="text-center">Завантаження адміністративної панелі...</div>;
  }

  return (
    <div key={`admin-panel-${language}`}>
      <h1 className="page-title">{t('admin_panel_title')}</h1>

      {/* Навігація по вкладках */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'statistics' ? 'active' : ''}`}
          onClick={() => setActiveTab('statistics')}
        >
          {t('statistics')}
        </button>
        <button
          className={`tab ${activeTab === 'customers' ? 'active' : ''}`}
          onClick={() => setActiveTab('customers')}
        >
          {t('customers')}
        </button>
        <button
          className={`tab ${activeTab === 'appointments' ? 'active' : ''}`}
          onClick={() => setActiveTab('appointments')}
        >
          {t('appointments')}
        </button>
        <button
          className={`tab ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => setActiveTab('services')}
        >
          {t('services')}
        </button>

        <button
          className={`tab ${activeTab === 'categories' ? 'active' : ''}`}
          onClick={() => setActiveTab('categories')}
        >
          {t('categories')}
        </button>
        <button
          className={`tab ${activeTab === 'boxes' ? 'active' : ''}`}
          onClick={() => setActiveTab('boxes')}
        >
          {t('boxes')}
        </button>
        <button
          className={`tab ${activeTab === 'homepage' ? 'active' : ''}`}
          onClick={() => setActiveTab('homepage')}
        >
          {t('homepage')}
        </button>
      </div>

      {/* Статистика */}
      {activeTab === 'statistics' && statistics && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('statistics')}</h2>
          </div>

          <div className="grid grid-4">
            <div className="text-center">
              <h3>{statistics.total_appointments}</h3>
              <p>{t('total_appointments')}</p>
            </div>
            <div className="text-center">
              <h3>{statistics.pending_appointments}</h3>
              <p>{t('pending_appointments')}</p>
            </div>
            <div className="text-center">
              <h3>{statistics.completed_appointments}</h3>
              <p>{t('completed_appointments')}</p>
            </div>
            <div className="text-center">
              <h3>{statistics.total_customers}</h3>
              <p>{t('total_customers')}</p>
            </div>
            <div className="text-center">
              <h3>{statistics.blocked_customers}</h3>
              <p>{t('blocked_customers')}</p>
            </div>
            <div className="text-center">
              <h3>{statistics.monthly_appointments}</h3>
              <p>{t('monthly_appointments')}</p>
            </div>
            <div className="text-center">
              <h3>{statistics.total_revenue} {language === 'en' ? 'UAH' : 'грн'}</h3>
              <p>{t('total_revenue')}</p>
            </div>
            <div className="text-center">
              <h3>{statistics.services_count}</h3>
              <p>{t('active_services')}</p>
            </div>
          </div>
        </div>
      )}

      {/* Розклад на цей тиждень */}
      {activeTab === 'statistics' && weeklySchedule && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('weekly_schedule')}</h2>
            <p className="text-muted">
              {new Date(weeklySchedule.week_start).toLocaleDateString(language === 'en' ? 'en-US' : 'uk-UA', {
                year: 'numeric',
                month: language === 'en' ? 'short' : 'short',
                day: 'numeric'
              })} - {new Date(weeklySchedule.week_end).toLocaleDateString(language === 'en' ? 'en-US' : 'uk-UA', {
                year: 'numeric',
                month: language === 'en' ? 'short' : 'short',
                day: 'numeric'
              })}
            </p>
          </div>

          <div className="weekly-schedule">
            {Object.values(weeklySchedule.schedule).map((day, index) => (
              <div key={day.date} className="schedule-day">
                <div className="day-header">
                  <h3>{getDayName(day.day_name)}</h3>
                  <span className="date">{new Date(day.date).toLocaleDateString(language === 'en' ? 'en-US' : 'uk-UA', {
                    day: 'numeric',
                    month: language === 'en' ? 'short' : 'short'
                  })}</span>
                </div>

                <div className="boxes-schedule">
                  {Object.values(day.boxes_schedule).map((boxSchedule) => (
                    <div key={boxSchedule.box_id} className="box-schedule">
                      <div className="box-header">
                        <h4>{boxSchedule.box_name}</h4>
                        <span className="appointments-count">
                          {boxSchedule.appointments.length} {t('appointments_count')}
                        </span>
                      </div>

                      <div className="appointments-list">
                        {boxSchedule.appointments.length === 0 ? (
                          <div className="no-appointments">
                            <p>{t('free')}</p>
                          </div>
                        ) : (
                          boxSchedule.appointments.map(appointment => (
                            <div key={appointment.id} className={`appointment-card ${appointment.status}`}>
                              <div className="appointment-time">
                                <strong>{appointment.time}</strong>
                              </div>
                              <div className="appointment-details">
                                <div className="service-name">{appointment.service_name}</div>
                                <div className="customer-name">{appointment.customer_name}</div>
                                <div className="price">
                                  {appointment.total_price} {language === 'en' ? 'UAH' : 'грн'}
                                  {(() => {
                                    // Тут потрібно було б передавати оригінальну ціну послуги
                                    // Поки що просто показуємо фінальну ціну
                                    return null;
                                  })()}
                                </div>
                              </div>
                              <div className="appointment-status">
                                <span className={`badge ${getStatusBadgeClass(appointment.status)}`}>
                                  {appointment.status_text}
                                </span>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Управління клієнтами */}
      {activeTab === 'customers' && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('customer_management')}</h2>
          </div>

          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>{t('client')}</th>
                  <th>Email</th>
                  <th>{t('status')}</th>
                  <th>{t('actions')}</th>
                </tr>
              </thead>
              <tbody>
                {customers.map(customer => (
                  <tr key={customer.id}>
                    <td>{customer.user.first_name} {customer.user.last_name}</td>
                    <td>{customer.user.email}</td>
                    <td>
                      {customer.is_blocked ?
                        <span className="badge badge-danger">{t('blocked')}</span> :
                        <span className="badge badge-success">{t('active')}</span>
                      }
                    </td>
                    <td>
                      <div className="btn-group">
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handleEditCustomer(customer)}
                          style={{ marginRight: '5px' }}
                        >
                          {t('edit')}
                        </button>
                        {customer.is_blocked ? (
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() => handleUnblockCustomer(customer.id)}
                          >
                            {t('unblock_user')}
                          </button>
                        ) : (
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleBlockCustomer(customer.id)}
                          >
                            {t('block_user')}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Управління записами */}
      {activeTab === 'appointments' && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('appointments_management')}</h2>
            <div className="filters-container">
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setShowAppointmentFilters(true)}
              >
                {getActiveFiltersCount() > 0 ? `${t('filters')} (${getActiveFiltersCount()})` : t('filters')}
              </button>
              <button
                className="btn btn-outline-secondary btn-sm"
                onClick={clearAppointmentFilters}
                disabled={getActiveFiltersCount() === 0}
              >
                {t('clear_filters')}
              </button>
            </div>
          </div>

          <div className="table-responsive">
            {!Array.isArray(appointments) || appointments.length === 0 ? (
              <div className="text-center p-3">
                <p>{!Array.isArray(appointments) ? t('loading_appointments') : t('no_appointments_found')}</p>
              </div>
            ) : (
              <table className="table" key={`appointments-table-${language}`}>
                <thead>
                  <tr>
                    <th>{t('client')}</th>
                    <th>{t('service')}</th>
                    <th>{t('box_name')}</th>
                    <th>{t('date')}</th>
                    <th>{t('time')}</th>
                    <th>{t('status')}</th>
                    <th>{t('cost')}</th>
                    <th>{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map(appointment => (
                    <tr key={appointment.id}>
                      <td>
                        {appointment.customer ?
                          `${appointment.customer.user?.first_name || ''} ${appointment.customer.user?.last_name || ''}`.trim() ||
                          appointment.guest_name :
                          appointment.guest_name
                        }
                      </td>
                      <td>{appointment.service?.get_name ? appointment.service.get_name(language) : appointment.service?.name}</td>
                      <td>{appointment.box?.get_name ? appointment.box.get_name(language) : appointment.box?.name}</td>
                      <td>{formatDate(appointment.appointment_date)}</td>
                      <td>{formatTime(appointment.appointment_time)}</td>
                      <td>
                        <span className={getStatusBadgeClass(appointment.status)}>
                          {getStatusText(appointment.status)}
                        </span>
                      </td>
                      <td>
                        {appointment.total_price} {language === 'en' ? 'UAH' : 'грн'}
                        {(() => {
                          const selectedService = appointment.service;
                          if (selectedService && selectedService.price !== appointment.total_price) {
                            const discountAmount = selectedService.price - appointment.total_price;
                            const discountPercentage = (discountAmount / selectedService.price) * 100;
                            return (
                              <span className="discount-applied">
                                {' '}({t('discount')} {discountPercentage.toFixed(1)}%)
                              </span>
                            );
                          }
                          return null;
                        })()}
                      </td>
                      <td>
                        {appointment.status === 'pending' && (
                          <button
                            className="btn btn-info btn-sm"
                            onClick={() => handleConfirmAppointment(appointment.id)}
                          >
                            {t('confirm')}
                          </button>
                        )}
                        {appointment.status === 'confirmed' && (
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() => handleCompleteAppointment(appointment.id)}
                          >
                            {t('complete')}
                          </button>
                        )}
                        {(appointment.status === 'pending' || appointment.status === 'confirmed') && (
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleCancelAppointment(appointment.id)}
                          >
                            {t('cancel')}
                          </button>
                        )}
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handleViewAppointmentDetails(appointment.id)}
                        >
                          {t('details')}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Управління послугами */}
      {activeTab === 'services' && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('services_management')}</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowServiceForm(true)}
            >
              {t('add_service')}
            </button>
          </div>

          <div className="table-responsive">
            <table className="table" key={`services-table-${language}`}>
              <thead>
                <tr>
                  <th>{t('service_name')}</th>
                  <th>{t('service_category')}</th>
                  <th>{t('service_price')}</th>
                  <th>{t('service_duration')}</th>
                  <th>{t('service_status')}</th>
                  <th>{t('service_actions')}</th>
                </tr>
              </thead>
              <tbody>
                {services.map(service => (
                  <tr key={service.id}>
                    <td>{service.name}</td>
                    <td>{service.category?.name || t('not_specified')}</td>
                    <td>{service.price} {language === 'en' ? 'UAH' : 'грн'}</td>
                    <td>{service.duration_minutes} {language === 'en' ? 'min' : 'хв'}</td>
                    <td>
                      <span className={`badge badge-${service.is_active ? 'success' : 'danger'}`}>
                        {service.is_active ? t('service_active') : t('service_inactive')}
                      </span>
                    </td>
                    <td>
                      <div className="btn-group">
                        <button
                          className="btn btn-info btn-sm"
                          onClick={() => editService(service)}
                        >
                          {t('service_edit')}
                        </button>
                        <button
                          className={`btn btn-sm ${service.is_active ? 'btn-warning' : 'btn-success'}`}
                          onClick={() => handleToggleServiceStatus(service.id)}
                        >
                          {service.is_active ? t('service_deactivate') : t('service_activate')}
                        </button>

                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDeleteService(service.id)}
                        >
                          {t('service_delete')}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Управління категоріями */}
      {activeTab === 'categories' && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('categories_management')}</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowCategoryForm(true)}
            >
              {t('add_category')}
            </button>
          </div>

          <div className="table-responsive">
            <table className="table" key={`categories-table-${language}`}>
              <thead>
                <tr>
                  <th>{t('category_name')}</th>
                  <th>{t('category_description')}</th>
                  <th>{t('category_order')}</th>
                  <th>{t('category_actions')}</th>
                </tr>
              </thead>
              <tbody>
                {categories.map(category => (
                  <tr key={category.id}>
                    <td>{category.get_name ? category.get_name(language) : category.name}</td>
                    <td>{category.get_description ? category.get_description(language) : category.description}</td>
                    <td>{category.order}</td>
                    <td>
                      <div className="btn-group">
                        <button
                          className="btn btn-info btn-sm"
                          onClick={() => editCategory(category)}
                        >
                          {t('category_edit')}
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDeleteCategory(category.id)}
                        >
                          {t('category_delete')}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Управління боксами */}
      {activeTab === 'boxes' && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('boxes_management')}</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowBoxForm(true)}
            >
              {t('add_box')}
            </button>
          </div>

          <div className="table-responsive">
            <table className="table" key={`boxes-table-${language}`}>
              <thead>
                <tr>
                  <th>{t('box_name')}</th>
                  <th>{t('box_description')}</th>
                  <th>{t('box_status')}</th>
                  <th>{t('box_actions')}</th>
                </tr>
              </thead>
              <tbody>
                {boxes.map(box => (
                  <tr key={box.id}>
                    <td>{box.get_name ? box.get_name(language) : box.name}</td>
                    <td>{box.get_description ? box.get_description(language) : box.description}</td>
                    <td>
                      <span className={`badge badge-${box.is_active ? 'success' : 'danger'}`}>
                        {box.is_active ? t('box_active') : t('box_inactive')}
                      </span>
                    </td>
                    <td>
                      <div className="btn-group">
                        <button
                          className="btn btn-info btn-sm"
                          onClick={() => editBox(box)}
                        >
                          {t('box_edit')}
                        </button>
                        <button
                          className="btn btn-warning btn-sm"
                          onClick={() => handleToggleBoxStatus(box.id)}
                        >
                          {box.is_active ? t('box_deactivate') : t('box_activate')}
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDeleteBox(box.id)}
                        >
                          {t('box_delete')}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Управління головною сторінкою */}
      {activeTab === 'homepage' && (
        <div className="card">
          <div className="card-header">
            <h2 className="section-title">{t('homepage_management')}</h2>
            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={() => {
                  if (stoInfo) {
                    setStoInfoForm({
                      name: stoInfo.name,
                      description: stoInfo.description,
                      motto: stoInfo.motto,
                      welcome_text: stoInfo.welcome_text,
                      what_you_can_title: stoInfo.what_you_can_title,
                      what_you_can_items: stoInfo.what_you_can_items && stoInfo.what_you_can_items.length > 0
                        ? stoInfo.what_you_can_items
                        : [''],
                      address: stoInfo.address,
                      phone: stoInfo.phone,
                      email: stoInfo.email,
                      working_hours: stoInfo.working_hours,
                      is_active: stoInfo.is_active
                    });
                  }
                  setShowStoInfoForm(true);
                }}
              >
                {t('edit_info_ukrainian')}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  if (stoInfo) {
                    setStoInfoFormEn({
                      name_en: stoInfo.name_en || '',
                      description_en: stoInfo.description_en || '',
                      motto_en: stoInfo.motto_en || '',
                      welcome_text_en: stoInfo.welcome_text_en || '',
                      what_you_can_title_en: stoInfo.what_you_can_title_en || '',
                      what_you_can_items_en: stoInfo.what_you_can_items_en && stoInfo.what_you_can_items_en.length > 0
                        ? stoInfo.what_you_can_items_en
                        : [''],
                      address_en: stoInfo.address_en || '',
                      phone: stoInfo.phone,
                      email: stoInfo.email,
                      working_hours_en: stoInfo.working_hours_en || '',
                      is_active: stoInfo.is_active
                    });
                  }
                  setShowStoInfoFormEn(true);
                }}
              >
                {t('edit_info_english')}
              </button>
              <button
                className="btn btn-info"
                onClick={() => setShowFeaturedServicesForm(true)}
              >
                {t('manage_featured_services')}
              </button>
            </div>
          </div>

          {stoInfo && (
            <div className="sto-info-preview">
              <h3>{t('current_sto_info')}</h3>
              <div className="info-grid">
                <div>
                  <strong>{t('sto_name_label')}</strong>
                  <span className="text-content">{stoInfo.name}</span>
                </div>
                <div>
                  <strong>{t('sto_motto_label')}</strong>
                  <span className="text-content">{stoInfo.motto}</span>
                </div>
                <div>
                  <strong>{t('sto_address_label')}</strong>
                  <span className="text-content">{stoInfo.address}</span>
                </div>
                <div>
                  <strong>{t('sto_phone_label')}</strong>
                  <span className="text-content">{stoInfo.phone}</span>
                </div>
                <div>
                  <strong>{t('sto_email_label')}</strong>
                  <span className="text-content">{stoInfo.email}</span>
                </div>
                <div>
                  <strong>{t('sto_working_hours_label')}</strong>
                  <span className="text-content">{stoInfo.working_hours}</span>
                </div>
              </div>
              <div>
                <strong>{t('sto_description_label')}</strong>
                <p className="text-content">{stoInfo.description}</p>
              </div>
              <div>
                <strong>{t('sto_welcome_text_label')}</strong>
                <p className="text-content">{stoInfo.welcome_text}</p>
              </div>
              <div>
                <strong>{stoInfo.what_you_can_title || t('sto_what_you_can_label')}</strong>
                <ul>
                  {stoInfo.what_you_can_items.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Модальне вікно для форми послуги */}
      {showServiceForm && (
        <div className="modal-overlay">
          <div className="modal" key={`service-form-${language}`}>
            <div className="modal-header">
              <h3>{editingService ? t('edit_service') : t('add_service')}</h3>
              <button
                className="btn btn-close"
                onClick={() => {
                  setShowServiceForm(false);
                  setEditingService(null);
                  setServiceForm({
                    name: '',
                    name_en: '',
                    description: '',
                    description_en: '',
                    price: '',
                    duration_minutes: '',
                    category_id: '',
                    is_active: true
                  });
                }}
              >
                ×
              </button>
            </div>
            <form onSubmit={editingService ? handleUpdateService : handleCreateService}>
              <div className="form-group">
                <label>{t('service_name_label')} (Українська)</label>
                <input
                  type="text"
                  value={serviceForm.name}
                  onChange={(e) => setServiceForm({ ...serviceForm, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('service_name_label')} (English)</label>
                <input
                  type="text"
                  value={serviceForm.name_en}
                  onChange={(e) => setServiceForm({ ...serviceForm, name_en: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('service_description_label')} (Українська)</label>
                <textarea
                  value={serviceForm.description}
                  onChange={(e) => setServiceForm({ ...serviceForm, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('service_description_label')} (English)</label>
                <textarea
                  value={serviceForm.description_en}
                  onChange={(e) => setServiceForm({ ...serviceForm, description_en: e.target.value })}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>{t('service_price_label')} ({language === 'en' ? 'UAH' : 'грн'}):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={serviceForm.price}
                    onChange={(e) => setServiceForm({ ...serviceForm, price: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('service_duration_label')}</label>
                  <input
                    type="number"
                    value={serviceForm.duration_minutes}
                    onChange={(e) => setServiceForm({ ...serviceForm, duration_minutes: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label>{t('service_category_label')}</label>
                <select
                  value={serviceForm.category_id}
                  onChange={(e) => setServiceForm({ ...serviceForm, category_id: e.target.value })}
                >
                  <option value="">{t('not_specified')}</option>
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.get_name ? category.get_name(language) : category.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={serviceForm.is_active}
                    onChange={(e) => setServiceForm({ ...serviceForm, is_active: e.target.checked })}
                  />
                  {t('service_active_label')}
                </label>
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn btn-primary">
                  {editingService ? t('service_update') : t('service_create')}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowServiceForm(false);
                    setEditingService(null);
                    setServiceForm({
                      name: '',
                      name_en: '',
                      description: '',
                      description_en: '',
                      price: '',
                      duration_minutes: '',
                      category_id: '',
                      is_active: true,
                      is_featured: false
                    });
                  }}
                >
                  {t('cancel')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальне вікно для форми категорії */}
      {showCategoryForm && (
        <div className="modal-overlay">
          <div className="modal" key={`category-form-${language}`}>
            <div className="modal-header">
              <h3>{editingCategory ? t('edit_category') : t('add_category')}</h3>
              <button
                className="btn btn-close"
                onClick={() => {
                  setShowCategoryForm(false);
                  setEditingCategory(null);
                  setCategoryForm({
                    name: '',
                    name_en: '',
                    description: '',
                    description_en: '',
                    order: ''
                  });
                }}
              >
                ×
              </button>
            </div>
            <form onSubmit={editingCategory ? handleUpdateCategory : handleCreateCategory}>
              <div className="form-group">
                <label>{t('category_name_label')} (Українська)</label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('category_name_label')} (English)</label>
                <input
                  type="text"
                  value={categoryForm.name_en}
                  onChange={(e) => setCategoryForm({ ...categoryForm, name_en: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('category_description_label')} (Українська)</label>
                <textarea
                  value={categoryForm.description}
                  onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('category_description_label')} (English)</label>
                <textarea
                  value={categoryForm.description_en}
                  onChange={(e) => setCategoryForm({ ...categoryForm, description_en: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('category_order_label')}</label>
                <input
                  type="number"
                  value={categoryForm.order}
                  onChange={(e) => setCategoryForm({ ...categoryForm, order: e.target.value })}
                  placeholder="Автоматично (залиште порожнім)"
                />
              </div>

              <div className="modal-footer">
                <button type="submit" className="btn btn-primary">
                  {editingCategory ? t('category_update') : t('category_create')}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowCategoryForm(false);
                    setEditingCategory(null);
                    setCategoryForm({
                      name: '',
                      name_en: '',
                      description: '',
                      description_en: '',
                      order: '',
                      is_active: true
                    });
                  }}
                >
                  {t('cancel')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальне вікно для форми боксу */}
      {showBoxForm && (
        <div className="modal-overlay">
          <div className="modal" key={`box-form-${language}`}>
            <div className="modal-header">
              <h3>{editingBox ? t('edit_box') : t('add_box')}</h3>
              <button
                className="btn btn-close"
                onClick={() => {
                  setShowBoxForm(false);
                  setEditingBox(null);
                  setBoxForm({
                    name: '',
                    name_en: '',
                    description: '',
                    description_en: '',
                    is_active: true,
                    working_hours: {
                      monday: { start: '08:00', end: '18:00' },
                      tuesday: { start: '08:00', end: '18:00' },
                      wednesday: { start: '08:00', end: '18:00' },
                      thursday: { start: '08:00', end: '18:00' },
                      friday: { start: '08:00', end: '18:00' },
                      saturday: { start: '09:00', end: '15:00' },
                      sunday: { start: '00:00', end: '00:00' }
                    }
                  });
                }}
              >
                ×
              </button>
            </div>
            <form onSubmit={editingBox ? handleUpdateBox : handleCreateBox}>
              <div className="form-group">
                <label>{t('box_name_label')} (Українська)</label>
                <input
                  type="text"
                  value={boxForm.name}
                  onChange={(e) => setBoxForm({ ...boxForm, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('box_name_label')} (English)</label>
                <input
                  type="text"
                  value={boxForm.name_en}
                  onChange={(e) => setBoxForm({ ...boxForm, name_en: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>{t('box_description_label')} (Українська)</label>
                <textarea
                  value={boxForm.description}
                  onChange={(e) => setBoxForm({ ...boxForm, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>{t('box_description_label')} (English)</label>
                <textarea
                  value={boxForm.description_en}
                  onChange={(e) => setBoxForm({ ...boxForm, description_en: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={boxForm.is_active}
                    onChange={(e) => setBoxForm({ ...boxForm, is_active: e.target.checked })}
                  />
                  {t('box_active_label')}
                </label>
              </div>
              <div className="form-group">
                <label>{t('box_working_hours_label')}</label>
                <div className="dynamic-list">
                  {Object.entries(boxForm.working_hours).map(([day, hours]) => (
                    <div key={day} className="list-item">
                      <strong>{day.charAt(0).toUpperCase() + day.slice(1)}:</strong>
                      <input
                        type="text"
                        value={`${hours.start} - ${hours.end}`}
                        onChange={(e) => {
                          const [start, end] = e.target.value.split(' - ');
                          setBoxForm({
                            ...boxForm,
                            working_hours: {
                              ...boxForm.working_hours,
                              [day]: { start, end }
                            }
                          });
                        }}
                        placeholder="HH:MM - HH:MM"
                      />
                    </div>
                  ))}
                </div>
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn btn-primary">
                  {editingBox ? t('box_update') : t('box_create')}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowBoxForm(false);
                    setEditingBox(null);
                    setBoxForm({
                      name: '',
                      name_en: '',
                      description: '',
                      description_en: '',
                      is_active: true,
                      working_hours: {
                        monday: { start: '08:00', end: '18:00' },
                        tuesday: { start: '08:00', end: '18:00' },
                        wednesday: { start: '08:00', end: '18:00' },
                        thursday: { start: '08:00', end: '18:00' },
                        friday: { start: '08:00', end: '18:00' },
                        saturday: { start: '09:00', end: '15:00' },
                        sunday: { start: '00:00', end: '00:00' }
                      }
                    });
                  }}
                >
                  {t('cancel')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальне вікно для форми інформації про СТО */}
      {showStoInfoForm && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{t('edit_sto_info')}</h3>
              <button
                className="btn btn-close"
                onClick={() => setShowStoInfoForm(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleUpdateStoInfo}>
              <div className="form-group">
                <label>Назва СТО:</label>
                <input
                  type="text"
                  value={stoInfoForm.name}
                  onChange={(e) => setStoInfoForm({ ...stoInfoForm, name: e.target.value })}
                  maxLength={200}
                  required
                />
                <small className="char-counter">{stoInfoForm.name.length}/200</small>
              </div>
              <div className="form-group">
                <label>Девіз:</label>
                <input
                  type="text"
                  value={stoInfoForm.motto}
                  onChange={(e) => setStoInfoForm({ ...stoInfoForm, motto: e.target.value })}
                  maxLength={200}
                  required
                />
                <small className="char-counter">{stoInfoForm.motto.length}/200</small>
              </div>
              <div className="form-group">
                <label>Опис:</label>
                <textarea
                  value={stoInfoForm.description}
                  onChange={(e) => setStoInfoForm({ ...stoInfoForm, description: e.target.value })}
                  maxLength={1000}
                  required
                />
                <small className="char-counter">{stoInfoForm.description.length}/1000</small>
              </div>
              <div className="form-group">
                <label>Привітальний текст:</label>
                <textarea
                  value={stoInfoForm.welcome_text}
                  onChange={(e) => setStoInfoForm({ ...stoInfoForm, welcome_text: e.target.value })}
                  maxLength={1000}
                  required
                />
                <small className="char-counter">{stoInfoForm.welcome_text.length}/1000</small>
              </div>
              <div className="form-group">
                <label>Що ми можемо:</label>
                <input
                  type="text"
                  value={stoInfoForm.what_you_can_title}
                  onChange={(e) => setStoInfoForm({ ...stoInfoForm, what_you_can_title: e.target.value })}
                  maxLength={200}
                  required
                />
                <small className="char-counter">{stoInfoForm.what_you_can_title.length}/200</small>
              </div>
              <div className="form-group">
                <label>Пункти списку:</label>
                <div className="dynamic-list">
                  {stoInfoForm.what_you_can_items.map((item, index) => (
                    <div key={index} className="list-item">
                      <input
                        type="text"
                        value={item}
                        onChange={(e) => {
                          const newItems = [...stoInfoForm.what_you_can_items];
                          newItems[index] = e.target.value;
                          setStoInfoForm({ ...stoInfoForm, what_you_can_items: newItems });
                        }}
                        maxLength={300}
                        placeholder={`Пункт ${index + 1}`}
                      />
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => {
                          if (stoInfoForm.what_you_can_items.length > 1) {
                            const newItems = stoInfoForm.what_you_can_items.filter((_, i) => i !== index);
                            setStoInfoForm({ ...stoInfoForm, what_you_can_items: newItems });
                          }
                        }}
                        disabled={stoInfoForm.what_you_can_items.length <= 1}
                      >
                        Видалити
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => {
                      setStoInfoForm({
                        ...stoInfoForm,
                        what_you_can_items: [...stoInfoForm.what_you_can_items, '']
                      });
                    }}
                  >
                    + Додати пункт
                  </button>
                </div>
              </div>
              <div className="form-group">
                <label>Адреса:</label>
                <input
                  type="text"
                  value={stoInfoForm.address}
                  onChange={(e) => setStoInfoForm({ ...stoInfoForm, address: e.target.value })}
                  maxLength={500}
                  required
                />
                <small className="char-counter">{stoInfoForm.address.length}/500</small>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Телефон:</label>
                  <input
                    type="text"
                    value={stoInfoForm.phone}
                    onChange={(e) => setStoInfoForm({ ...stoInfoForm, phone: e.target.value })}
                    maxLength={20}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email:</label>
                  <input
                    type="email"
                    value={stoInfoForm.email}
                    onChange={(e) => setStoInfoForm({ ...stoInfoForm, email: e.target.value })}
                    maxLength={254}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Робочі години:</label>
                <input
                  type="text"
                  value={stoInfoForm.working_hours}
                  onChange={(e) => setStoInfoForm({ ...stoInfoForm, working_hours: e.target.value })}
                  maxLength={100}
                  required
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={stoInfoForm.is_active}
                    onChange={(e) => setStoInfoForm({ ...stoInfoForm, is_active: e.target.checked })}
                  />
                  Активна
                </label>
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn btn-primary">
                  Оновити
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowStoInfoForm(false)}
                >
                  Скасувати
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальне вікно для форми англійської версії інформації про СТО */}
      {showStoInfoFormEn && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Edit STO Information (English)</h3>
              <button
                className="btn btn-close"
                onClick={() => setShowStoInfoFormEn(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleUpdateStoInfoEn}>
              <div className="form-group">
                <label>STO Name:</label>
                <input
                  type="text"
                  value={stoInfoFormEn.name_en}
                  onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, name_en: e.target.value })}
                  maxLength={200}
                  required
                />
                <small className="char-counter">{stoInfoFormEn.name_en.length}/200</small>
              </div>
              <div className="form-group">
                <label>Motto:</label>
                <input
                  type="text"
                  value={stoInfoFormEn.motto_en}
                  onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, motto_en: e.target.value })}
                  maxLength={200}
                  required
                />
                <small className="char-counter">{stoInfoFormEn.motto_en.length}/200</small>
              </div>
              <div className="form-group">
                <label>Description:</label>
                <textarea
                  value={stoInfoFormEn.description_en}
                  onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, description_en: e.target.value })}
                  maxLength={1000}
                  required
                />
                <small className="char-counter">{stoInfoFormEn.description_en.length}/1000</small>
              </div>
              <div className="form-group">
                <label>Welcome Text:</label>
                <textarea
                  value={stoInfoFormEn.welcome_text_en}
                  onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, welcome_text_en: e.target.value })}
                  maxLength={1000}
                  required
                />
                <small className="char-counter">{stoInfoFormEn.welcome_text_en.length}/1000</small>
              </div>
              <div className="form-group">
                <label>What We Can Do:</label>
                <input
                  type="text"
                  value={stoInfoFormEn.what_you_can_title_en}
                  onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, what_you_can_title_en: e.target.value })}
                  maxLength={200}
                  required
                />
                <small className="char-counter">{stoInfoFormEn.what_you_can_title_en.length}/200</small>
              </div>
              <div className="form-group">
                <label>List Items:</label>
                <div className="dynamic-list">
                  {stoInfoFormEn.what_you_can_items_en.map((item, index) => (
                    <div key={index} className="list-item">
                      <input
                        type="text"
                        value={item}
                        onChange={(e) => {
                          const newItems = [...stoInfoFormEn.what_you_can_items_en];
                          newItems[index] = e.target.value;
                          setStoInfoFormEn({ ...stoInfoFormEn, what_you_can_items_en: newItems });
                        }}
                        maxLength={300}
                        placeholder={`Item ${index + 1}`}
                      />
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => {
                          if (stoInfoFormEn.what_you_can_items_en.length > 1) {
                            const newItems = stoInfoFormEn.what_you_can_items_en.filter((_, i) => i !== index);
                            setStoInfoFormEn({ ...stoInfoFormEn, what_you_can_items_en: newItems });
                          }
                        }}
                        disabled={stoInfoFormEn.what_you_can_items_en.length <= 1}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => {
                      setStoInfoFormEn({
                        ...stoInfoFormEn,
                        what_you_can_items_en: [...stoInfoFormEn.what_you_can_items_en, '']
                      });
                    }}
                  >
                    + Add Item
                  </button>
                </div>
              </div>
              <div className="form-group">
                <label>Address:</label>
                <input
                  type="text"
                  value={stoInfoFormEn.address_en}
                  onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, address_en: e.target.value })}
                  maxLength={500}
                  required
                />
                <small className="char-counter">{stoInfoFormEn.address_en.length}/500</small>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Phone:</label>
                  <input
                    type="text"
                    value={stoInfoFormEn.phone}
                    onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, phone: e.target.value })}
                    maxLength={20}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email:</label>
                  <input
                    type="email"
                    value={stoInfoFormEn.email}
                    onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, email: e.target.value })}
                    maxLength={254}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Working Hours:</label>
                <input
                  type="text"
                  value={stoInfoFormEn.working_hours_en}
                  onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, working_hours_en: e.target.value })}
                  maxLength={100}
                  required
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={stoInfoFormEn.is_active}
                    onChange={(e) => setStoInfoFormEn({ ...stoInfoFormEn, is_active: e.target.checked })}
                  />
                  Active
                </label>
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn btn-primary">
                  Update
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowStoInfoFormEn(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальне вікно для фільтрів записів */}
      {showAppointmentFilters && (
        <div className="modal-overlay">
          <div className="modal" key={`appointment-filters-${language}`}>
            <div className="modal-header">
              <h3>{t('appointment_filters')}</h3>
              <button
                className="btn btn-close"
                onClick={() => setShowAppointmentFilters(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={(e) => {
              e.preventDefault();
              setShowAppointmentFilters(false);
              // Оновлення відбудеться автоматично через useEffect при зміні appointmentFilters
            }}>
              <div className="form-group">
                <label>{t('date_from')}</label>
                <input
                  type="date"
                  value={appointmentFilters.date_from}
                  onChange={(e) => handleAppointmentFilterChange('date_from', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>{t('date_to')}</label>
                <input
                  type="date"
                  value={appointmentFilters.date_to}
                  onChange={(e) => handleAppointmentFilterChange('date_to', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>{t('box')}</label>
                <select
                  value={appointmentFilters.box_id}
                  onChange={(e) => handleAppointmentFilterChange('box_id', e.target.value)}
                >
                  <option value="">{t('all_boxes')}</option>
                  {boxes.map(box => (
                    <option key={box.id} value={box.id}>
                      {box.get_name ? box.get_name(language) : box.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>{t('service')}</label>
                <select
                  value={appointmentFilters.service_id}
                  onChange={(e) => handleAppointmentFilterChange('service_id', e.target.value)}
                >
                  <option value="">{t('all_services')}</option>
                  {services.map(service => (
                    <option key={service.id} value={service.id}>
                      {service.get_name ? service.get_name(language) : service.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>{t('status')}:</label>
                <select
                  value={appointmentFilters.status}
                  onChange={(e) => handleAppointmentFilterChange('status', e.target.value)}
                >
                  <option value="">{t('all_statuses')}</option>
                  <option value="pending">{t('pending')}</option>
                  <option value="confirmed">{t('confirmed')}</option>
                  <option value="completed">{t('completed')}</option>
                  <option value="cancelled">{t('cancelled_by_client')}</option>
                  <option value="cancelled_by_admin">{t('cancelled_by_admin')}</option>
                </select>
              </div>
              <div className="form-group">
                <label>{t('client_name')}</label>
                <input
                  type="text"
                  value={appointmentFilters.customer_name}
                  onChange={(e) => handleAppointmentFilterChange('customer_name', e.target.value)}
                  placeholder={t('client_name_placeholder')}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>{t('time_from')}</label>
                  <input
                    type="time"
                    value={appointmentFilters.time_from}
                    onChange={(e) => handleAppointmentFilterChange('time_from', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>{t('time_to')}</label>
                  <input
                    type="time"
                    value={appointmentFilters.time_to}
                    onChange={(e) => handleAppointmentFilterChange('time_to', e.target.value)}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>{t('price_from')} ({language === 'en' ? 'UAH' : 'грн'}):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={appointmentFilters.price_min}
                    onChange={(e) => handleAppointmentFilterChange('price_min', e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <div className="form-group">
                  <label>{t('price_to')} ({language === 'en' ? 'UAH' : 'грн'}):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={appointmentFilters.price_max}
                    onChange={(e) => handleAppointmentFilterChange('price_max', e.target.value)}
                    placeholder="0.00"
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn btn-primary">
                  {t('apply_filters')}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={clearAppointmentFilters}
                >
                  {t('clear_all_filters')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальне вікно для деталей запису */}
      {showAppointmentDetails && selectedAppointment && (
        <div className="modal-overlay">
          <div className="modal" key={`appointment-details-${language}`}>
            <div className="modal-header">
              <h3>{t('appointment_details')} #{selectedAppointment.id}</h3>
              <button
                className="btn btn-close"
                onClick={() => {
                  setShowAppointmentDetails(false);
                  setSelectedAppointment(null);
                }}
              >
                ×
              </button>
            </div>
            <div className="appointment-details">
              <div className="detail-row">
                <strong>{t('client')}:</strong>
                <span>
                  {selectedAppointment.customer ?
                    `${selectedAppointment.customer.user?.first_name || ''} ${selectedAppointment.customer.user?.last_name || ''}`.trim() ||
                    selectedAppointment.guest_name :
                    selectedAppointment.guest_name
                  }
                </span>
              </div>
              {selectedAppointment.guest_phone && (
                <div className="detail-row">
                  <strong>{t('phone')}</strong>
                  <span>{selectedAppointment.guest_phone}</span>
                </div>
              )}
              {selectedAppointment.guest_email && (
                <div className="detail-row">
                  <strong>{t('email')}</strong>
                  <span>{selectedAppointment.guest_email}</span>
                </div>
              )}
              <div className="detail-row">
                <strong>{t('service')}</strong>
                <span>{selectedAppointment.service?.get_name ? selectedAppointment.service.get_name(language) : selectedAppointment.service?.name}</span>
              </div>
              <div className="detail-row">
                <strong>{t('box_name')}</strong>
                <span>{selectedAppointment.box?.get_name ? selectedAppointment.box.get_name(language) : selectedAppointment.box?.name}</span>
              </div>
              <div className="detail-row">
                <strong>{t('appointment_date')}</strong>
                <span>{formatDate(selectedAppointment.appointment_date)}</span>
              </div>
              <div className="detail-row">
                <strong>{t('appointment_time')}</strong>
                <span>{formatTime(selectedAppointment.appointment_time)}</span>
              </div>
              <div className="detail-row">
                <strong>{t('status')}:</strong>
                <span className={getStatusBadgeClass(selectedAppointment.status)}>
                  {getStatusText(selectedAppointment.status)}
                </span>
              </div>
              <div className="detail-row">
                <strong>{t('total_cost')}</strong>
                <span>
                  {selectedAppointment.total_price} {language === 'en' ? 'UAH' : 'грн'}
                  {(() => {
                    const selectedService = selectedAppointment.service;
                    if (selectedService && selectedService.price !== selectedAppointment.total_price) {
                      const discountAmount = selectedService.price - selectedAppointment.total_price;
                      const discountPercentage = (discountAmount / selectedService.price) * 100;
                      return (
                        <span className="discount-applied">
                          {' '}({t('discount')} {discountPercentage.toFixed(1)}%: -{discountAmount.toFixed(2)} {language === 'en' ? 'UAH' : 'грн'})
                        </span>
                      );
                    }
                    return null;
                  })()}
                </span>
              </div>
              {selectedAppointment.notes && (
                <div className="detail-row">
                  <strong>{t('notes')}:</strong>
                  <span>{selectedAppointment.notes}</span>
                </div>
              )}
              {!selectedAppointment.notes && (
                <div className="detail-row">
                  <strong>{t('notes')}:</strong>
                  <span>{t('no_notes')}</span>
                </div>
              )}
              <div className="detail-row">
                <strong>{t('created_at')}</strong>
                <span>{new Date(selectedAppointment.created_at).toLocaleString(language === 'en' ? 'en-US' : 'uk-UA')}</span>
              </div>
              {selectedAppointment.updated_at !== selectedAppointment.created_at && (
                <div className="detail-row">
                  <strong>{t('updated_at')}</strong>
                  <span>{new Date(selectedAppointment.updated_at).toLocaleString(language === 'en' ? 'en-US' : 'uk-UA')}</span>
                </div>
              )}
            </div>
            <div className="modal-footer">
              {(selectedAppointment.status === 'pending' || selectedAppointment.status === 'confirmed') && (
                <button
                  className="btn btn-danger"
                  onClick={() => {
                    handleCancelAppointment(selectedAppointment.id);
                    setShowAppointmentDetails(false);
                    setSelectedAppointment(null);
                  }}
                >
                  {t('cancel_appointment')}
                </button>
              )}
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setShowAppointmentDetails(false);
                  setSelectedAppointment(null);
                }}
              >
                {t('close')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальне вікно редагування клієнта */}
      {showCustomerEditForm && (
        <div className="modal-overlay">
          <div className="modal customer-edit-modal">
            <div className="modal-header">
              <h3>Редагування клієнта</h3>
              <button
                type="button"
                className="btn-close"
                onClick={() => {
                  setShowCustomerEditForm(false);
                  setEditingCustomer(null);
                  setCustomerEditForm({
                    first_name: '',
                    last_name: '',
                    email: '',
                    password: '',
                    password_confirm: ''
                  });
                }}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleUpdateCustomer} className="customer-edit-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Ім'я</label>
                  <input
                    type="text"
                    name="first_name"
                    value={customerEditForm.first_name}
                    onChange={handleCustomerEditChange}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Фамілія</label>
                  <input
                    type="text"
                    name="last_name"
                    value={customerEditForm.last_name}
                    onChange={handleCustomerEditChange}
                    className="form-input"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  value={customerEditForm.email}
                  onChange={handleCustomerEditChange}
                  className="form-input"
                  required
                />
              </div>



              <div className="password-section">
                <h4>Зміна пароля</h4>
                <p className="password-hint">Залиште поля порожніми, якщо не хочете змінювати пароль</p>

                <div className="form-row">
                  <div className="form-group">
                    <label>Новий пароль</label>
                    <input
                      type="password"
                      name="password"
                      value={customerEditForm.password}
                      onChange={handleCustomerEditChange}
                      className="form-input"
                      placeholder="Введіть новий пароль"
                    />
                    <small className="password-requirements">
                      Пароль повинен містити мінімум 8 символів, великі та малі літери, цифри
                    </small>
                  </div>

                  <div className="form-group">
                    <label>Підтвердіть новий пароль</label>
                    <input
                      type="password"
                      name="password_confirm"
                      value={customerEditForm.password_confirm}
                      onChange={handleCustomerEditChange}
                      className="form-input"
                      placeholder="Повторіть новий пароль"
                    />
                    <small className="password-hint">
                      Введіть пароль ще раз для підтвердження
                    </small>
                  </div>
                </div>
              </div>

              <div className="modal-footer">
                <button type="submit" className="btn btn-primary">Зберегти зміни</button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowCustomerEditForm(false);
                    setEditingCustomer(null);
                    setCustomerEditForm({
                      first_name: '',
                      last_name: '',
                      email: '',
                      password: '',
                      password_confirm: ''
                    });
                  }}
                >
                  Скасувати
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальне вікно для управління рекомендованими послугами */}
      {showFeaturedServicesForm && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{t('manage_featured_services')}</h3>
              <button
                className="btn btn-close"
                onClick={() => setShowFeaturedServicesForm(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>{t('select_featured_services_description')}</p>

              <div className="featured-services-list">
                {services.map(service => (
                  <div key={service.id} className="featured-service-item">
                    <label>
                      <input
                        type="checkbox"
                        checked={service.is_featured}
                        onChange={async (e) => {
                          try {
                            await api.post(`/api/admin/${service.id}/toggle_featured_service/`);
                            // Оновлюємо список послуг
                            const response = await api.get(`/api/admin/services_management/?language=${language}`);
                            setServices(response.data);
                          } catch (error) {
                            toast.error(t('error_toggle_featured_service'));
                          }
                        }}
                      />
                      <span className="service-name">{service.name}</span>
                      <span className="service-price">{service.price} {language === 'en' ? 'UAH' : 'грн'}</span>
                    </label>
                  </div>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setShowFeaturedServicesForm(false)}
              >
                {t('close')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;

// Стилі для управління рекомендованими послугами
const styles = `
  .featured-services-list {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
  }
  
  .featured-service-item {
    padding: 8px;
    border-bottom: 1px solid #eee;
  }
  
  .featured-service-item:last-child {
    border-bottom: none;
  }
  
  .featured-service-item label {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
  }
  
  .featured-service-item input[type="checkbox"] {
    margin: 0;
  }
  
  .service-name {
    flex: 1;
    font-weight: 500;
  }
  
  .service-price {
    color: #666;
    font-size: 0.9em;
  }
`;

// Додаємо стилі до DOM
if (!document.getElementById('admin-panel-styles')) {
  const styleSheet = document.createElement('style');
  styleSheet.id = 'admin-panel-styles';
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
} 