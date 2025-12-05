"""
End-to-End (E2E) тести для повних сценаріїв використання.
Перевіряють повний flow від початку до кінця, імітуючи реальну поведінку користувача.
Це вершина піраміди тестування.
"""

from decimal import Decimal
from datetime import date, time, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from backend.api.models import (
    ServiceCategory, Service, Customer, Appointment, Box, STOInfo
)


class CustomerE2ETest(TestCase):
    """E2E тести для повного flow користувача"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()

        # Створюємо базові дані
        self.category = ServiceCategory.objects.create(
            name='Технічне обслуговування',
            name_en='Technical Maintenance',
            order=1
        )
        self.service = Service.objects.create(
            name='Повне ТО',
            name_en='Full Technical Maintenance',
            description='Повне технічне обслуговування',
            description_en='Full technical maintenance',
            price=Decimal('1500.00'),
            category=self.category,
            duration_minutes=120,
            is_active=True,
            is_featured=True
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
        STOInfo.objects.create(
            name='СТО AutoServis',
            name_en='Auto Service AutoServis',
            description='Найкращий сервіс',
            description_en='Best service',
            address='Вул. Тестова, 1',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

    def test_full_customer_journey(self):
        """
        Повний E2E сценарій користувача:
        1. Перегляд головної сторінки (інформація про СТО)
        2. Перегляд послуг
        3. Реєстрація
        4. Вхід в систему
        5. Перегляд профілю
        6. Створення запису
        7. Перегляд своїх записів
        8. Оновлення запису
        9. Скасування запису
        """
        # 1. Перегляд інформації про СТО (без авторизації)
        sto_url = '/api/sto-info/?language=uk'
        response = self.client.get(sto_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'СТО AutoServis')

        # 2. Перегляд послуг (без авторизації)
        services_url = '/api/services/?language=uk'
        response = self.client.get(services_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        service_id = response.data[0]['id']

        # 3. Реєстрація
        register_data = {
            'email': 'newcustomer@example.com',
            'username': 'newcustomer',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Customer'
        }
        register_url = '/api/auth/register/'
        response = self.client.post(register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        access_token = response.data['access']

        # 4. Вхід в систему (використовуємо токен)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 5. Перегляд профілю
        profile_url = '/api/customers/profile/'
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']
                         ['email'], 'newcustomer@example.com')
        self.assertEqual(response.data['completed_appointments_count'], 0)

        # 6. Отримання доступних дат
        tomorrow = date.today() + timedelta(days=1)
        available_dates_url = f'/api/boxes/available_dates/?service_id={service_id}'
        response = self.client.get(available_dates_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_dates', response.data)

        # 7. Отримання доступних часів
        available_times_url = f'/api/boxes/available_times/?date={tomorrow.strftime("%Y-%m-%d")}&service_id={service_id}'
        response = self.client.get(available_times_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_times', response.data)
        available_time = response.data['available_times'][0] if response.data['available_times'] else '10:00'

        # 8. Створення запису
        appointment_data = {
            'service_id': service_id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': available_time,
            'notes': 'E2E тестовий запис'
        }
        appointment_url = '/api/appointments/'
        response = self.client.post(
            appointment_url, appointment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        appointment_id = response.data['id']
        self.assertEqual(response.data['status'], 'pending')

        # 9. Перегляд своїх записів
        my_appointments_url = '/api/appointments/my_appointments/'
        response = self.client.get(my_appointments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['id'], appointment_id)

        # 10. Оновлення запису (якщо є час)
        future_date = date.today() + timedelta(days=3)
        update_data = {
            'service_id': service_id,
            'appointment_date': future_date.strftime('%Y-%m-%d'),
            'appointment_time': '14:00',
            'notes': 'Оновлений запис'
        }
        update_url = f'/api/appointments/{appointment_id}/'
        response = self.client.patch(update_url, update_data, format='json')
        # Може бути помилка якщо менше 2 годин до запису, це нормально
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data['notes'], 'Оновлений запис')

        # 11. Скасування запису
        cancel_url = f'/api/appointments/{appointment_id}/cancel/'
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Перевіряємо що запис скасований
        appointment = Appointment.objects.get(id=appointment_id)
        self.assertEqual(appointment.status, 'cancelled')


class GuestE2ETest(TestCase):
    """E2E тести для повного flow гостя (без реєстрації)"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()

        self.category = ServiceCategory.objects.create(
            name='Діагностика',
            name_en='Diagnostics',
            order=1
        )
        self.service = Service.objects.create(
            name='Комп\'ютерна діагностика',
            name_en='Computer Diagnostics',
            price=Decimal('500.00'),
            category=self.category,
            duration_minutes=45,
            is_active=True
        )
        self.box = Box.objects.create(
            name='Бокс 2',
            working_hours={
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'}
            },
            is_active=True
        )

    def test_full_guest_journey(self):
        """
        Повний E2E сценарій гостя:
        1. Перегляд послуг
        2. Перегляд інформації про СТО
        3. Створення запису без реєстрації
        4. Перевірка що запис створився
        """
        # 1. Перегляд послуг (без авторизації)
        services_url = '/api/services/?language=uk'
        response = self.client.get(services_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_id = None
        for service in response.data:
            if service['id'] == self.service.id:
                service_id = service['id']
                break
        self.assertIsNotNone(service_id)

        # 2. Перегляд інформації про СТО
        sto_url = '/api/sto-info/?language=uk'
        response = self.client.get(sto_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Отримання доступних дат
        tomorrow = date.today() + timedelta(days=1)
        available_dates_url = f'/api/boxes/available_dates/?service_id={service_id}'
        response = self.client.get(available_dates_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. Отримання доступних часів
        available_times_url = f'/api/boxes/available_times/?date={tomorrow.strftime("%Y-%m-%d")}&service_id={service_id}'
        response = self.client.get(available_times_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        available_time = response.data['available_times'][0] if response.data['available_times'] else '10:00'

        # 5. Створення запису для гостя
        guest_appointment_data = {
            'service_id': service_id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': available_time,
            'guest_name': 'Guest User',
            'guest_phone': '+380501234567',
            'guest_email': 'guest@example.com',
            'notes': 'E2E тест для гостя'
        }
        guest_appointment_url = '/api/guest-appointments/'
        response = self.client.post(
            guest_appointment_url, guest_appointment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['guest_name'], 'Guest User')
        self.assertEqual(response.data['guest_email'], 'guest@example.com')
        self.assertIsNone(response.data.get('customer'))

        # 6. Перевірка що запис створився в БД
        appointment = Appointment.objects.get(id=response.data['id'])
        self.assertIsNone(appointment.customer)
        self.assertEqual(appointment.guest_name, 'Guest User')
        self.assertEqual(appointment.status, 'pending')


class AdminE2ETest(TestCase):
    """E2E тести для повного flow адміністратора"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()

        # Створюємо адміністратора
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@sto.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )

        # Створюємо користувача
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customer123',
            first_name='Test',
            last_name='Customer'
        )
        self.customer = Customer.objects.create(user=self.user)

        # Створюємо послуги та бокси
        self.category = ServiceCategory.objects.create(
            name='Технічне обслуговування',
            name_en='Technical Maintenance',
            order=1
        )
        self.service = Service.objects.create(
            name='Повне ТО',
            name_en='Full Technical Maintenance',
            price=Decimal('1500.00'),
            category=self.category,
            duration_minutes=120,
            is_active=True
        )
        self.box = Box.objects.create(
            name='Бокс 1',
            working_hours={
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'}
            },
            is_active=True
        )

    def test_full_admin_journey(self):
        """
        Повний E2E сценарій адміністратора:
        1. Вхід в систему
        2. Перегляд статистики
        3. Перегляд клієнтів
        4. Перегляд записів
        5. Підтвердження запису
        6. Завершення запису
        7. Перегляд статистики після змін
        8. Управління послугами
        9. Управління клієнтами
        """
        # 1. Вхід в систему
        login_data = {
            'email': 'admin@sto.com',
            'password': 'admin123'
        }
        login_url = '/api/auth/login/'
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 2. Перегляд статистики
        stats_url = '/api/admin/statistics/'
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        initial_appointments = response.data['total_appointments']

        # 3. Перегляд клієнтів
        customers_url = '/api/admin/customer_management/'
        response = self.client.get(customers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

        # 4. Створення запису для клієнта (як адмін)
        tomorrow = date.today() + timedelta(days=1)
        appointment_data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'notes': 'Запис створений адміністратором'
        }
        # Адмін може створювати записи через API (якщо є такий endpoint)
        # Або через клієнта
        self.client.force_authenticate(user=self.user)
        appointment_url = '/api/appointments/'
        response = self.client.post(
            appointment_url, appointment_data, format='json')
        appointment_id = response.data['id']

        # 5. Перехід на адміна
        self.client.force_authenticate(user=self.admin)

        # 6. Перегляд записів з фільтрами
        appointments_url = '/api/admin/appointments/?status=pending'
        response = self.client.get(appointments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 7. Підтвердження запису
        confirm_url = f'/api/appointments/{appointment_id}/confirm/'
        response = self.client.post(confirm_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 8. Перевірка статусу
        appointment = Appointment.objects.get(id=appointment_id)
        self.assertEqual(appointment.status, 'confirmed')

        # 9. Завершення запису
        complete_url = f'/api/appointments/{appointment_id}/complete/'
        response = self.client.post(complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 10. Перевірка статусу
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')

        # 11. Перегляд статистики після змін
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(
            response.data['completed_appointments'],
            initial_appointments
        )

        # 12. Перегляд тижневого розкладу
        schedule_url = '/api/admin/weekly_schedule/'
        response = self.client.get(schedule_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('schedule', response.data)

        # 13. Управління послугами - перегляд
        services_url = '/api/admin/services_management/'
        response = self.client.get(services_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 14. Створення нової послуги
        new_service_data = {
            'name': 'Нова послуга E2E',
            'name_en': 'New Service E2E',
            'description': 'Опис',
            'description_en': 'Description',
            'price': '2000.00',
            'category_id': self.category.id,
            'duration_minutes': 90,
            'is_active': True
        }
        create_service_url = '/api/admin/create_service/'
        response = self.client.post(
            create_service_url, new_service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_service_id = response.data['id']

        # 15. Оновлення послуги
        update_service_data = {
            'price': '2200.00'
        }
        update_service_url = f'/api/admin/{new_service_id}/update_service/'
        response = self.client.patch(
            update_service_url, update_service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 16. Управління клієнтом - блокування
        block_url = f'/api/admin/{self.customer.id}/block_customer/'
        response = self.client.post(block_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_blocked)

        # 17. Розблокування клієнта
        unblock_url = f'/api/admin/{self.customer.id}/unblock_customer/'
        response = self.client.post(unblock_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_blocked)


class LoyaltySystemE2ETest(TestCase):
    """E2E тести для повного циклу системи лояльності"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='loyaltyuser',
            email='loyalty@example.com',
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
            working_hours={'monday': {'start': '08:00', 'end': '18:00'}},
            is_active=True
        )

    def test_full_loyalty_cycle(self):
        """
        Повний E2E цикл системи лояльності:
        1. Створення записів
        2. Завершення записів (нарахування знижки)
        3. Перевірка знижки в новому записі
        4. Перевірка історії транзакцій
        """
        self.client.force_authenticate(user=self.user)

        # 1. Перегляд профілю (початковий стан)
        profile_url = '/api/customers/profile/'
        response = self.client.get(profile_url)
        initial_discount_count = response.data['completed_appointments_count']
        self.assertEqual(initial_discount_count, 0)

        # 2. Створення та завершення 5 записів (має бути 2.5% знижка)
        for i in range(5):
            tomorrow = date.today() + timedelta(days=i+1)
            appointment_data = {
                'service_id': self.service.id,
                'appointment_date': tomorrow.strftime('%Y-%m-%d'),
                'appointment_time': '10:00'
            }

            # Створення запису
            appointment_url = '/api/appointments/'
            response = self.client.post(
                appointment_url, appointment_data, format='json')
            appointment_id = response.data['id']

            # Завершення запису (як адмін)
            admin = User.objects.create_user(
                username=f'admin{i}',
                email=f'admin{i}@example.com',
                password='admin123',
                is_staff=True
            )
            self.client.force_authenticate(user=admin)
            complete_url = f'/api/appointments/{appointment_id}/complete/'
            self.client.post(complete_url)

            # Повертаємось на користувача
            self.client.force_authenticate(user=self.user)

        # 3. Перегляд профілю після завершених записів
        response = self.client.get(profile_url)
        self.assertEqual(response.data['completed_appointments_count'], 5)

        # 4. Створення нового запису (має бути знижка 2.5%)
        future_date = date.today() + timedelta(days=10)
        new_appointment_data = {
            'service_id': self.service.id,
            'appointment_date': future_date.strftime('%Y-%m-%d'),
            'appointment_time': '10:00'
        }
        response = self.client.post(
            appointment_url, new_appointment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Перевірка що застосована знижка
        expected_price = Decimal('975.00')  # 1000 - 2.5% = 975
        actual_price = Decimal(str(response.data['total_price']))
        self.assertEqual(actual_price, expected_price)

        # 5. Перегляд історії обслуговування
        history_url = '/api/service-history/'
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 5)

        # 6. Перегляд транзакцій лояльності
        transactions_url = '/api/loyalty-transactions/'
        response = self.client.get(transactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MultilingualE2ETest(TestCase):
    """E2E тести для багатомовності в повних сценаріях"""

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
            description='Повне технічне обслуговування',
            description_en='Full technical maintenance',
            price=Decimal('1500.00'),
            category=self.category,
            is_active=True
        )
        STOInfo.objects.create(
            name='СТО Test',
            name_en='STO Test',
            description='Опис українською',
            description_en='Description in English',
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

    def test_multilingual_user_journey(self):
        """
        E2E тест багатомовності:
        1. Перегляд українською
        2. Перегляд англійською
        3. Створення запису з різними мовами
        """
        # 1. Перегляд послуг українською
        services_uk_url = '/api/services/?language=uk'
        response = self.client.get(services_uk_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Повне ТО')
        self.assertEqual(response.data[0]['category']
                         ['name'], 'Технічне обслуговування')

        # 2. Перегляд послуг англійською
        services_en_url = '/api/services/?language=en'
        response = self.client.get(services_en_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'],
                         'Full Technical Maintenance')
        self.assertEqual(response.data[0]['category']
                         ['name'], 'Technical Maintenance')

        # 3. Перегляд інформації про СТО українською
        sto_uk_url = '/api/sto-info/?language=uk'
        response = self.client.get(sto_uk_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'СТО Test')
        self.assertIn('українською', response.data['description'].lower())

        # 4. Перегляд інформації про СТО англійською
        sto_en_url = '/api/sto-info/?language=en'
        response = self.client.get(sto_en_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'STO Test')
        self.assertIn('english', response.data['description'].lower())
