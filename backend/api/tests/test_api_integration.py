"""
Інтеграційні тести для API endpoints.
Перевіряють взаємодію між views, serializers, services та базою даних.
"""

from decimal import Decimal
from datetime import date, time, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from backend.api.models import (
    ServiceCategory, Service, Customer, Appointment, Box, STOInfo
)


class AuthAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API аутентифікації"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'

    def test_register_user_success(self):
        """Перевірка успішної реєстрації через API"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')

        # Перевіряємо що користувач створився в БД
        user = User.objects.get(email='newuser@example.com')
        self.assertTrue(hasattr(user, 'customer'))

    def test_register_user_duplicate_email(self):
        """Перевірка обробки дублікату email через API"""
        # Створюємо першого користувача
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )

        data = {
            'email': 'existing@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('вже існує', response.data['error'].lower())

    def test_login_user_success(self):
        """Перевірка успішного входу через API"""
        # Створюємо користувача
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Customer.objects.create(user=user)

        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_user_wrong_password(self):
        """Перевірка обробки неправильного пароля через API"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Customer.objects.create(user=user)

        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ServicesAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API послуг"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.category = ServiceCategory.objects.create(
            name='Технічне обслуговування',
            name_en='Technical Maintenance',
            order=1
        )
        self.service = Service.objects.create(
            name='Повне ТО',
            name_en='Full Technical Maintenance',
            description='Опис',
            description_en='Description',
            price=Decimal('1500.00'),
            category=self.category,
            duration_minutes=120,
            is_active=True
        )

    def test_get_services_list_ukrainian(self):
        """Перевірка отримання списку послуг українською"""
        url = '/api/services/?language=uk'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['name'], 'Повне ТО')
        self.assertEqual(response.data[0]['category']['name'], 'Технічне обслуговування')

    def test_get_services_list_english(self):
        """Перевірка отримання списку послуг англійською"""
        url = '/api/services/?language=en'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Full Technical Maintenance')
        self.assertEqual(response.data[0]['category']['name'], 'Technical Maintenance')

    def test_get_featured_services(self):
        """Перевірка отримання рекомендованих послуг"""
        # Створюємо рекомендовану послугу
        featured_service = Service.objects.create(
            name='Рекомендована послуга',
            name_en='Featured Service',
            price=Decimal('2000.00'),
            category=self.category,
            is_featured=True,
            is_active=True
        )

        url = '/api/services/featured/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertTrue(any(s['id'] == featured_service.id for s in response.data))

    def test_get_service_categories(self):
        """Перевірка отримання категорій послуг"""
        url = '/api/service-categories/?language=uk'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['name'], 'Технічне обслуговування')


class AppointmentsAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API записів"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.customer = Customer.objects.create(user=self.user)
        self.category = ServiceCategory.objects.create(name='Тест', order=1)
        self.service = Service.objects.create(
            name='Тестова послуга',
            name_en='Test Service',
            price=Decimal('1000.00'),
            category=self.category,
            duration_minutes=60
        )
        self.box = Box.objects.create(
            name='Бокс 1',
            name_en='Box 1',
            working_hours={
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'},
                'wednesday': {'start': '08:00', 'end': '18:00'},
                'thursday': {'start': '08:00', 'end': '18:00'},
                'friday': {'start': '08:00', 'end': '18:00'},
                'saturday': {'start': '09:00', 'end': '15:00'},
                'sunday': {'start': '00:00', 'end': '00:00'}
            },
            is_active=True
        )

    def test_create_appointment_authenticated(self):
        """Перевірка створення запису авторизованим користувачем"""
        self.client.force_authenticate(user=self.user)

        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'notes': 'Тестова примітка'
        }

        url = '/api/appointments/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['service']['id'], self.service.id)
        self.assertEqual(response.data['status'], 'pending')

        # Перевіряємо що запис створився в БД
        appointment = Appointment.objects.get(id=response.data['id'])
        self.assertEqual(appointment.customer, self.customer)
        self.assertEqual(appointment.service, self.service)

    def test_create_appointment_with_discount(self):
        """Перевірка застосування знижки при створенні запису"""
        # Створюємо 4 завершених записів (2% знижка)
        for i in range(4):
            Appointment.objects.create(
                customer=self.customer,
                service=self.service,
                box=self.box,
                appointment_date=date.today(),
                appointment_time=time(10, 0),
                status='completed',
                total_price=Decimal('1000.00')
            )

        self.client.force_authenticate(user=self.user)

        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00'
        }

        url = '/api/appointments/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Ціна має бути зі знижкою 2%
        expected_price = Decimal('980.00')  # 1000 - 2%
        self.assertEqual(Decimal(str(response.data['total_price'])), expected_price)

    def test_create_appointment_unauthenticated(self):
        """Перевірка що неавторизований користувач не може створити запис"""
        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00'
        }

        url = '/api/appointments/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_my_appointments(self):
        """Перевірка отримання власних записів"""
        # Створюємо кілька записів
        for i in range(3):
            Appointment.objects.create(
                customer=self.customer,
                service=self.service,
                box=self.box,
                appointment_date=date.today() + timedelta(days=i+1),
                appointment_time=time(10, 0),
                status='pending',
                total_price=Decimal('1000.00')
            )

        self.client.force_authenticate(user=self.user)

        url = '/api/appointments/my_appointments/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_update_appointment_success(self):
        """Перевірка оновлення запису"""
        tomorrow = date.today() + timedelta(days=2)
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.user)

        new_date = tomorrow + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': new_date.strftime('%Y-%m-%d'),
            'appointment_time': '14:00',
            'notes': 'Оновлена примітка'
        }

        url = f'/api/appointments/{appointment.id}/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['appointment_time'], '14:00:00')
        self.assertEqual(response.data['notes'], 'Оновлена примітка')

    def test_cancel_appointment(self):
        """Перевірка скасування запису"""
        tomorrow = date.today() + timedelta(days=2)
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/appointments/{appointment.id}/cancel/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('скасовано', response.data['message'].lower())

        # Перевіряємо що статус змінився
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled')

    def test_create_guest_appointment(self):
        """Перевірка створення запису для гостя"""
        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'guest_name': 'Guest User',
            'guest_phone': '+380501234567',
            'guest_email': 'guest@example.com'
        }

        url = '/api/guest-appointments/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['guest_name'], 'Guest User')
        self.assertEqual(response.data['guest_email'], 'guest@example.com')
        self.assertIsNone(response.data.get('customer'))


class BoxesAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API боксів"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.box = Box.objects.create(
            name='Бокс 1',
            name_en='Box 1',
            working_hours={
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'}
            },
            is_active=True
        )
        self.category = ServiceCategory.objects.create(name='Тест', order=1)
        self.service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=self.category,
            duration_minutes=60
        )

    def test_get_available_dates(self):
        """Перевірка отримання доступних дат"""
        url = f'/api/boxes/available_dates/?service_id={self.service.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_dates', response.data)
        self.assertIsInstance(response.data['available_dates'], list)

    def test_get_available_times(self):
        """Перевірка отримання доступних часів"""
        tomorrow = date.today() + timedelta(days=1)
        url = f'/api/boxes/available_times/?date={tomorrow.strftime("%Y-%m-%d")}&service_id={self.service.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_times', response.data)
        self.assertIsInstance(response.data['available_times'], list)
        self.assertGreater(len(response.data['available_times']), 0)


class CustomerProfileAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API профілю клієнта"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            address='Test Address',
            loyalty_points=100
        )

    def test_get_profile(self):
        """Перевірка отримання профілю"""
        self.client.force_authenticate(user=self.user)

        url = '/api/customers/profile/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['first_name'], 'Test')
        self.assertEqual(response.data['loyalty_points'], 100)
        self.assertEqual(response.data['address'], 'Test Address')

    def test_update_profile(self):
        """Перевірка оновлення профілю"""
        self.client.force_authenticate(user=self.user)

        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'address': 'New Address'
        }

        url = '/api/customers/update_profile/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], 'Updated')
        self.assertEqual(response.data['user']['email'], 'updated@example.com')
        self.assertEqual(response.data['address'], 'New Address')

        # Перевіряємо що дані оновилися в БД
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@example.com')


class STOInfoAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API інформації про СТО"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.sto_info = STOInfo.objects.create(
            name='СТО Test',
            name_en='STO Test',
            description='Опис',
            description_en='Description',
            motto='Девіз',
            motto_en='Motto',
            welcome_text='Ласкаво просимо',
            welcome_text_en='Welcome',
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

    def test_get_sto_info_ukrainian(self):
        """Перевірка отримання інформації про СТО українською"""
        url = '/api/sto-info/?language=uk'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'СТО Test')
        self.assertEqual(response.data['motto'], 'Девіз')

    def test_get_sto_info_english(self):
        """Перевірка отримання інформації про СТО англійською"""
        url = '/api/sto-info/?language=en'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'STO Test')
        self.assertEqual(response.data['motto'], 'Motto')


class FullAppointmentFlowTest(TestCase):
    """Інтеграційні тести для повного flow створення та обробки запису"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(user=self.user)
        self.category = ServiceCategory.objects.create(name='Тест', order=1)
        self.service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=self.category,
            duration_minutes=60
        )
        self.box = Box.objects.create(
            name='Бокс 1',
            working_hours={
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'}
            },
            is_active=True
        )

    def test_full_appointment_flow(self):
        """Перевірка повного flow: створення -> підтвердження -> завершення"""
        self.client.force_authenticate(user=self.user)

        # 1. Створення запису
        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00'
        }

        create_url = '/api/appointments/'
        response = self.client.post(create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        appointment_id = response.data['id']
        self.assertEqual(response.data['status'], 'pending')

        # 2. Підтвердження запису (як адміністратор)
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.client.force_authenticate(user=admin_user)

        confirm_url = f'/api/appointments/{appointment_id}/confirm/'
        response = self.client.post(confirm_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Перевіряємо що статус змінився
        appointment = Appointment.objects.get(id=appointment_id)
        self.assertEqual(appointment.status, 'confirmed')

        # 3. Завершення запису
        complete_url = f'/api/appointments/{appointment_id}/complete/'
        response = self.client.post(complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Перевіряємо що статус змінився
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')


class ServiceHistoryAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API історії обслуговування"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(user=self.user)
        self.category = ServiceCategory.objects.create(name='Тест', order=1)
        self.service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=self.category
        )
        self.box = Box.objects.create(
            name='Бокс 1',
            working_hours={'monday': {'start': '08:00', 'end': '18:00'}},
            is_active=True
        )

    def test_get_service_history(self):
        """Перевірка отримання історії обслуговування"""
        from backend.api.models import ServiceHistory

        # Створюємо завершений запис з історією
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() - timedelta(days=1),
            appointment_time=time(10, 0),
            status='completed',
            total_price=Decimal('1000.00')
        )

        ServiceHistory.objects.create(
            appointment=appointment,
            actual_duration=60,
            final_price=Decimal('1000.00'),
            mechanic_notes='Все добре'
        )

        self.client.force_authenticate(user=self.user)

        url = '/api/service-history/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['appointment']['id'], appointment.id)


class LoyaltyTransactionsAPIIntegrationTest(TestCase):
    """Інтеграційні тести для API транзакцій лояльності"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(user=self.user)

    def test_get_loyalty_transactions(self):
        """Перевірка отримання транзакцій лояльності"""
        from backend.api.models import LoyaltyTransaction

        # Створюємо транзакції
        LoyaltyTransaction.objects.create(
            customer=self.customer,
            transaction_type='earned',
            points=100,
            description='Тестова транзакція'
        )

        self.client.force_authenticate(user=self.user)

        url = '/api/loyalty-transactions/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['points'], 100)

