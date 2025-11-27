import os
import django
import sys

# Додаємо шлях до backend
sys.path.append('backend')

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from api.models import Service, ServiceCategory, STOInfo, Box

print("=== Перевірка даних в базі ===")

# Перевіряємо категорії
categories = ServiceCategory.objects.all()
print(f"Категорії: {categories.count()}")
for cat in categories:
    print(f"  - {cat.name}")

# Перевіряємо послуги
services = Service.objects.all()
print(f"Послуги: {services.count()}")
for service in services:
    print(f"  - {service.name} (категорія: {service.category.name if service.category else 'Немає'})")

# Перевіряємо інформацію про СТО
sto_info = STOInfo.objects.all()
print(f"Інформація про СТО: {sto_info.count()}")
for info in sto_info:
    print(f"  - {info.name}")

# Перевіряємо бокси
boxes = Box.objects.all()
print(f"Бокси: {boxes.count()}")
for box in boxes:
    print(f"  - {box.name}")

print("=== Кінець перевірки ===") 