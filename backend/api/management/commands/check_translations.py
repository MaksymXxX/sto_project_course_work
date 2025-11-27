from django.core.management.base import BaseCommand
from backend.api.models import Box, Service

class Command(BaseCommand):
    help = 'Перевіряє переклади боксів та послуг'

    def handle(self, *args, **options):
        self.stdout.write("=== ПЕРЕВІРКА ДАНИХ БОКСІВ ===")
        boxes = Box.objects.all()
        for box in boxes:
            self.stdout.write(f"ID: {box.id}")
            self.stdout.write(f"  Назва (uk): {box.name}")
            self.stdout.write(f"  Назва (en): {box.name_en}")
            self.stdout.write(f"  get_name('uk'): {box.get_name('uk')}")
            self.stdout.write(f"  get_name('en'): {box.get_name('en')}")
            self.stdout.write()

        self.stdout.write("=== ПЕРЕВІРКА ДАНИХ ПОСЛУГ ===")
        services = Service.objects.all()
        for service in services:
            self.stdout.write(f"ID: {service.id}")
            self.stdout.write(f"  Назва (uk): {service.name}")
            self.stdout.write(f"  Назва (en): {service.name_en}")
            self.stdout.write(f"  get_name('uk'): {service.get_name('uk')}")
            self.stdout.write(f"  get_name('en'): {service.get_name('en')}")
            self.stdout.write()
