from django.core.management.base import BaseCommand
from backend.api.models import ServiceCategory, Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Завантажує тестові дані для категорій та послуг'

    def handle(self, *args, **options):
        self.stdout.write('Початок завантаження тестових даних...')

        # Створюємо категорії
        categories_data = [
            {
                'name': 'Технічне обслуговування',
                'description': 'Комплексне технічне обслуговування автомобіля',
                'order': 1
            },
            {
                'name': 'Діагностика та ремонт',
                'description': 'Діагностика та ремонт різних систем автомобіля',
                'order': 2
            },
            {
                'name': 'Шиномонтаж',
                'description': 'Послуги з шиномонтажу та балансування',
                'order': 3
            },
            {
                'name': 'Електрика',
                'description': 'Роботи з електрообладнанням автомобіля',
                'order': 4
            },
            {
                'name': 'Додаткові послуги',
                'description': 'Додаткові послуги по обслуговуванню',
                'order': 5
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Створено категорію: {category.name}')

        # Створюємо послуги
        services_data = [
            # Технічне обслуговування
            {
                'category': 'Технічне обслуговування',
                'name': 'Заміна мастила в двигуні',
                'description': 'Заміна моторного мастила з фільтром',
                'price': Decimal('600.00'),
                'duration': 30
            },
            {
                'category': 'Технічне обслуговування',
                'name': 'Заміна повітряного фільтра',
                'description': 'Заміна повітряного фільтра двигуна',
                'price': Decimal('250.00'),
                'duration': 15
            },
            {
                'category': 'Технічне обслуговування',
                'name': 'Заміна паливного фільтра',
                'description': 'Заміна паливного фільтра',
                'price': Decimal('300.00'),
                'duration': 20
            },
            {
                'category': 'Технічне обслуговування',
                'name': 'Заміна салонного фільтра',
                'description': 'Заміна фільтра салону',
                'price': Decimal('200.00'),
                'duration': 15
            },
            {
                'category': 'Технічне обслуговування',
                'name': 'Комплексне ТО (із заміною фільтрів і мастила)',
                'description': 'Повне технічне обслуговування',
                'price': Decimal('1500.00'),
                'duration': 120
            },
            # Діагностика та ремонт
            {
                'category': 'Діагностика та ремонт',
                'name': 'Комп\'ютерна діагностика',
                'description': 'Діагностика електронних систем',
                'price': Decimal('400.00'),
                'duration': 45
            },
            {
                'category': 'Діагностика та ремонт',
                'name': 'Діагностика ходової частини',
                'description': 'Перевірка стану ходової частини',
                'price': Decimal('300.00'),
                'duration': 30
            },
            {
                'category': 'Діагностика та ремонт',
                'name': 'Ремонт гальмівної системи',
                'description': 'Ремонт та обслуговування гальм',
                'price': Decimal('800.00'),
                'duration': 60
            },
            {
                'category': 'Діагностика та ремонт',
                'name': 'Заміна гальмівних колодок',
                'description': 'Заміна передніх або задніх колодок',
                'price': Decimal('500.00'),
                'duration': 45
            },
            {
                'category': 'Діагностика та ремонт',
                'name': 'Заміна амортизаторів',
                'description': 'Заміна амортизаторів підвіски',
                'price': Decimal('700.00'),
                'duration': 90
            },
            # Шиномонтаж
            {
                'category': 'Шиномонтаж',
                'name': 'Зняття/установка колеса',
                'description': 'Зняття та встановлення колеса',
                'price': Decimal('100.00'),
                'duration': 15
            },
            {
                'category': 'Шиномонтаж',
                'name': 'Балансування коліс',
                'description': 'Балансування колеса на стенді',
                'price': Decimal('150.00'),
                'duration': 20
            },
            {
                'category': 'Шиномонтаж',
                'name': 'Комплексний шиномонтаж (4 колеса)',
                'description': 'Повний шиномонтаж всіх коліс',
                'price': Decimal('800.00'),
                'duration': 90
            },
            {
                'category': 'Шиномонтаж',
                'name': 'Ремонт проколу',
                'description': 'Ремонт проколотого колеса',
                'price': Decimal('150.00'),
                'duration': 30
            },
            # Електрика
            {
                'category': 'Електрика',
                'name': 'Заміна акумулятора',
                'description': 'Заміна автомобільного акумулятора',
                'price': Decimal('300.00'),
                'duration': 30
            },
            {
                'category': 'Електрика',
                'name': 'Діагностика електрообладнання',
                'description': 'Перевірка електросистеми автомобіля',
                'price': Decimal('400.00'),
                'duration': 45
            },
            {
                'category': 'Електрика',
                'name': 'Установка сигналізації',
                'description': 'Встановлення автосигналізації',
                'price': Decimal('2000.00'),
                'duration': 180
            },
            # Додаткові послуги
            {
                'category': 'Додаткові послуги',
                'name': 'Автомийка (зовнішня + внутрішня)',
                'description': 'Повна мийка автомобіля',
                'price': Decimal('350.00'),
                'duration': 60
            },
            {
                'category': 'Додаткові послуги',
                'name': 'Хімчистка салону',
                'description': 'Професійна хімчистка салону',
                'price': Decimal('1200.00'),
                'duration': 240
            },
            {
                'category': 'Додаткові послуги',
                'name': 'Полірування фар',
                'description': 'Полірування фар автомобіля',
                'price': Decimal('500.00'),
                'duration': 90
            },
            {
                'category': 'Додаткові послуги',
                'name': 'Установка відеореєстратора',
                'description': 'Встановлення відеореєстратора',
                'price': Decimal('600.00'),
                'duration': 120
            }
        ]

        for service_data in services_data:
            category = categories[service_data['category']]
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                category=category,
                defaults={
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'duration': service_data['duration']
                }
            )
            if created:
                self.stdout.write(f'Створено послугу: {service.name}')

        self.stdout.write(
            self.style.SUCCESS('Тестові дані успішно завантажено!')
        ) 