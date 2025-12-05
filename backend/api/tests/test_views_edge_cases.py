"""
Тести для edge cases та помилкових сценаріїв в views.
Покриває непокриті частини views.py.
"""

from decimal import Decimal
from datetime import date, time, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from backend.api.models import (
    ServiceCategory, Service, Customer, Appointment, Box
)


class ViewsEdgeCasesTest(TestCase):
    """Тести для edge cases в views"""

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
            working_hours={'monday': {'start': '08:00', 'end': '18:00'}},
            is_active=True
        )

    def test_guest_appointment_blocked_user(self):
        """Перевірка створення запису гостя заблокованим користувачем"""
        self.customer.is_blocked = True
        self.customer.save()

        self.client.force_authenticate(user=self.user)

        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'guest_name': 'Guest',
            'guest_email': 'guest@example.com'
        }

        url = '/api/guest-appointments/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('заблокований', response.data['error'].lower())

    def test_update_appointment_wrong_owner(self):
        """Перевірка оновлення запису іншим користувачем"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_customer = Customer.objects.create(user=other_user)

        appointment = Appointment.objects.create(
            customer=other_customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=2),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.user)

        data = {
            'service_id': self.service.id,
            'appointment_date': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'appointment_time': '14:00'
        }

        url = f'/api/appointments/{appointment.id}/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_appointment_wrong_status(self):
        """Перевірка скасування запису з неправильним статусом"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='completed',  # Вже завершено
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/appointments/{appointment.id}/cancel/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('статус', response.data['error'].lower())

    def test_get_language_from_request_accept_language(self):
        """Перевірка отримання мови з Accept-Language заголовка"""
        from backend.api.views import get_language_from_request
        from unittest.mock import Mock

        request = Mock()
        request.query_params = {}
        request.META = {'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.9'}

        language = get_language_from_request(request)
        self.assertEqual(language, 'en')

    def test_get_language_from_request_default(self):
        """Перевірка отримання мови за замовчуванням"""
        from backend.api.views import get_language_from_request
        from unittest.mock import Mock

        request = Mock()
        request.query_params = {}
        request.META = {}

        language = get_language_from_request(request)
        self.assertEqual(language, 'uk')

    def test_box_available_boxes_missing_params(self):
        """Перевірка обробки відсутніх параметрів для available_boxes"""
        self.client.force_authenticate(user=self.user)

        url = '/api/boxes/available_boxes/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('параметри', response.data['error'].lower())

    def test_box_available_boxes_invalid_date(self):
        """Перевірка обробки невалідної дати"""
        self.client.force_authenticate(user=self.user)

        url = '/api/boxes/available_boxes/?date=invalid&time=10:00'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('формат', response.data['error'].lower())

    def test_update_profile_blocked_user(self):
        """Перевірка оновлення профілю заблокованим користувачем"""
        self.customer.is_blocked = True
        self.customer.save()

        self.client.force_authenticate(user=self.user)

        data = {'first_name': 'Updated'}
        url = '/api/customers/update_profile/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('заблокований', response.data['error'].lower())

    def test_get_profile_blocked_user(self):
        """Перевірка отримання профілю заблокованим користувачем"""
        self.customer.is_blocked = True
        self.customer.save()

        self.client.force_authenticate(user=self.user)

        url = '/api/customers/profile/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_blocked'])

    def test_admin_confirm_appointment_wrong_status(self):
        """Перевірка підтвердження запису з неправильним статусом"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            status='completed',  # Вже завершено
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/appointments/{appointment.id}/confirm/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('статус', response.data['error'].lower())

    def test_admin_complete_appointment_wrong_status(self):
        """Перевірка завершення запису з неправильним статусом"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',  # Не підтверджено
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/appointments/{appointment.id}/complete/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('статус', response.data['error'].lower())

    def test_admin_cancel_appointment_wrong_status(self):
        """Перевірка скасування запису адміном з неправильним статусом"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            status='completed',  # Вже завершено
            total_price=Decimal('1000.00')
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/admin/{appointment.id}/cancel_appointment/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('статус', response.data['error'].lower())

    def test_admin_update_customer_duplicate_email(self):
        """Перевірка оновлення клієнта з дублікатом email"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        other_customer = Customer.objects.create(user=other_user)

        self.client.force_authenticate(user=admin)

        data = {'email': 'other@example.com'}  # Вже використовується
        url = f'/api/admin/{self.customer.id}/update_customer/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('використовується', response.data['error'].lower())

    def test_admin_update_customer_invalid_password(self):
        """Перевірка оновлення клієнта з невалідним паролем"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        data = {'password': '123'}  # Занадто короткий
        url = f'/api/admin/{self.customer.id}/update_customer/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('пароль', response.data['error'].lower())

    def test_service_catalog_get_sto_info(self):
        """Перевірка отримання інформації про СТО через ServiceCatalog"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        sto_info = ServiceCatalog.get_sto_info()
        self.assertIsNotNone(sto_info)

    def test_service_catalog_update_sto_info(self):
        """Перевірка оновлення інформації про СТО"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        data = {
            'name': 'Оновлене СТО',
            'description': 'Новий опис',
            'address': 'Нова адреса',
            'phone': '+380501234567',
            'email': 'new@sto.com',
            'working_hours': 'Пн-Пт: 9:00-19:00'
        }

        result = ServiceCatalog.update_sto_info(data)
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['sto_info'])

    def test_admin_get_service_for_edit(self):
        """Перевірка отримання послуги для редагування"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/admin/{self.service.id}/get_service_for_edit/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.service.id)

    def test_admin_get_service_for_edit_not_exists(self):
        """Перевірка отримання неіснуючої послуги"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        url = '/api/admin/99999/get_service_for_edit/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_update_category(self):
        """Перевірка оновлення категорії"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        data = {
            'name': 'Оновлена категорія',
            'name_en': 'Updated Category',
            'order': 2
        }

        url = f'/api/admin/{self.category.id}/update_category/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Оновлена категорія')

    def test_admin_delete_category(self):
        """Перевірка видалення категорії"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        # Створюємо окрему категорію для видалення
        category_to_delete = ServiceCategory.objects.create(
            name='Категорія для видалення',
            order=99
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/admin/{category_to_delete.id}/delete_category/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ServiceCategory.objects.filter(id=category_to_delete.id).exists())

    def test_admin_create_box(self):
        """Перевірка створення боксу"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        data = {
            'name': 'Новий бокс',
            'name_en': 'New Box',
            'working_hours': {
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'}
            },
            'is_active': True
        }

        url = '/api/admin/create_box/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Новий бокс')

    def test_admin_update_box(self):
        """Перевірка оновлення боксу"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        data = {
            'name': 'Оновлений бокс',
            'working_hours': {
                'monday': {'start': '09:00', 'end': '19:00'}
            }
        }

        url = f'/api/admin/{self.box.id}/update_box/'
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Оновлений бокс')

    def test_admin_delete_box(self):
        """Перевірка видалення боксу"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        # Створюємо окремий бокс для видалення
        box_to_delete = Box.objects.create(
            name='Бокс для видалення',
            working_hours={'monday': {'start': '08:00', 'end': '18:00'}},
            is_active=True
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/admin/{box_to_delete.id}/delete_box/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Box.objects.filter(id=box_to_delete.id).exists())

    def test_admin_toggle_box_status(self):
        """Перевірка зміни статусу боксу"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/admin/{self.box.id}/toggle_box_status/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.box.refresh_from_db()
        self.assertFalse(self.box.is_active)

    def test_admin_update_home_page(self):
        """Перевірка оновлення головної сторінки"""
        from backend.api.models import STOInfo

        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        STOInfo.objects.create(
            name='СТО Test',
            description='Опис',
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

        self.client.force_authenticate(user=admin)

        data = {
            'name': 'Оновлене СТО',
            'description': 'Новий опис',
            'address': 'Нова адреса'
        }

        url = '/api/admin/update_home_page/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Оновлене СТО')

    def test_admin_featured_services(self):
        """Перевірка отримання основних послуг"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        # Створюємо рекомендовану послугу
        featured_service = Service.objects.create(
            name='Рекомендована',
            name_en='Featured',
            price=Decimal('2000.00'),
            category=self.category,
            is_featured=True,
            is_active=True
        )

        self.client.force_authenticate(user=admin)

        url = '/api/admin/featured_services/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_admin_toggle_featured_service(self):
        """Перевірка зміни статусу основної послуги"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        url = f'/api/admin/{self.service.id}/toggle_featured_service/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.service.refresh_from_db()
        self.assertTrue(self.service.is_featured)

    def test_admin_appointments_filters(self):
        """Перевірка фільтрів для записів"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        # Створюємо записи з різними параметрами
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
            total_price=Decimal('1500.00')
        )

        self.client.force_authenticate(user=admin)

        # Фільтр по даті
        url = f'/api/admin/appointments/?date_from={date.today().strftime("%Y-%m-%d")}&date_to={date.today().strftime("%Y-%m-%d")}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Фільтр по боксу
        url = f'/api/admin/appointments/?box_id={self.box.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Фільтр по послузі
        url = f'/api/admin/appointments/?service_id={self.service.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Фільтр по ціні
        url = '/api/admin/appointments/?price_min=1200&price_max=2000'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

