"""
Інтеграційні тести для адміністративних API endpoints.
Перевіряють функціонал адмін панелі.
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


class AdminStatisticsAPITest(TestCase):
    """Тести для API статистики адміністратора"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
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

    def test_get_statistics(self):
        """Перевірка отримання статистики"""
        # Створюємо тестові дані
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(11, 0),
            status='completed',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.admin)

        url = '/api/admin/statistics/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_appointments', response.data)
        self.assertIn('pending_appointments', response.data)
        self.assertIn('completed_appointments', response.data)
        self.assertIn('total_customers', response.data)
        self.assertEqual(response.data['total_appointments'], 2)
        self.assertEqual(response.data['pending_appointments'], 1)
        self.assertEqual(response.data['completed_appointments'], 1)

    def test_get_statistics_non_admin(self):
        """Перевірка що не-адмін не може отримати статистику"""
        self.client.force_authenticate(user=self.user)

        url = '/api/admin/statistics/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCustomerManagementTest(TestCase):
    """Тести для управління клієнтами"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123',
            first_name='Test',
            last_name='User'
        )
        self.customer = Customer.objects.create(user=self.user)

    def test_get_customers_list(self):
        """Перевірка отримання списку клієнтів"""
        self.client.force_authenticate(user=self.admin)

        url = '/api/admin/customer_management/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['user']['email'], 'user@example.com')

    def test_block_customer(self):
        """Перевірка блокування клієнта"""
        self.client.force_authenticate(user=self.admin)

        url = f'/api/admin/{self.customer.id}/block_customer/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('заблоковано', response.data['message'].lower())

        # Перевіряємо що клієнт заблокований
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_blocked)

    def test_unblock_customer(self):
        """Перевірка розблокування клієнта"""
        # Спочатку блокуємо
        self.customer.is_blocked = True
        self.customer.save()

        self.client.force_authenticate(user=self.admin)

        url = f'/api/admin/{self.customer.id}/unblock_customer/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('розблоковано', response.data['message'].lower())

        # Перевіряємо що клієнт розблокований
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_blocked)

    def test_update_customer(self):
        """Перевірка оновлення даних клієнта"""
        self.client.force_authenticate(user=self.admin)

        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }

        url = f'/api/admin/{self.customer.id}/update_customer/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], 'Updated')
        self.assertEqual(response.data['user']['email'], 'updated@example.com')


class AdminServicesManagementTest(TestCase):
    """Тести для управління послугами"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.category = ServiceCategory.objects.create(
            name='Категорія',
            name_en='Category',
            order=1
        )

    def test_get_services_list(self):
        """Перевірка отримання списку послуг для управління"""
        Service.objects.create(
            name='Послуга 1',
            name_en='Service 1',
            price=Decimal('1000.00'),
            category=self.category
        )

        self.client.force_authenticate(user=self.admin)

        url = '/api/admin/services_management/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_create_service(self):
        """Перевірка створення послуги"""
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': 'Нова послуга',
            'name_en': 'New Service',
            'description': 'Опис',
            'description_en': 'Description',
            'price': '1500.00',
            'category_id': self.category.id,
            'duration_minutes': 90,
            'is_active': True,
            'is_featured': False
        }

        url = '/api/admin/create_service/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Нова послуга')
        self.assertEqual(response.data['price'], '1500.00')

        # Перевіряємо що послуга створилася в БД
        service = Service.objects.get(id=response.data['id'])
        self.assertEqual(service.name, 'Нова послуга')

    def test_update_service(self):
        """Перевірка оновлення послуги"""
        service = Service.objects.create(
            name='Послуга',
            name_en='Service',
            price=Decimal('1000.00'),
            category=self.category
        )

        self.client.force_authenticate(user=self.admin)

        data = {
            'name': 'Оновлена послуга',
            'price': '1200.00'
        }

        url = f'/api/admin/{service.id}/update_service/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Оновлена послуга')

    def test_delete_service(self):
        """Перевірка видалення послуги"""
        service = Service.objects.create(
            name='Послуга для видалення',
            price=Decimal('1000.00'),
            category=self.category
        )

        self.client.force_authenticate(user=self.admin)

        url = f'/api/admin/{service.id}/delete_service/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('видалено', response.data['message'].lower())

        # Перевіряємо що послуга видалена
        self.assertFalse(Service.objects.filter(id=service.id).exists())

    def test_toggle_service_status(self):
        """Перевірка зміни статусу послуги"""
        service = Service.objects.create(
            name='Послуга',
            price=Decimal('1000.00'),
            category=self.category,
            is_active=True
        )

        self.client.force_authenticate(user=self.admin)

        url = f'/api/admin/{service.id}/toggle_service_status/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])

        # Перевіряємо що статус змінився
        service.refresh_from_db()
        self.assertFalse(service.is_active)


class AdminAppointmentsManagementTest(TestCase):
    """Тести для управління записами"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
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

    def test_get_appointments_with_filters(self):
        """Перевірка отримання записів з фільтрами"""
        # Створюємо записи
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(11, 0),
            status='confirmed',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.admin)

        # Фільтр по статусу
        url = '/api/admin/appointments/?status=pending'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')

    def test_confirm_appointment(self):
        """Перевірка підтвердження запису"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.admin)

        url = f'/api/appointments/{appointment.id}/confirm/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('підтверджено', response.data['message'].lower())

        # Перевіряємо що статус змінився
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'confirmed')

    def test_complete_appointment(self):
        """Перевірка завершення запису"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='confirmed',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.admin)

        url = f'/api/appointments/{appointment.id}/complete/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('завершено', response.data['message'].lower())

        # Перевіряємо що статус змінився
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')

    def test_cancel_appointment_by_admin(self):
        """Перевірка скасування запису адміністратором"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            status='confirmed',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.admin)

        url = f'/api/admin/{appointment.id}/cancel_appointment/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('скасовано', response.data['message'].lower())

        # Перевіряємо що статус змінився
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled_by_admin')

    def test_get_weekly_schedule(self):
        """Перевірка отримання тижневого розкладу"""
        # Створюємо записи на цей тиждень
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=start_of_week,
            appointment_time=time(10, 0),
            status='confirmed',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.admin)

        url = '/api/admin/weekly_schedule/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('schedule', response.data)
        self.assertIn('week_start', response.data)

    def test_get_categories_management(self):
        """Перевірка отримання списку категорій для управління"""
        ServiceCategory.objects.create(
            name='Категорія',
            name_en='Category',
            order=1
        )

        self.client.force_authenticate(user=self.admin)

        url = '/api/admin/categories_management/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_create_category(self):
        """Перевірка створення категорії"""
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': 'Нова категорія',
            'name_en': 'New Category',
            'description': 'Опис',
            'description_en': 'Description',
            'order': 1
        }

        url = '/api/admin/create_category/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Нова категорія')

    def test_get_boxes_management(self):
        """Перевірка отримання списку боксів"""
        Box.objects.create(
            name='Бокс 1',
            working_hours={'monday': {'start': '08:00', 'end': '18:00'}},
            is_active=True
        )

        self.client.force_authenticate(user=self.admin)

        url = '/api/admin/boxes_management/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_home_page_management(self):
        """Перевірка отримання інформації про головну сторінку"""
        STOInfo.objects.create(
            name='СТО Test',
            description='Опис',
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

        self.client.force_authenticate(user=self.admin)

        url = '/api/admin/home_page_management/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'СТО Test')

    def test_get_appointment_details(self):
        """Перевірка отримання деталей запису"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.admin)

        url = f'/api/admin/{appointment.id}/appointment_details/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], appointment.id)
        self.assertEqual(response.data['status'], 'pending')

