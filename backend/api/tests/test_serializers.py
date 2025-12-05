"""
Юніт-тести для серіалізаторів.
Перевіряють коректність серіалізації та десеріалізації даних,
особливо багатомовність.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User

from backend.api.models import (
    ServiceCategory, Service, Customer, Box, STOInfo
)
from backend.api.serializers import (
    ServiceCategorySerializer, ServiceSerializer,
    BoxSerializer, STOInfoSerializer, CustomerSerializer
)


class ServiceCategorySerializerTest(TestCase):
    """Тести для ServiceCategorySerializer"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.category = ServiceCategory.objects.create(
            name='Технічне обслуговування',
            name_en='Technical Maintenance',
            description='Опис українською',
            description_en='Description in English',
            order=1
        )

    def test_serialization_ukrainian(self):
        """Перевірка серіалізації українською мовою"""
        serializer = ServiceCategorySerializer(
            self.category,
            context={'language': 'uk'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'Технічне обслуговування')
        self.assertEqual(data['description'], 'Опис українською')

    def test_serialization_english(self):
        """Перевірка серіалізації англійською мовою"""
        serializer = ServiceCategorySerializer(
            self.category,
            context={'language': 'en'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'Technical Maintenance')
        self.assertEqual(data['description'], 'Description in English')

    def test_serialization_admin_panel(self):
        """Перевірка серіалізації для адмін панелі (обидві мови)"""
        serializer = ServiceCategorySerializer(
            self.category,
            context={'language': 'uk', 'admin_panel': True}
        )
        data = serializer.data

        # В адмін панелі мають бути обидві мови
        self.assertEqual(data['name'], 'Технічне обслуговування')
        self.assertEqual(data['name_en'], 'Technical Maintenance')
        self.assertEqual(data['description'], 'Опис українською')
        self.assertEqual(data['description_en'], 'Description in English')

    def test_deserialization(self):
        """Перевірка десеріалізації"""
        data = {
            'name': 'Нова категорія',
            'name_en': 'New Category',
            'description': 'Опис',
            'description_en': 'Description',
            'order': 2
        }

        serializer = ServiceCategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())

        category = serializer.save()
        self.assertEqual(category.name, 'Нова категорія')
        self.assertEqual(category.name_en, 'New Category')


class ServiceSerializerTest(TestCase):
    """Тести для ServiceSerializer"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.category = ServiceCategory.objects.create(
            name='Категорія',
            name_en='Category',
            order=1
        )
        self.service = Service.objects.create(
            name='Послуга',
            name_en='Service',
            description='Опис',
            description_en='Description',
            price=Decimal('1000.00'),
            category=self.category,
            duration_minutes=60
        )

    def test_serialization_ukrainian(self):
        """Перевірка серіалізації українською"""
        serializer = ServiceSerializer(
            self.service,
            context={'language': 'uk'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'Послуга')
        self.assertEqual(data['description'], 'Опис')
        self.assertEqual(data['category']['name'], 'Категорія')

    def test_serialization_english(self):
        """Перевірка серіалізації англійською"""
        serializer = ServiceSerializer(
            self.service,
            context={'language': 'en'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'Service')
        self.assertEqual(data['description'], 'Description')
        self.assertEqual(data['category']['name'], 'Category')

    def test_serialization_admin_panel(self):
        """Перевірка серіалізації для адмін панелі"""
        serializer = ServiceSerializer(
            self.service,
            context={'language': 'uk', 'admin_panel': True}
        )
        data = serializer.data

        # В адмін панелі мають бути обидві мови
        self.assertEqual(data['name'], 'Послуга')
        self.assertEqual(data['name_en'], 'Service')
        self.assertEqual(data['category']['name'], 'Категорія')

    def test_deserialization(self):
        """Перевірка десеріалізації"""
        data = {
            'name': 'Нова послуга',
            'name_en': 'New Service',
            'description': 'Опис',
            'description_en': 'Description',
            'price': '1500.00',
            'category_id': self.category.id,
            'duration_minutes': 90
        }

        serializer = ServiceSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        service = serializer.save()
        self.assertEqual(service.name, 'Нова послуга')
        self.assertEqual(service.price, Decimal('1500.00'))


class BoxSerializerTest(TestCase):
    """Тести для BoxSerializer"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.working_hours = {
            'monday': {'start': '08:00', 'end': '18:00'},
            'tuesday': {'start': '08:00', 'end': '18:00'}
        }
        self.box = Box.objects.create(
            name='Бокс 1',
            name_en='Box 1',
            description='Опис',
            description_en='Description',
            is_active=True,
            working_hours=self.working_hours
        )

    def test_serialization_ukrainian(self):
        """Перевірка серіалізації українською"""
        serializer = BoxSerializer(
            self.box,
            context={'language': 'uk'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'Бокс 1')
        self.assertEqual(data['description'], 'Опис')
        self.assertIsInstance(data['working_hours'], dict)
        self.assertEqual(data['working_hours']['monday']['start'], '08:00')

    def test_serialization_english(self):
        """Перевірка серіалізації англійською"""
        serializer = BoxSerializer(
            self.box,
            context={'language': 'en'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'Box 1')
        self.assertEqual(data['description'], 'Description')

    def test_working_hours_json_parsing(self):
        """Перевірка парсингу JSON для working_hours"""
        # Створюємо бокс з JSON строкою
        import json
        working_hours_str = json.dumps(self.working_hours)
        box = Box.objects.create(
            name='Бокс 2',
            is_active=True
        )
        box.working_hours = working_hours_str
        box.save()

        serializer = BoxSerializer(box, context={'language': 'uk'})
        data = serializer.data

        self.assertIsInstance(data['working_hours'], dict)
        self.assertIn('monday', data['working_hours'])


class STOInfoSerializerTest(TestCase):
    """Тести для STOInfoSerializer"""

    def setUp(self):
        """Налаштування тестових даних"""
        self.sto_info = STOInfo.objects.create(
            name='СТО Test',
            name_en='STO Test',
            description='Опис',
            description_en='Description',
            motto='Девіз',
            motto_en='Motto',
            welcome_text='Ласкаво просимо',
            welcome_text_en='Welcome',
            what_you_can_title='У нас ви можете',
            what_you_can_title_en='What you can',
            what_you_can_items=['Пункт 1', 'Пункт 2'],
            what_you_can_items_en=['Item 1', 'Item 2'],
            address='Адреса',
            phone='+380501234567',
            email='info@sto.com',
            working_hours='Пн-Пт: 8:00-18:00'
        )

    def test_serialization_ukrainian(self):
        """Перевірка серіалізації українською"""
        serializer = STOInfoSerializer(
            self.sto_info,
            context={'language': 'uk'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'СТО Test')
        self.assertEqual(data['motto'], 'Девіз')
        self.assertEqual(data['what_you_can_title'], 'У нас ви можете')
        self.assertIsInstance(data['what_you_can_items'], list)
        self.assertEqual(len(data['what_you_can_items']), 2)

    def test_serialization_english(self):
        """Перевірка серіалізації англійською"""
        serializer = STOInfoSerializer(
            self.sto_info,
            context={'language': 'en'}
        )
        data = serializer.data

        self.assertEqual(data['name'], 'STO Test')
        self.assertEqual(data['motto'], 'Motto')
        self.assertEqual(data['what_you_can_title'], 'What you can')
        self.assertEqual(data['what_you_can_items'], ['Item 1', 'Item 2'])

