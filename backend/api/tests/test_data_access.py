"""
Тести для Data Access Layer.
Перевіряють методи доступу до даних.
"""

from decimal import Decimal
from datetime import date, time
from django.test import TestCase
from django.contrib.auth.models import User

from backend.api.models import (
    ServiceCategory, Service, Customer, Appointment,
    ServiceHistory, LoyaltyTransaction, STOInfo, Box
)
from backend.api.data_access import DataAccessLayer


class DataAccessLayerTest(TestCase):
    """Тести для DataAccessLayer"""

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

    def test_get_customer_by_user(self):
        """Перевірка отримання клієнта за користувачем"""
        customer = DataAccessLayer.get_customer_by_user(self.user)
        self.assertIsNotNone(customer)
        self.assertEqual(customer, self.customer)

    def test_get_customer_by_user_not_exists(self):
        """Перевірка отримання клієнта який не існує"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        customer = DataAccessLayer.get_customer_by_user(new_user)
        self.assertIsNone(customer)

    def test_get_all_customers(self):
        """Перевірка отримання всіх клієнтів"""
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        Customer.objects.create(user=User.objects.get(username='user2'))

        customers = DataAccessLayer.get_all_customers()
        self.assertGreaterEqual(customers.count(), 2)

    def test_create_customer(self):
        """Перевірка створення клієнта"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        customer = DataAccessLayer.create_customer(new_user, 'Test Address')
        self.assertIsNotNone(customer)
        self.assertEqual(customer.user, new_user)
        self.assertEqual(customer.address, 'Test Address')

    def test_update_customer(self):
        """Перевірка оновлення клієнта"""
        DataAccessLayer.update_customer(
            self.customer,
            address='New Address',
            loyalty_points=200
        )
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.address, 'New Address')
        self.assertEqual(self.customer.loyalty_points, 200)

    def test_get_all_services(self):
        """Перевірка отримання всіх активних послуг"""
        Service.objects.create(
            name='Неактивна послуга',
            price=Decimal('500.00'),
            category=self.category,
            is_active=False
        )

        services = DataAccessLayer.get_all_services()
        self.assertEqual(services.count(), 1)  # Тільки активна
        self.assertEqual(services.first(), self.service)

    def test_get_service_by_id(self):
        """Перевірка отримання послуги за ID"""
        service = DataAccessLayer.get_service_by_id(self.service.id)
        self.assertIsNotNone(service)
        self.assertEqual(service, self.service)

    def test_get_service_by_id_not_exists(self):
        """Перевірка отримання неіснуючої послуги"""
        service = DataAccessLayer.get_service_by_id(99999)
        self.assertIsNone(service)

    def test_create_service(self):
        """Перевірка створення послуги"""
        service = DataAccessLayer.create_service(
            name='Нова послуга',
            price=Decimal('2000.00'),
            category=self.category
        )
        self.assertIsNotNone(service)
        self.assertEqual(service.name, 'Нова послуга')

    def test_update_service(self):
        """Перевірка оновлення послуги"""
        DataAccessLayer.update_service(
            self.service,
            price=Decimal('1500.00'),
            is_active=False
        )
        self.service.refresh_from_db()
        self.assertEqual(self.service.price, Decimal('1500.00'))
        self.assertFalse(self.service.is_active)

    def test_get_appointments_by_user(self):
        """Перевірка отримання записів користувача"""
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        appointments = DataAccessLayer.get_appointments_by_user(self.user)
        self.assertEqual(appointments.count(), 1)

    def test_get_appointment_by_id(self):
        """Перевірка отримання запису за ID"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        result = DataAccessLayer.get_appointment_by_id(appointment.id, self.user)
        self.assertIsNotNone(result)
        self.assertEqual(result, appointment)

    def test_get_appointment_by_id_admin(self):
        """Перевірка отримання запису адміністратором"""
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
            status='pending',
            total_price=Decimal('1000.00')
        )

        result = DataAccessLayer.get_appointment_by_id(appointment.id, admin)
        self.assertIsNotNone(result)
        self.assertEqual(result, appointment)

    def test_get_appointment_by_id_guest(self):
        """Перевірка отримання запису гостя"""
        appointment = Appointment.objects.create(
            guest_name='Guest',
            guest_email='guest@example.com',
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        result = DataAccessLayer.get_appointment_by_id(appointment.id, None)
        self.assertIsNotNone(result)
        self.assertEqual(result, appointment)

    def test_create_appointment(self):
        """Перевірка створення запису"""
        appointment = DataAccessLayer.create_appointment(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.customer, self.customer)

    def test_update_appointment(self):
        """Перевірка оновлення запису"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        DataAccessLayer.update_appointment(
            appointment,
            status='confirmed',
            notes='Оновлена примітка'
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'confirmed')
        self.assertEqual(appointment.notes, 'Оновлена примітка')

    def test_update_appointment_by_id(self):
        """Перевірка оновлення запису за ID"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='pending',
            total_price=Decimal('1000.00')
        )

        result = DataAccessLayer.update_appointment_by_id(
            appointment.id,
            status='confirmed'
        )
        self.assertIsNotNone(result)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'confirmed')

    def test_update_appointment_by_id_not_exists(self):
        """Перевірка оновлення неіснуючого запису"""
        result = DataAccessLayer.update_appointment_by_id(99999, status='confirmed')
        self.assertIsNone(result)

    def test_get_service_history_by_user(self):
        """Перевірка отримання історії обслуговування"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='completed',
            total_price=Decimal('1000.00')
        )
        ServiceHistory.objects.create(
            appointment=appointment,
            actual_duration=60,
            final_price=Decimal('1000.00')
        )

        history = DataAccessLayer.get_service_history_by_user(self.user)
        self.assertEqual(history.count(), 1)

    def test_create_service_history(self):
        """Перевірка створення запису в історії"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='completed',
            total_price=Decimal('1000.00')
        )

        history = DataAccessLayer.create_service_history(
            appointment=appointment,
            actual_duration=60,
            final_price=Decimal('1000.00'),
            mechanic_notes='Все добре'
        )
        self.assertIsNotNone(history)
        self.assertEqual(history.appointment, appointment)

    def test_get_loyalty_transactions_by_user(self):
        """Перевірка отримання транзакцій лояльності"""
        LoyaltyTransaction.objects.create(
            customer=self.customer,
            transaction_type='earned',
            points=100,
            description='Тестова транзакція'
        )

        transactions = DataAccessLayer.get_loyalty_transactions_by_user(self.user)
        self.assertEqual(transactions.count(), 1)

    def test_create_loyalty_transaction(self):
        """Перевірка створення транзакції лояльності"""
        transaction = DataAccessLayer.create_loyalty_transaction(
            customer=self.customer,
            transaction_type='earned',
            points=100,
            description='Тестова транзакція'
        )
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.points, 100)

    def test_get_sto_info_exists(self):
        """Перевірка отримання інформації про СТО (якщо існує)"""
        STOInfo.objects.create(
            name='СТО Test',
            description='Опис',
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

        sto_info = DataAccessLayer.get_sto_info()
        self.assertIsNotNone(sto_info)
        self.assertEqual(sto_info.name, 'СТО Test')

    def test_get_sto_info_not_exists(self):
        """Перевірка отримання інформації про СТО (якщо не існує - створюється)"""
        # Видаляємо всі STOInfo
        STOInfo.objects.all().delete()

        sto_info = DataAccessLayer.get_sto_info()
        self.assertIsNotNone(sto_info)
        self.assertIsNotNone(sto_info.name)

    def test_create_or_update_sto_info_create(self):
        """Перевірка створення інформації про СТО"""
        STOInfo.objects.all().delete()

        sto_info = DataAccessLayer.create_or_update_sto_info(
            name='Нове СТО',
            description='Опис',
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )
        self.assertIsNotNone(sto_info)
        self.assertEqual(sto_info.name, 'Нове СТО')

    def test_create_or_update_sto_info_update(self):
        """Перевірка оновлення інформації про СТО"""
        STOInfo.objects.create(
            name='Старе СТО',
            description='Старий опис',
            address='Стара адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00',
            is_active=True
        )

        sto_info = DataAccessLayer.create_or_update_sto_info(
            name='Оновлене СТО',
            description='Новий опис'
        )
        self.assertIsNotNone(sto_info)
        self.assertEqual(sto_info.name, 'Оновлене СТО')
        self.assertEqual(sto_info.description, 'Новий опис')

    def test_get_appointments_count(self):
        """Перевірка отримання кількості записів"""
        for i in range(3):
            Appointment.objects.create(
                customer=self.customer,
                service=self.service,
                box=self.box,
                appointment_date=date.today(),
                appointment_time=time(10 + i, 0),
                status='pending',
                total_price=Decimal('1000.00')
            )

        count = DataAccessLayer.get_appointments_count()
        self.assertEqual(count, 3)

    def test_get_appointments_by_status(self):
        """Перевірка отримання записів за статусом"""
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

        pending = DataAccessLayer.get_appointments_by_status('pending')
        self.assertEqual(pending.count(), 1)

        completed = DataAccessLayer.get_appointments_by_status('completed')
        self.assertEqual(completed.count(), 1)

    def test_get_customers_count(self):
        """Перевірка отримання кількості клієнтів"""
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        Customer.objects.create(user=User.objects.get(username='user2'))

        count = DataAccessLayer.get_customers_count()
        self.assertEqual(count, 2)

    def test_get_blocked_customers_count(self):
        """Перевірка отримання кількості заблокованих клієнтів"""
        self.customer.is_blocked = True
        self.customer.save()

        count = DataAccessLayer.get_blocked_customers_count()
        self.assertEqual(count, 1)

    def test_get_services_count(self):
        """Перевірка отримання кількості активних послуг"""
        Service.objects.create(
            name='Неактивна',
            price=Decimal('500.00'),
            category=self.category,
            is_active=False
        )

        count = DataAccessLayer.get_services_count()
        self.assertEqual(count, 1)  # Тільки активна

    def test_get_total_revenue(self):
        """Перевірка отримання загального доходу"""
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='completed',
            total_price=Decimal('1000.00')
        )
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            box=self.box,
            appointment_date=date.today(),
            appointment_time=time(11, 0),
            status='completed',
            total_price=Decimal('1500.00')
        )

        revenue = DataAccessLayer.get_total_revenue()
        self.assertEqual(revenue, Decimal('2500.00'))

