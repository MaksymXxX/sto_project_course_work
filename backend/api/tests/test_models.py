"""
Юніт-тести для моделей даних.
Перевіряють ізольовану роботу методів моделей без залучення зовнішніх систем.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, time
import json

from backend.api.models import (
    ServiceCategory, Service, Customer, Appointment,
    Box, STOInfo, ServiceHistory, LoyaltyTransaction
)


class ServiceCategoryModelTest(TestCase):
    """Тести для моделі ServiceCategory"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.category = ServiceCategory.objects.create(
            name='Технічне обслуговування',
            name_en='Technical Maintenance',
            description='Повне технічне обслуговування автомобіля',
            description_en='Full technical maintenance of the vehicle',
            order=1
        )

    def test_category_creation(self):
        """Перевірка створення категорії"""
        self.assertEqual(self.category.name, 'Технічне обслуговування')
        self.assertEqual(self.category.name_en, 'Technical Maintenance')
        self.assertEqual(self.category.order, 1)

    def test_get_name_ukrainian(self):
        """Перевірка отримання назви українською мовою"""
        name = self.category.get_name('uk')
        self.assertEqual(name, 'Технічне обслуговування')

    def test_get_name_english(self):
        """Перевірка отримання назви англійською мовою"""
        name = self.category.get_name('en')
        self.assertEqual(name, 'Technical Maintenance')

    def test_get_name_fallback(self):
        """Перевірка fallback на українську, якщо англійська відсутня"""
        category_no_en = ServiceCategory.objects.create(
            name='Діагностика',
            order=2
        )
        name = category_no_en.get_name('en')
        self.assertEqual(name, 'Діагностика')  # Fallback на українську

    def test_get_description_ukrainian(self):
        """Перевірка отримання опису українською мовою"""
        desc = self.category.get_description('uk')
        self.assertIn('технічне обслуговування', desc.lower())

    def test_get_description_english(self):
        """Перевірка отримання опису англійською мовою"""
        desc = self.category.get_description('en')
        self.assertIn('technical maintenance', desc.lower())

    def test_category_str_representation(self):
        """Перевірка строкового представлення"""
        self.assertEqual(str(self.category), 'Технічне обслуговування')

    def test_category_ordering(self):
        """Перевірка сортування категорій"""
        category2 = ServiceCategory.objects.create(
            name='Діагностика',
            order=2
        )
        categories = list(ServiceCategory.objects.all())
        self.assertEqual(categories[0].order, 1)
        self.assertEqual(categories[1].order, 2)


class ServiceModelTest(TestCase):
    """Тести для моделі Service"""

    def setUp(self):
        """Налаштування тестових даних"""
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

    def test_service_creation(self):
        """Перевірка створення послуги"""
        self.assertEqual(self.service.name, 'Повне ТО')
        self.assertEqual(self.service.price, Decimal('1500.00'))
        self.assertEqual(self.service.duration_minutes, 120)
        self.assertTrue(self.service.is_active)
        self.assertTrue(self.service.is_featured)

    def test_service_price_validation(self):
        """Перевірка що ціна не може бути від'ємною"""
        # Django DecimalField автоматично перевіряє це
        with self.assertRaises(Exception):
            Service.objects.create(
                name='Тест',
                price=Decimal('-100.00'),
                category=self.category
            )

    def test_get_name_ukrainian(self):
        """Перевірка отримання назви українською"""
        name = self.service.get_name('uk')
        self.assertEqual(name, 'Повне ТО')

    def test_get_name_english(self):
        """Перевірка отримання назви англійською"""
        name = self.service.get_name('en')
        self.assertEqual(name, 'Full Technical Maintenance')

    def test_service_str_representation(self):
        """Перевірка строкового представлення"""
        self.assertEqual(str(self.service), 'Повне ТО')

    def test_service_default_duration(self):
        """Перевірка значення за замовчуванням для тривалості"""
        service = Service.objects.create(
            name='Тест',
            price=Decimal('100.00'),
            category=self.category
        )
        # Значення за замовчуванням
        self.assertEqual(service.duration_minutes, 60)


class BoxModelTest(TestCase):
    """Тести для моделі Box"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.working_hours = {
            'monday': {'start': '08:00', 'end': '18:00'},
            'tuesday': {'start': '08:00', 'end': '18:00'},
            'wednesday': {'start': '08:00', 'end': '18:00'},
            'thursday': {'start': '08:00', 'end': '18:00'},
            'friday': {'start': '08:00', 'end': '18:00'},
            'saturday': {'start': '09:00', 'end': '15:00'},
            'sunday': {'start': '00:00', 'end': '00:00'}  # Вихідний
        }
        self.box = Box.objects.create(
            name='Бокс 1',
            name_en='Box 1',
            description='Бокс для ТО та ремонту',
            description_en='Box for maintenance and repair',
            is_active=True,
            working_hours=self.working_hours
        )

    def test_box_creation(self):
        """Перевірка створення боксу"""
        self.assertEqual(self.box.name, 'Бокс 1')
        self.assertTrue(self.box.is_active)
        self.assertIsInstance(self.box.working_hours, dict)

    def test_get_working_hours_for_day(self):
        """Перевірка отримання графіку роботи для дня"""
        monday_hours = self.box.get_working_hours_for_day('monday')
        self.assertEqual(monday_hours['start'], '08:00')
        self.assertEqual(monday_hours['end'], '18:00')

    def test_get_working_hours_for_weekend(self):
        """Перевірка графіку для вихідного дня"""
        sunday_hours = self.box.get_working_hours_for_day('sunday')
        self.assertEqual(sunday_hours['start'], '00:00')
        self.assertEqual(sunday_hours['end'], '00:00')

    def test_is_available_at_time_working_day(self):
        """Перевірка доступності боксу в робочий час"""
        test_date = date(2024, 1, 15)  # Понеділок
        test_time = time(10, 0)  # 10:00
        self.assertTrue(self.box.is_available_at_time(test_date, test_time))

    def test_is_available_at_time_after_hours(self):
        """Перевірка доступності боксу після робочих годин"""
        test_date = date(2024, 1, 15)  # Понеділок
        test_time = time(20, 0)  # 20:00
        self.assertFalse(self.box.is_available_at_time(test_date, test_time))

    def test_is_available_at_time_weekend(self):
        """Перевірка доступності боксу у вихідний день"""
        test_date = date(2024, 1, 14)  # Неділя
        test_time = time(10, 0)  # 10:00
        self.assertFalse(self.box.is_available_at_time(test_date, test_time))

    def test_get_name_multilingual(self):
        """Перевірка отримання назви за мовою"""
        self.assertEqual(self.box.get_name('uk'), 'Бокс 1')
        self.assertEqual(self.box.get_name('en'), 'Box 1')


class CustomerModelTest(TestCase):
    """Тести для моделі Customer"""

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
            address='Test Address 123',
            loyalty_points=100
        )

    def test_customer_creation(self):
        """Перевірка створення клієнта"""
        self.assertEqual(self.customer.user, self.user)
        self.assertEqual(self.customer.loyalty_points, 100)
        self.assertFalse(self.customer.is_blocked)

    def test_customer_str_representation(self):
        """Перевірка строкового представлення"""
        self.assertEqual(str(self.customer), 'Test User')

    def test_calculate_discount_percentage_no_appointments(self):
        """Перевірка розрахунку знижки без завершених записів"""
        discount = self.customer.calculate_discount_percentage()
        self.assertEqual(discount, 0)

    def test_calculate_discount_percentage_with_appointments(self):
        """Перевірка розрахунку знижки з завершеними записами"""
        # Створюємо категорію та послугу
        category = ServiceCategory.objects.create(name='Тест', order=1)
        service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=category
        )

        # Створюємо 5 завершених записів (має бути 2.5% знижка)
        for i in range(5):
            Appointment.objects.create(
                customer=self.customer,
                service=service,
                appointment_date=date.today(),
                appointment_time=time(10, 0),
                status='completed',
                total_price=Decimal('1000.00')
            )

        discount = self.customer.calculate_discount_percentage()
        self.assertEqual(discount, 2.5)  # 5 * 0.5% = 2.5%

    def test_calculate_discount_percentage_max_limit(self):
        """Перевірка максимальної знижки 10%"""
        category = ServiceCategory.objects.create(name='Тест', order=1)
        service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=category
        )

        # Створюємо 25 завершених записів (має бути максимум 10%)
        for i in range(25):
            Appointment.objects.create(
                customer=self.customer,
                service=service,
                appointment_date=date.today(),
                appointment_time=time(10, 0),
                status='completed',
                total_price=Decimal('1000.00')
            )

        discount = self.customer.calculate_discount_percentage()
        self.assertEqual(discount, 10.0)  # Максимум 10%

    def test_apply_discount_to_price(self):
        """Перевірка застосування знижки до ціни"""
        # Створюємо 4 завершених записів (2% знижка)
        category = ServiceCategory.objects.create(name='Тест', order=1)
        service = Service.objects.create(
            name='Тестова послуга',
            price=Decimal('1000.00'),
            category=category
        )

        for i in range(4):
            Appointment.objects.create(
                customer=self.customer,
                service=service,
                appointment_date=date.today(),
                appointment_time=time(10, 0),
                status='completed',
                total_price=Decimal('1000.00')
            )

        original_price = Decimal('1000.00')
        final_price = self.customer.apply_discount_to_price(original_price)
        expected_price = Decimal('980.00')  # 1000 - 2% = 980
        self.assertEqual(final_price, expected_price)

    def test_customer_blocking(self):
        """Перевірка блокування клієнта"""
        self.assertFalse(self.customer.is_blocked)
        self.customer.is_blocked = True
        self.customer.save()
        self.assertTrue(self.customer.is_blocked)


class AppointmentModelTest(TestCase):
    """Тести для моделі Appointment"""

    def setUp(self):
        """Налаштування тестових даних"""
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

    def test_appointment_creation(self):
        """Перевірка створення запису"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date(2024, 1, 15),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )
        self.assertEqual(appointment.status, 'pending')
        self.assertEqual(appointment.total_price, Decimal('1000.00'))

    def test_appointment_auto_total_price(self):
        """Перевірка автоматичного встановлення ціни"""
        appointment = Appointment(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date(2024, 1, 15),
            appointment_time=time(10, 0),
            status='pending'
        )
        # До збереження total_price не встановлено
        self.assertIsNone(appointment.total_price)
        appointment.save()
        # Після збереження total_price = service.price
        self.assertEqual(appointment.total_price, self.service.price)

    def test_appointment_str_representation(self):
        """Перевірка строкового представлення"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date(2024, 1, 15),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )
        self.assertIn('testuser', str(appointment).lower())
        self.assertIn('тестова послуга', str(appointment).lower())

    def test_guest_appointment_creation(self):
        """Перевірка створення запису для гостя"""
        appointment = Appointment.objects.create(
            guest_name='Guest User',
            guest_phone='+380501234567',
            guest_email='guest@example.com',
            service=self.service,
            box=self.box,
            appointment_date=date(2024, 1, 15),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )
        self.assertIsNone(appointment.customer)
        self.assertEqual(appointment.guest_name, 'Guest User')
        self.assertEqual(appointment.guest_email, 'guest@example.com')

    def test_appointment_status_choices(self):
        """Перевірка валідних статусів запису"""
        valid_statuses = ['pending', 'confirmed', 'in_progress', 'completed',
                          'cancelled', 'cancelled_by_admin']
        for status in valid_statuses:
            appointment = Appointment.objects.create(
                customer=self.customer,
                service=self.service,
                box=self.box,
                appointment_date=date(2024, 1, 15),
                appointment_time=time(10, 0),
                status=status,
                total_price=Decimal('1000.00')
            )
            self.assertEqual(appointment.status, status)


class STOInfoModelTest(TestCase):
    """Тести для моделі STOInfo"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.sto_info = STOInfo.objects.create(
            name='СТО AutoServis',
            name_en='Auto Service AutoServis',
            description='Найкращий сервіс',
            description_en='Best service',
            motto='Якість та надійність',
            motto_en='Quality and reliability',
            welcome_text='Ласкаво просимо',
            welcome_text_en='Welcome',
            what_you_can_title='У нас ви можете',
            what_you_can_title_en='What you can',
            what_you_can_items=['Послуга 1', 'Послуга 2'],
            what_you_can_items_en=['Service 1', 'Service 2'],
            address='Вул. Тестова, 1',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

    def test_sto_info_creation(self):
        """Перевірка створення інформації про СТО"""
        self.assertEqual(self.sto_info.name, 'СТО AutoServis')
        self.assertTrue(self.sto_info.is_active)

    def test_get_name_multilingual(self):
        """Перевірка отримання назви за мовою"""
        self.assertEqual(self.sto_info.get_name('uk'), 'СТО AutoServis')
        self.assertEqual(self.sto_info.get_name(
            'en'), 'Auto Service AutoServis')

    def test_get_what_you_can_items_list(self):
        """Перевірка отримання списку пунктів"""
        items_uk = self.sto_info.get_what_you_can_items_list('uk')
        self.assertEqual(len(items_uk), 2)
        self.assertIn('Послуга 1', items_uk)

        items_en = self.sto_info.get_what_you_can_items_list('en')
        self.assertEqual(len(items_en), 2)
        self.assertIn('Service 1', items_en)

    def test_set_what_you_can_items_list(self):
        """Перевірка встановлення списку пунктів"""
        new_items = ['Новий пункт 1', 'Новий пункт 2']
        self.sto_info.set_what_you_can_items_list(new_items, 'uk')
        self.sto_info.save()
        items = self.sto_info.get_what_you_can_items_list('uk')
        self.assertEqual(items, new_items)
