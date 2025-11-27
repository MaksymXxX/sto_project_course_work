#!/usr/bin/env python
"""
Скрипт для завантаження базових даних СТО проекту.
Запускається командою: python manage.py load_initial_data
"""

import os
import sys
import django
from datetime import time
from django.utils import timezone

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import (
    ServiceCategory, Service, Box, STOInfo, Customer
)


def create_superuser():
    """Створення суперкористувача"""
    if not User.objects.filter(username='admin@sto.com').exists():
        User.objects.create_superuser(
            username='admin@sto.com',
            email='admin@sto.com',
            password='admin123',
            first_name='Адміністратор',
            last_name='Системи'
        )
        print("✅ Суперкористувач створено: admin@sto.com / admin123")
    else:
        print("ℹ️ Суперкористувач вже існує")


def create_service_categories():
    """Створення категорій послуг"""
    categories_data = [
        {
            'name': 'Технічне обслуговування',
            'name_en': 'Technical Maintenance',
            'description': 'Регулярне технічне обслуговування автомобіля',
            'description_en': 'Regular technical maintenance of the vehicle',
            'order': 1
        },
        {
            'name': 'Діагностика',
            'name_en': 'Diagnostics',
            'description': 'Комп\'ютерна та механічна діагностика',
            'description_en': 'Computer and mechanical diagnostics',
            'order': 2
        },
        {
            'name': 'Ремонт ходової частини',
            'name_en': 'Chassis Repair',
            'description': 'Ремонт підвіски, гальм та керування',
            'description_en': 'Repair of suspension, brakes and steering',
            'order': 3
        },
        {
            'name': 'Заміна мастил',
            'name_en': 'Oil Change',
            'description': 'Заміна моторного масла та фільтрів',
            'description_en': 'Engine oil and filter replacement',
            'order': 4
        },
        {
            'name': 'Шиномонтаж',
            'name_en': 'Tire Service',
            'description': 'Заміна та балансування шин',
            'description_en': 'Tire replacement and balancing',
            'order': 5
        },
        {
            'name': 'Електрика',
            'name_en': 'Electrical',
            'description': 'Ремонт електросистем автомобіля',
            'description_en': 'Repair of vehicle electrical systems',
            'order': 6
        }
    ]
    
    for cat_data in categories_data:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Категорія створена: {category.name}")
        else:
            print(f"ℹ️ Категорія вже існує: {category.name}")


def create_services():
    """Створення послуг"""
    services_data = [
        {
            'name': 'Повне ТО',
            'name_en': 'Full Technical Maintenance',
            'description': 'Комплексне технічне обслуговування автомобіля',
            'description_en': 'Comprehensive technical maintenance of the vehicle',
            'price': 1500.00,
            'duration_minutes': 120,
            'category_name': 'Технічне обслуговування',
            'is_featured': True
        },
        {
            'name': 'Заміна масла',
            'name_en': 'Oil Change',
            'description': 'Заміна моторного масла та масляного фільтра',
            'description_en': 'Engine oil and oil filter replacement',
            'price': 800.00,
            'duration_minutes': 60,
            'category_name': 'Заміна мастил',
            'is_featured': True
        },
        {
            'name': 'Комп\'ютерна діагностика',
            'name_en': 'Computer Diagnostics',
            'description': 'Діагностика електронних систем автомобіля',
            'description_en': 'Diagnostics of vehicle electronic systems',
            'price': 500.00,
            'duration_minutes': 45,
            'category_name': 'Діагностика',
            'is_featured': True
        },
        {
            'name': 'Заміна гальмівних колодок',
            'name_en': 'Brake Pad Replacement',
            'description': 'Заміна гальмівних колодок спереду або ззаду',
            'description_en': 'Front or rear brake pad replacement',
            'price': 1200.00,
            'duration_minutes': 90,
            'category_name': 'Ремонт ходової частини',
            'is_featured': False
        },
        {
            'name': 'Заміна амортизаторів',
            'name_en': 'Shock Absorber Replacement',
            'description': 'Заміна амортизаторів підвіски',
            'description_en': 'Suspension shock absorber replacement',
            'price': 2000.00,
            'duration_minutes': 120,
            'category_name': 'Ремонт ходової частини',
            'is_featured': False
        },
        {
            'name': 'Шиномонтаж (4 колеса)',
            'name_en': 'Tire Service (4 wheels)',
            'description': 'Заміна та балансування 4 шин',
            'description_en': 'Replacement and balancing of 4 tires',
            'price': 600.00,
            'duration_minutes': 60,
            'category_name': 'Шиномонтаж',
            'is_featured': True
        },
        {
            'name': 'Заміна свічок запалювання',
            'name_en': 'Spark Plug Replacement',
            'description': 'Заміна свічок запалювання',
            'description_en': 'Spark plug replacement',
            'price': 400.00,
            'duration_minutes': 30,
            'category_name': 'Електрика',
            'is_featured': False
        },
        {
            'name': 'Заміна повітряного фільтра',
            'name_en': 'Air Filter Replacement',
            'description': 'Заміна повітряного фільтра двигуна',
            'description_en': 'Engine air filter replacement',
            'price': 200.00,
            'duration_minutes': 20,
            'category_name': 'Заміна мастил',
            'is_featured': False
        }
    ]
    
    for service_data in services_data:
        category_name = service_data.pop('category_name')
        try:
            category = ServiceCategory.objects.get(name=category_name)
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    **service_data,
                    'category': category
                }
            )
            if created:
                print(f"✅ Послуга створена: {service.name} - {service.price} грн")
            else:
                print(f"ℹ️ Послуга вже існує: {service.name}")
        except ServiceCategory.DoesNotExist:
            print(f"❌ Категорія не знайдена: {category_name}")


def create_boxes():
    """Створення боксів"""
    boxes_data = [
        {
            'name': 'Бокс 1',
            'name_en': 'Box 1',
            'description': 'Основний бокс для ТО та ремонту',
            'description_en': 'Main box for maintenance and repair',
            'working_hours': {
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'},
                'wednesday': {'start': '08:00', 'end': '18:00'},
                'thursday': {'start': '08:00', 'end': '18:00'},
                'friday': {'start': '08:00', 'end': '18:00'},
                'saturday': {'start': '09:00', 'end': '16:00'},
                'sunday': {'start': '09:00', 'end': '16:00'}
            }
        },
        {
            'name': 'Бокс 2',
            'name_en': 'Box 2',
            'description': 'Бокс для діагностики та електрики',
            'description_en': 'Box for diagnostics and electrical work',
            'working_hours': {
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'},
                'wednesday': {'start': '08:00', 'end': '18:00'},
                'thursday': {'start': '08:00', 'end': '18:00'},
                'friday': {'start': '08:00', 'end': '18:00'},
                'saturday': {'start': '09:00', 'end': '16:00'},
                'sunday': {'start': '09:00', 'end': '16:00'}
            }
        },
        {
            'name': 'Шиномонтаж',
            'name_en': 'Tire Service',
            'description': 'Спеціалізований бокс для шиномонтажу',
            'description_en': 'Specialized box for tire service',
            'working_hours': {
                'monday': {'start': '08:00', 'end': '18:00'},
                'tuesday': {'start': '08:00', 'end': '18:00'},
                'wednesday': {'start': '08:00', 'end': '18:00'},
                'thursday': {'start': '08:00', 'end': '18:00'},
                'friday': {'start': '08:00', 'end': '18:00'},
                'saturday': {'start': '09:00', 'end': '16:00'},
                'sunday': {'start': '09:00', 'end': '16:00'}
            }
        }
    ]
    
    for box_data in boxes_data:
        box, created = Box.objects.get_or_create(
            name=box_data['name'],
            defaults=box_data
        )
        if created:
            print(f"✅ Бокс створено: {box.name}")
        else:
            print(f"ℹ️ Бокс вже існує: {box.name}")


def create_sto_info():
    """Створення інформації про СТО"""
    sto_info_data = {
        'name': 'СТО "AutoServis"',
        'name_en': 'Auto Service "AutoServis"',
        'description': 'Професійне обслуговування та ремонт автомобілів усіх марок. Понад 10 років досвіду в галузі автомобільного сервісу.',
        'description_en': 'Professional maintenance and repair of all car brands. Over 10 years of experience in the automotive service industry.',
        'motto': 'Надійність. Якість. Доступність.',
        'motto_en': 'Reliability. Quality. Accessibility.',
        'welcome_text': 'Вітаємо на нашому офіційному сайті! Ми спеціалізуємося на комплексному обслуговуванні автомобілів усіх марок. Понад 10 років досвіду дозволяють нам гарантувати високу якість робіт і індивідуальний підхід до кожного клієнта.',
        'welcome_text_en': 'Welcome to our official website! We specialize in comprehensive maintenance of all car brands. Over 10 years of experience allows us to guarantee high quality work and individual approach to each client.',
        'what_you_can_title': 'У нас ви можете:',
        'what_you_can_title_en': 'What you can do with us:',
        'what_you_can_items': [
            'Отримати професійну діагностику автомобіля',
            'Замовити технічне обслуговування',
            'Відремонтувати ходову частину',
            'Замінити масло та фільтри',
            'Відремонтувати електросистему',
            'Замінити шини та зробити балансування'
        ],
        'what_you_can_items_en': [
            'Get professional car diagnostics',
            'Order technical maintenance',
            'Repair the chassis',
            'Change oil and filters',
            'Repair the electrical system',
            'Replace tires and do balancing'
        ],
        'address': 'м. Київ, вул. Автосервісна, 123',
        'address_en': 'Kyiv, Autoservice St., 123',
        'phone': '+380441234567',
        'phone_en': '+380441234567',
        'email': 'info@autoservis.ua',
        'email_en': 'info@autoservis.ua',
        'working_hours': 'Пн-Пт: 8:00-18:00, Сб-Нд: 9:00-16:00',
        'working_hours_en': 'Mon-Fri: 8:00-18:00, Sat-Sun: 9:00-16:00'
    }
    
    sto_info, created = STOInfo.objects.get_or_create(
        id=1,
        defaults=sto_info_data
    )
    if created:
        print("✅ Інформація про СТО створена")
    else:
        print("ℹ️ Інформація про СТО вже існує")


def create_test_customer():
    """Створення тестового клієнта"""
    if not User.objects.filter(username='test@example.com').exists():
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='test123',
            first_name='Тестовий',
            last_name='Користувач'
        )
        Customer.objects.create(user=user)
        print("✅ Тестовий клієнт створено: test@example.com / test123")
    else:
        print("ℹ️ Тестовий клієнт вже існує")


def main():
    """Головна функція завантаження даних"""
    print("🚀 Початок завантаження базових даних...")
    
    try:
        # Створення суперкористувача
        create_superuser()
        
        # Створення категорій послуг
        create_service_categories()
        
        # Створення послуг
        create_services()
        
        # Створення боксів
        create_boxes()
        
        # Створення інформації про СТО
        create_sto_info()
        
        # Створення тестового клієнта
        create_test_customer()
        
        print("\n✅ Завантаження базових даних завершено успішно!")
        print("\n📋 Доступні облікові записи:")
        print("   Адміністратор: admin@sto.com / admin123")
        print("   Тестовий клієнт: test@example.com / test123")
        print("\n🌐 Запустіть сервер: python manage.py runserver")
        print("📱 Запустіть фронтенд: cd frontend && npm start")
        
    except Exception as e:
        print(f"❌ Помилка при завантаженні даних: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
