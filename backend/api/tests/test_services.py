"""
Юніт-тести для сервісного шару.
Перевіряють бізнес-логіку без залучення бази даних та зовнішніх залежностей.
"""

from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock

from backend.api.models import (
    ServiceCategory, Service, Customer, Appointment, Box
)
from backend.services.appointment_service.appointment_service import (
    AppointmentService
)
from backend.services.auth_service.auth_service import AuthorizationService
from backend.services.user_service.user_service import UserService


class AppointmentServiceTest(TestCase):
    """Тести для AppointmentService"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.customer = Customer.objects.create(user=self.user)
        self.category = ServiceCategory.objects.create(
            name='Тестова категорія',
            order=1
        )
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
                'tuesday': {'start': '08:00', 'end': '18:00'},
                'wednesday': {'start': '08:00', 'end': '18:00'},
                'thursday': {'start': '08:00', 'end': '18:00'},
                'friday': {'start': '08:00', 'end': '18:00'},
                'saturday': {'start': '09:00', 'end': '15:00'},
                'sunday': {'start': '00:00', 'end': '00:00'}
            },
            is_active=True
        )

    def test_create_appointment_success(self):
        """Перевірка успішного створення запису"""
        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'notes': 'Тестова примітка'
        }

        result = AppointmentService.create_appointment(data, self.user)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['appointment'])
        self.assertEqual(result['appointment'].service, self.service)
        self.assertEqual(result['appointment'].customer, self.customer)

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

        tomorrow = date.today() + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00'
        }

        result = AppointmentService.create_appointment(data, self.user)

        self.assertTrue(result['success'])
        # Ціна має бути зі знижкою 2%
        expected_price = Decimal('980.00')  # 1000 - 2%
        self.assertEqual(result['appointment'].total_price, expected_price)

    def test_create_appointment_no_available_box(self):
        """Перевірка обробки відсутності вільних боксів"""
        # Заповнюємо всі бокси
        tomorrow = date.today() + timedelta(days=1)
        for hour in range(8, 18):
            Appointment.objects.create(
                customer=self.customer,
                service=self.service,
                box=self.box,
                appointment_date=tomorrow,
                appointment_time=time(hour, 0),
                status='confirmed',
                total_price=Decimal('1000.00')
            )

        data = {
            'service_id': self.service.id,
            'appointment_date': tomorrow.strftime('%Y-%m-%d'),
            'appointment_time': '10:00'
        }

        result = AppointmentService.create_appointment(data, self.user)

        self.assertFalse(result['success'])
        self.assertIn('немає доступних боксів', result['error'].lower())

    def test_create_appointment_invalid_service(self):
        """Перевірка обробки невалідної послуги"""
        data = {
            'service_id': 99999,  # Неіснуюча послуга
            'appointment_date': '2024-12-31',
            'appointment_time': '10:00'
        }

        result = AppointmentService.create_appointment(data, self.user)

        self.assertFalse(result['success'])
        self.assertIn('не знайдено', result['error'].lower())

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

        result = AppointmentService.create_appointment(data, None)

        self.assertTrue(result['success'])
        self.assertIsNone(result['appointment'].customer)
        self.assertEqual(result['appointment'].guest_name, 'Guest User')
        self.assertEqual(
            result['appointment'].guest_email, 'guest@example.com')

    def test_update_appointment_success(self):
        """Перевірка успішного оновлення запису"""
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

        new_date = tomorrow + timedelta(days=1)
        data = {
            'service_id': self.service.id,
            'appointment_date': new_date.strftime('%Y-%m-%d'),
            'appointment_time': '14:00',
            'notes': 'Оновлена примітка'
        }

        result = AppointmentService.update_appointment(
            appointment.id, data, self.user)

        self.assertTrue(result['success'])
        self.assertEqual(
            result['appointment'].appointment_date, new_date)
        self.assertEqual(
            result['appointment'].appointment_time, time(14, 0))

    def test_update_appointment_too_soon(self):
        """Перевірка обмеження редагування менше ніж за 2 години"""
        # Створюємо запис через 1 годину
        future_time = timezone.now() + timedelta(hours=1)
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=future_time.date(),
            appointment_time=future_time.time(),
            status='pending',
            total_price=Decimal('1000.00')
        )

        data = {
            'service_id': self.service.id,
            'appointment_date': future_time.date().strftime('%Y-%m-%d'),
            'appointment_time': future_time.time().strftime('%H:%M')
        }

        result = AppointmentService.update_appointment(
            appointment.id, data, self.user)

        self.assertFalse(result['success'])
        self.assertIn('2 години', result['error'])

    def test_update_appointment_wrong_status(self):
        """Перевірка обмеження редагування запису з неправильним статусом"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today() + timedelta(days=2),
            appointment_time=time(10, 0),
            status='completed',  # Вже завершено
            total_price=Decimal('1000.00')
        )

        data = {
            'service_id': self.service.id,
            'appointment_date': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'appointment_time': '14:00'
        }

        result = AppointmentService.update_appointment(
            appointment.id, data, self.user)

        self.assertFalse(result['success'])
        self.assertIn('статус', result['error'].lower())

    def test_find_available_box(self):
        """Перевірка пошуку доступного боксу"""
        tomorrow = date.today() + timedelta(days=1)
        test_time = time(10, 0)

        box = AppointmentService._find_available_box(
            tomorrow, test_time, self.service)

        self.assertIsNotNone(box)
        self.assertEqual(box, self.box)

    def test_find_available_box_with_exclusion(self):
        """Перевірка пошуку боксу з виключенням існуючого запису"""
        tomorrow = date.today() + timedelta(days=1)
        test_time = time(10, 0)

        # Створюємо запис
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=tomorrow,
            appointment_time=test_time,
            status='confirmed',
            total_price=Decimal('1000.00')
        )

        # Шукаємо бокс, виключаючи поточний запис
        box = AppointmentService._find_available_box(
            tomorrow, test_time, self.service, appointment.id)

        # Має знайти той самий бокс, оскільки виключили поточний запис
        self.assertIsNotNone(box)

    def test_get_user_appointments(self):
        """Перевірка отримання записів користувача"""
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

        appointments = AppointmentService.get_user_appointments(self.user)

        self.assertEqual(appointments.count(), 3)


class AuthorizationServiceTest(TestCase):
    """Тести для AuthorizationService"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_register_user_success(self):
        """Перевірка успішної реєстрації користувача"""
        result = AuthorizationService.register_user(self.user_data)

        self.assertTrue(result['success'])
        self.assertIn('access', result)
        self.assertIn('refresh', result)
        self.assertEqual(result['user']['email'], 'test@example.com')
        self.assertEqual(result['user']['username'], 'testuser')

        # Перевіряємо що створився Customer профіль
        user = User.objects.get(email='test@example.com')
        self.assertTrue(hasattr(user, 'customer'))

    def test_register_user_duplicate_email(self):
        """Перевірка обробки дублікату email"""
        # Створюємо першого користувача
        AuthorizationService.register_user(self.user_data)

        # Спробуємо створити другого з тим самим email
        result = AuthorizationService.register_user(self.user_data)

        self.assertFalse(result['success'])
        self.assertIn('вже існує', result['error'].lower())

    def test_register_user_invalid_email(self):
        """Перевірка валідації email"""
        invalid_data = {
            'email': 'invalid-email',
            'password': 'testpass123'
        }

        result = AuthorizationService.register_user(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('email', result['error'].lower())

    def test_register_user_short_password(self):
        """Перевірка валідації короткого пароля"""
        invalid_data = {
            'email': 'test@example.com',
            'password': '12345'  # Менше 6 символів
        }

        result = AuthorizationService.register_user(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('6 символів', result['error'])

    def test_register_user_missing_fields(self):
        """Перевірка обробки відсутніх полів"""
        incomplete_data = {
            'email': 'test@example.com'
            # Відсутній пароль
        }

        result = AuthorizationService.register_user(incomplete_data)

        self.assertFalse(result['success'])
        self.assertIn('поля', result['error'].lower())

    def test_login_user_success(self):
        """Перевірка успішного входу"""
        # Спочатку реєструємо користувача
        AuthorizationService.register_user(self.user_data)

        # Потім входимо
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        result = AuthorizationService.login_user(login_data)

        self.assertTrue(result['success'])
        self.assertIn('access', result)
        self.assertIn('refresh', result)

    def test_login_user_wrong_password(self):
        """Перевірка обробки неправильного пароля"""
        # Реєструємо користувача
        AuthorizationService.register_user(self.user_data)

        # Входимо з неправильним паролем
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        result = AuthorizationService.login_user(login_data)

        self.assertFalse(result['success'])
        self.assertIn('пароль', result['error'].lower())

    def test_login_user_nonexistent(self):
        """Перевірка обробки неіснуючого користувача"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }

        result = AuthorizationService.login_user(login_data)

        self.assertFalse(result['success'])
        self.assertIn('не знайдено', result['error'].lower())

    def test_authenticate_user_success(self):
        """Перевірка успішної аутентифікації"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        result = AuthorizationService.authenticate_user(
            'testuser', 'testpass123')

        self.assertTrue(result['success'])
        self.assertIn('access', result)

    def test_authenticate_user_failure(self):
        """Перевірка невдалої аутентифікації"""
        result = AuthorizationService.authenticate_user(
            'nonexistent', 'wrongpass')

        self.assertFalse(result['success'])
        self.assertIn('облікові дані', result['error'].lower())

    def test_verify_token_valid(self):
        """Перевірка валідації валідного токена"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        result = AuthorizationService.verify_token(token)

        self.assertTrue(result['success'])
        self.assertEqual(result['user']['id'], user.id)

    def test_verify_token_invalid(self):
        """Перевірка обробки невалідного токена"""
        result = AuthorizationService.verify_token('invalid_token')

        self.assertFalse(result['success'])
        self.assertIn('токен', result['error'].lower())

    def test_check_permissions_authenticated(self):
        """Перевірка прав доступу для авторизованого користувача"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        result = AuthorizationService.check_permissions(user)
        self.assertTrue(result)

    def test_check_permissions_admin(self):
        """Перевірка прав адміністратора"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        result = AuthorizationService.check_permissions(admin, 'admin')
        self.assertTrue(result)

    def test_check_permissions_non_admin(self):
        """Перевірка відсутності прав адміністратора"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        result = AuthorizationService.check_permissions(user, 'admin')
        self.assertFalse(result)


class UserServiceTest(TestCase):
    """Тести для UserService"""

    def setUp(self):
        """Налаштування тестових даних"""
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
            loyalty_points=50
        )

    def test_get_user_profile_success(self):
        """Перевірка отримання профілю користувача"""
        profile = UserService.get_user_profile(self.user)

        self.assertIsNotNone(profile)
        self.assertEqual(profile['user']['email'], 'test@example.com')
        self.assertEqual(profile['user']['first_name'], 'Test')
        self.assertEqual(profile['loyalty_points'], 50)
        self.assertEqual(profile['address'], 'Test Address')

    def test_get_user_profile_nonexistent(self):
        """Перевірка отримання профілю неіснуючого користувача"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )

        profile = UserService.get_user_profile(new_user)

        self.assertIsNone(profile)  # Customer профіль не створено

    def test_get_user_profile_with_completed_appointments(self):
        """Перевірка підрахунку завершених записів"""
        category = ServiceCategory.objects.create(name='Тест', order=1)
        service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=category
        )
        box = Box.objects.create(
            name='Бокс 1',
            working_hours={'monday': {'start': '08:00', 'end': '18:00'}},
            is_active=True
        )

        # Створюємо 3 завершених записів
        for i in range(3):
            Appointment.objects.create(
                customer=self.customer,
                service=service,
                box=box,
                appointment_date=date.today(),
                appointment_time=time(10, 0),
                status='completed',
                total_price=Decimal('1000.00')
            )

        profile = UserService.get_user_profile(self.user)

        self.assertEqual(profile['completed_appointments_count'], 3)

    def test_update_user_profile_success(self):
        """Перевірка успішного оновлення профілю"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'address': 'New Address'
        }

        updated_profile = UserService.update_user_profile(
            self.user, update_data)

        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile['user']['first_name'], 'Updated')
        self.assertEqual(updated_profile['user']['last_name'], 'Name')
        self.assertEqual(updated_profile['user']
                         ['email'], 'updated@example.com')
        self.assertEqual(updated_profile['address'], 'New Address')

        # Перевіряємо що дані оновилися в БД
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.address, 'New Address')

    def test_update_user_profile_duplicate_email(self):
        """Перевірка обробки дублікату email"""
        # Створюємо іншого користувача
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        # Спробуємо оновити email на вже існуючий
        update_data = {
            'email': 'other@example.com'
        }

        result = UserService.update_user_profile(self.user, update_data)

        self.assertIsNone(result)  # Повертає None при дублікаті

    def test_update_user_profile_password(self):
        """Перевірка оновлення пароля"""
        update_data = {
            'password': 'newpassword123'
        }

        updated_profile = UserService.update_user_profile(
            self.user, update_data)

        self.assertIsNotNone(updated_profile)

        # Перевіряємо що пароль змінився
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_update_user_profile_invalid_password(self):
        """Перевірка обробки невалідного пароля"""
        update_data = {
            'password': '123'  # Занадто короткий
        }

        result = UserService.update_user_profile(self.user, update_data)

        self.assertIsNotNone(result)
        self.assertIn('error', result)
        self.assertIn('пароль', result['error'].lower())

    def test_get_all_customers(self):
        """Перевірка отримання всіх клієнтів"""
        # Створюємо ще одного користувача
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        Customer.objects.create(user=user2)

        customers = UserService.get_all_customers()

        self.assertEqual(len(customers), 2)
        emails = [c['user']['email'] for c in customers]
        self.assertIn('test@example.com', emails)
        self.assertIn('user2@example.com', emails)

    def test_block_customer(self):
        """Перевірка блокування клієнта"""
        result = UserService.block_customer(self.customer.id)

        self.assertTrue(result)

        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_blocked)

    def test_unblock_customer(self):
        """Перевірка розблокування клієнта"""
        # Спочатку блокуємо
        self.customer.is_blocked = True
        self.customer.save()

        # Потім розблоковуємо
        result = UserService.unblock_customer(self.customer.id)

        self.assertTrue(result)

        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_blocked)

    def test_block_nonexistent_customer(self):
        """Перевірка блокування неіснуючого клієнта"""
        result = UserService.block_customer(99999)

        self.assertFalse(result)


class ServiceCatalogTest(TestCase):
    """Тести для ServiceCatalog"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.category = ServiceCategory.objects.create(name='Тест', order=1)
        self.service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=self.category,
            is_active=True
        )

    def test_get_all_services(self):
        """Перевірка отримання всіх послуг"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        services = ServiceCatalog.get_all_services()
        self.assertGreater(services.count(), 0)

    def test_get_service_by_id(self):
        """Перевірка отримання послуги за ID"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        service = ServiceCatalog.get_service_by_id(self.service.id)
        self.assertIsNotNone(service)
        self.assertEqual(service, self.service)

    def test_get_service_by_id_not_exists(self):
        """Перевірка отримання неіснуючої послуги"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        service = ServiceCatalog.get_service_by_id(99999)
        self.assertIsNone(service)

    def test_create_service_success(self):
        """Перевірка створення послуги"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        data = {
            'name': 'Нова послуга',
            'description': 'Опис',
            'price': Decimal('1500.00'),
            'duration': 90,
            'is_active': True
        }

        result = ServiceCatalog.create_service(data)
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['service'])

    def test_create_service_error(self):
        """Перевірка обробки помилки при створенні послуги"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        # Невалідні дані (відсутня категорія)
        data = {
            'name': 'Послуга',
            'price': Decimal('1000.00')
            # Відсутні обов'язкові поля
        }

        result = ServiceCatalog.create_service(data)
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_update_service_success(self):
        """Перевірка оновлення послуги"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        data = {'price': Decimal('2000.00')}
        result = ServiceCatalog.update_service(self.service.id, data)

        self.assertTrue(result['success'])
        self.service.refresh_from_db()
        self.assertEqual(self.service.price, Decimal('2000.00'))

    def test_update_service_not_exists(self):
        """Перевірка оновлення неіснуючої послуги"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        data = {'price': Decimal('2000.00')}
        result = ServiceCatalog.update_service(99999, data)

        self.assertFalse(result['success'])
        self.assertIn('не знайдено', result['error'].lower())

    def test_delete_service_success(self):
        """Перевірка видалення (деактивації) послуги"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        result = ServiceCatalog.delete_service(self.service.id)

        self.assertTrue(result)
        self.service.refresh_from_db()
        self.assertFalse(self.service.is_active)

    def test_delete_service_not_exists(self):
        """Перевірка видалення неіснуючої послуги"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog

        result = ServiceCatalog.delete_service(99999)
        self.assertFalse(result)

    def test_update_sto_info_with_items(self):
        """Перевірка оновлення STOInfo з what_you_can_items"""
        from backend.services.service_catalog.service_catalog import ServiceCatalog
        from backend.api.models import STOInfo

        STOInfo.objects.create(
            name='СТО Test',
            description='Опис',
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

        data = {
            # З порожніми
            'what_you_can_items': ['Пункт 1', 'Пункт 2', '', '   ']
        }

        result = ServiceCatalog.update_sto_info(data)
        self.assertTrue(result['success'])

        # Перевіряємо що порожні елементи відфільтровані
        sto_info = STOInfo.objects.first()
        items = sto_info.get_what_you_can_items_list('uk')
        self.assertEqual(len(items), 2)  # Тільки 2 не порожніх
