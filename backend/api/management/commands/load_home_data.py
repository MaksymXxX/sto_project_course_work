from django.core.management.base import BaseCommand
from backend.api.models import STOInfo
from decimal import Decimal


class Command(BaseCommand):
    help = 'Завантажує тестові дані для головної сторінки'

    def handle(self, *args, **options):
        self.stdout.write('Початок завантаження даних для головної сторінки...')

        # Створюємо або оновлюємо інформацію про СТО
        sto_info, created = STOInfo.objects.get_or_create(
            is_active=True,
            defaults={
                'name': 'Станція технічного обслуговування "AutoServis"',
                'description': 'Комплексне обслуговування автомобілів усіх марок. Понад 10 років досвіду дозволяють нам гарантувати високу якість робіт і індивідуальний підхід до кожного клієнта.',
                'motto': 'Надійність. Якість. Доступність.',
                'welcome_text': 'Вітаємо на нашому офіційному сайті! Ми спеціалізуємося на комплексному обслуговуванні автомобілів усіх марок. Понад 10 років досвіду дозволяють нам гарантувати високу якість робіт і індивідуальний підхід до кожного клієнта.',
                'address': 'м. Київ, вул. Автосервісна, 123',
                'phone': '+380441234567',
                'email': 'info@autoservis.ua',
                'working_hours': 'Пн-Пт: 8:00-20:00, Сб: 9:00-18:00, Нд: 10:00-16:00'
            }
        )

        if created:
            self.stdout.write(f'Створено інформацію про СТО: {sto_info.name}')
        else:
            self.stdout.write(f'Оновлено інформацію про СТО: {sto_info.name}')

        self.stdout.write(
            self.style.SUCCESS('Дані для головної сторінки успішно завантажено!')
        ) 